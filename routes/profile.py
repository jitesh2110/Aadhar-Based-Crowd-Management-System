from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, aadharinfo, entrylogs

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile/<int:aadhar_number>", methods=['GET', 'POST'], endpoint="profile")
def profile(aadhar_number):
    person = aadharinfo.query.filter_by(aadhar_number=aadhar_number).first()
    if not person:
        flash("User not found!", "danger")
        return redirect(url_for("search.search"))

    logs = entrylogs.query.filter_by(aadhar_number=aadhar_number).order_by(entrylogs.entry_time.desc()).all()

    return render_template("profile.html", person=person, logs=logs)
