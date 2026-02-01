from flask import Blueprint, render_template, redirect, url_for, flash
from models import aadharinfo, entrylogs

profile_bp = Blueprint("profile", __name__)


PLACE_COORDS = {
    "Ramkund": [20.00828, 73.79191],
    "Sita Gufa": [20.00726, 73.79604],
    "Panchavati": [20.00711, 73.79251],
    "Kapaleshwar": [19.93243, 73.53053],
    "Godavari Ghat": [20.00028, 73.81462]
}


@profile_bp.route("/profile/<int:aadhar_number>", methods=["GET"], endpoint="profile")
def profile(aadhar_number):

    person = aadharinfo.query.filter_by(aadhar_number=aadhar_number).first()
    if not person:
        flash("User not found!", "danger")
        return redirect(url_for("search.search"))

    logs = (
        entrylogs.query
        .filter_by(aadhar_number=aadhar_number)
        .order_by(entrylogs.entry_time.asc())
        .all()
    )

    visited_points = []

    for log in logs:
        if log.status and log.status.lower() == "enterd":
            place_clean = (log.entry_place or "").lower()

            if "ramkund" in place_clean:
                key = "Ramkund"
            elif "godavari" in place_clean:
                key = "Godavari Ghat"
            elif "kapaleshwar" in place_clean:
                key = "Kapaleshwar"
            elif "sita gufa" in place_clean:
                key = "Sita Gufa"
            elif "panchavati" in place_clean:
                key = "Panchavati"
            else:
                continue

            lat, lng = PLACE_COORDS[key]

            visited_points.append({
                "name": key,
                "lat": lat,
                "lng": lng,
                "time": log.entry_time.strftime("%d-%m-%Y %H:%M")
            })

    return render_template(
        "profile.html",
        person=person,
        logs=logs,
        visited_points=visited_points
    )
