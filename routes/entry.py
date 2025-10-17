from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, aadharinfo, entrylogs
from datetime import datetime

entry_bp = Blueprint("entry", __name__)

@entry_bp.route("/", methods=['GET', 'POST'], endpoint="entry")
def entry():
    if "entry_point" not in session:
        return redirect(url_for("entrypoint.select_entrypoint"))

    entry_place = session.get("entry_point", "Ramkund")

    if request.method == 'POST':
        aadhar_num = request.form['aadhar_number']
        person = aadharinfo.query.filter_by(aadhar_number=aadhar_num).first()

        if not person:
            flash("Aadhar number not found in database", "danger")
            return redirect(url_for('entry.entry'))

        # Check last log
        last_log = entrylogs.query.filter_by(aadhar_number=aadhar_num).order_by(entrylogs.entry_time.desc()).first()

        if last_log and last_log.status == "Enterd":
            # Automatically log exit first
            last_log_exit = entrylogs(
                aadhar_number=aadhar_num,
                entry_place=last_log.entry_place,
                current_place=entry_place,
                visited_places=last_log.visited_places,
                status="Exited",
                entry_time=datetime.now()
            )
            db.session.add(last_log_exit)
            db.session.commit()
            flash(f"{person.name} was automatically exited from previous entry.", "info")

        new_log = entrylogs(
            aadhar_number=aadhar_num,
            entry_place=entry_place,
            current_place=entry_place,
            visited_places=entry_place,
            status="Enterd",
            entry_time=datetime.now()
        )
        db.session.add(new_log)
        db.session.commit()
        flash(f"Aadhar Found: {person.name} ✅ Entered at {entry_place}", "success")
        return redirect(url_for('entry.entry'))

    return render_template("entrypoint.html")
