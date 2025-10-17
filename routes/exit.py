from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, aadharinfo, entrylogs
from datetime import datetime

exit_bp = Blueprint("exit", __name__)

@exit_bp.route("/exitpoint", methods=['GET','POST'], endpoint="exit")
def exit():
    if "entry_point" not in session:
        return redirect(url_for("entrypoint.select_entrypoint"))

    exit_place = session.get("entry_point", "Ramkund")

    if request.method == 'POST':
        aadhar_num = request.form['aadhar_number']
        person = aadharinfo.query.filter_by(aadhar_number=aadhar_num).first()

        if not person:
            flash("Aadhar number not found in database", "danger")
            return redirect(url_for('exit.exit'))


        last_log = entrylogs.query.filter_by(aadhar_number=aadhar_num).order_by(entrylogs.entry_time.desc()).first()

        if not last_log or last_log.status != "Enterd":
            flash(f"{person.name} has no active entry to exit!", "warning")
            return redirect(url_for('exit.exit'))

        # Log exit
        new_exit_log = entrylogs(
            aadhar_number=aadhar_num,
            entry_place=exit_place,
            current_place=exit_place,
            visited_places=last_log.visited_places,
            status="Exited",
            entry_time=datetime.now()
        )
        db.session.add(new_exit_log)
        db.session.commit()

        flash(f"{person.name} ✅ Exited from {exit_place}", "success")
        return redirect(url_for('exit.exit'))

    return render_template("exitpoint.html")
