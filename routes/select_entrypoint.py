from flask import Blueprint, render_template, request, redirect, url_for, session, flash

entrypoint_bp = Blueprint("entrypoint", __name__)

places = ["Ramkund", "Sita Gufa", "Panchavati", "Kapaleshwar", "Godavari Ghat"]

@entrypoint_bp.route("/select_entrypoint", methods=["GET", "POST"])
def select_entrypoint():
    if request.method == "POST":
        selected_place = request.form.get("place")
        session["entry_point"] = selected_place
        flash(f"Entry point set to {selected_place}", "success")
        return redirect(url_for("entry.entry"))
    return render_template("select_entrypoint.html", places=places)
