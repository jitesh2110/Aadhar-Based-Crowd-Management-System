from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import aadharinfo

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET", "POST"], endpoint="search")
def search():
    if request.method == "POST":
        search_type = request.form["search_type"]
        search_value = request.form["search_value"]

        person = None

        if search_type == "aadhaar":
            person = aadharinfo.query.filter_by(
                aadhar_number=search_value
            ).first()

        if not person:
            flash("No person found with this Aadhaar number.", "warning")
            return redirect(url_for("search.search"))

        # 🔥 IMPORTANT: redirect, don’t render
        return redirect(
            url_for("profile.profile", aadhar_number=person.aadhar_number)
        )

    return render_template("search.html")
