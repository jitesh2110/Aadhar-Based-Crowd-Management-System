from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from models import db, aadharinfo, entrylogs
import cv2
import numpy as np
import pickle
from datetime import datetime

fingerprint_bp = Blueprint("fingerprint", __name__)


def extract_descriptors(image):

    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return descriptors

def match_descriptors(des1, des2):

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    good = [m for m in matches if m.distance < 50]
    return len(good)

@fingerprint_bp.route("/register_fingerprint/<aadhar_number>", methods=["GET", "POST"])
def register_fingerprint(aadhar_number):
    user = aadharinfo.query.filter_by(aadhar_number=aadhar_number).first()
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("search.search"))

    if request.method == "POST":
        if 'fingerprint_image' not in request.files:
            flash("Please upload an image!", "danger")
            return redirect(request.url)

        file = request.files['fingerprint_image']
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        descriptors = extract_descriptors(image)

        if descriptors is None:
            flash("Failed to extract features. Try a clearer fingerprint image.", "danger")
            return redirect(request.url)

        user.fingerprint_data = pickle.dumps(descriptors)
        db.session.commit()
        flash(f"Fingerprint registered for {user.name}", "success")
        return redirect(url_for("search.search"))

    return render_template("register_fingerprint.html", user=user)


def scan_fingerprint(is_entry=True):
    if 'fingerprint_image' not in request.files:
        flash("Please upload a fingerprint image!", "danger")
        return redirect(url_for("entry.entry") if is_entry else url_for("exit.exit"))

    file = request.files['fingerprint_image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    probe_des = extract_descriptors(image)
    if probe_des is None:
        flash("Failed to extract features. Try again.", "danger")
        return redirect(url_for("entry.entry") if is_entry else url_for("exit.exit"))

    users = aadharinfo.query.all()
    matched_user = None
    highest_matches = 0
    for user in users:
        if not user.fingerprint_data:
            continue
        db_des = pickle.loads(user.fingerprint_data)
        matches = match_descriptors(probe_des, db_des)
        if matches > highest_matches and matches > 10:
            highest_matches = matches
            matched_user = user

    if not matched_user:
        flash("Fingerprint not recognized!", "danger")
        return redirect(url_for("entry.entry") if is_entry else url_for("exit.exit"))

    place = session.get("entry_point", "Ramkund")


    last_log = entrylogs.query.filter_by(aadhar_number=matched_user.aadhar_number)\
        .order_by(entrylogs.entry_time.desc()).first()

    if is_entry:

        if last_log and last_log.status == "Enterd":
            exit_log = entrylogs(
                aadhar_number=matched_user.aadhar_number,
                entry_place=place,
                current_place=place,
                visited_places=place,
                status="Exited",
                entry_time=datetime.now()
            )
            db.session.add(exit_log)
            db.session.commit()
            flash(f"{matched_user.name} was still inside. Logged automatic exit first.", "info")


        new_log = entrylogs(
            aadhar_number=matched_user.aadhar_number,
            entry_place=place,
            current_place=place,
            visited_places=place,
            status="Enterd",
            entry_time=datetime.now()
        )
        db.session.add(new_log)
        db.session.commit()
        flash(f"Fingerprint recognized for entry: {matched_user.name}", "success")

    else:

        if not last_log or last_log.status == "Exited":
            flash(f"{matched_user.name} has no active entry. Cannot exit.", "warning")
            return redirect(url_for("exit.exit"))


        exit_log = entrylogs(
            aadhar_number=matched_user.aadhar_number,
            entry_place=place,
            current_place=place,
            visited_places=place,
            status="Exited",
            entry_time=datetime.now()
        )
        db.session.add(exit_log)
        db.session.commit()
        flash(f"Fingerprint recognized for exit: {matched_user.name}", "success")

    return redirect(url_for("entry.entry") if is_entry else url_for("exit.exit"))



@fingerprint_bp.route("/scan_fingerprint_entry", methods=["POST"])
def scan_entry():
    return scan_fingerprint(is_entry=True)

@fingerprint_bp.route("/scan_fingerprint_exit", methods=["POST"])
def scan_exit():
    return scan_fingerprint(is_entry=False)

