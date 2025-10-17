from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, aadharinfo, entrylogs
import cv2
import numpy as np
import pickle
import insightface
from insightface.app import FaceAnalysis
from datetime import datetime
import base64
from io import BytesIO
import re

face_bp = Blueprint("face", __name__)

face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640, 640))

def match_face(input_embedding, threshold=0.45):
    users = aadharinfo.query.filter(aadharinfo.face_embedding != None).all()
    if not users:
        return None, None

    known_embeddings = []
    labels = []
    aadhaars = []

    for u in users:
        emb = pickle.loads(u.face_embedding)
        known_embeddings.append(emb)
        labels.append(u.name)
        aadhaars.append(u.aadhar_number)

    known_embeddings = np.array(known_embeddings)
    known_embeddings = known_embeddings / np.linalg.norm(known_embeddings, axis=1, keepdims=True)
    input_embedding = input_embedding / np.linalg.norm(input_embedding)

    sims = np.dot(known_embeddings, input_embedding)
    best_idx = np.argmax(sims)
    best_score = sims[best_idx]

    if best_score < threshold:
        return None, None
    return aadhaars[best_idx], labels[best_idx]


@face_bp.route("/register_face_webcam/<aadhar_number>", methods=["GET", "POST"])
def register_face_webcam(aadhar_number):
    user = aadharinfo.query.filter_by(aadhar_number=aadhar_number).first()
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("search.search"))

    if request.method == "POST":
        data_url = request.form.get("face_image")
        if not data_url:
            flash("No image captured!", "warning")
            return redirect(request.url)

        img_str = re.sub('^data:image/.+;base64,', '', data_url)
        img_bytes = BytesIO(base64.b64decode(img_str))
        img = cv2.imdecode(np.frombuffer(img_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        faces = face_app.get(img)
        if len(faces) == 0:
            flash("No face detected!", "danger")
            return redirect(request.url)

        embedding = faces[0].normed_embedding
        user.face_embedding = pickle.dumps(embedding)
        db.session.commit()
        flash("Face registered successfully!", "success")
        return redirect(url_for("profile.profile", aadhar_number=user.aadhar_number))

    return render_template("register_face_webcam.html", user=user)


@face_bp.route("/face_entry", methods=["GET", "POST"])
def face_entry():
    if request.method == "POST":
        data_url = request.form.get("face_image")
        if not data_url:
            flash("Please capture an image!", "warning")
            return redirect(request.url)

        img_str = re.sub('^data:image/.+;base64,', '', data_url)
        img_bytes = BytesIO(base64.b64decode(img_str))
        img = cv2.imdecode(np.frombuffer(img_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        faces = face_app.get(img)
        if len(faces) == 0:
            flash("No face detected!", "danger")
            return redirect(request.url)

        embedding = faces[0].normed_embedding
        aadhar_number, name = match_face(embedding)

        if not aadhar_number:
            flash("Face not recognized!", "danger")
            return redirect(request.url)

        place = session.get("entry_point")


        last_log = entrylogs.query.filter_by(aadhar_number=aadhar_number)\
            .order_by(entrylogs.entry_time.desc()).first()


        if last_log and last_log.status == "Enterd":
            auto_exit = entrylogs(
                aadhar_number=aadhar_number,
                entry_place=place,
                status="Exited",
                entry_time=datetime.now()
            )
            db.session.add(auto_exit)
            db.session.commit()
            flash(f"{name} was still inside. Logged automatic exit first.", "info")

        new_entry = entrylogs(
            aadhar_number=aadhar_number,
            entry_place=place,
            status="Enterd",
            entry_time=datetime.now()
        )
        db.session.add(new_entry)
        db.session.commit()
        flash(f"✅ Entry logged for {name}", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("face_entry.html")


@face_bp.route("/face_exit", methods=["GET", "POST"])
def face_exit():
    if request.method == "POST":
        data_url = request.form.get("face_image")
        if not data_url:
            flash("Please capture an image!", "warning")
            return redirect(request.url)

        img_str = re.sub('^data:image/.+;base64,', '', data_url)
        img_bytes = BytesIO(base64.b64decode(img_str))
        img = cv2.imdecode(np.frombuffer(img_bytes.read(), np.uint8), cv2.IMREAD_COLOR)

        faces = face_app.get(img)
        if len(faces) == 0:
            flash("No face detected!", "danger")
            return redirect(request.url)

        embedding = faces[0].normed_embedding
        aadhar_number, name = match_face(embedding)

        if not aadhar_number:
            flash("Face not recognized!", "danger")
            return redirect(request.url)

        place = session.get("entry_point", "Ramkund")


        last_log = entrylogs.query.filter_by(aadhar_number=aadhar_number)\
            .order_by(entrylogs.entry_time.desc()).first()

        if not last_log or last_log.status == "Exited":
            flash(f"{name} has no active entry. Cannot exit.", "warning")
            return redirect(request.url)


        new_exit = entrylogs(
            aadhar_number=aadhar_number,
            entry_place=place,
            status="Exited",
            entry_time=datetime.now()
        )
        db.session.add(new_exit)
        db.session.commit()
        flash(f"✅ Exit logged for {name}", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("face_exit.html")
