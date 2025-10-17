from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, aadharinfo, entrylogs
import pandas as pd

search_bp = Blueprint("search", __name__)

@search_bp.route("/search",methods=['GET','POST'],endpoint="search")
def search():
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_value = request.form['search_value']

        if search_type == "aadhaar":
            person = aadharinfo.query.filter_by(aadhar_number=search_value).first()
        if person is None:
            flash("No person found with this Aadhaar number.", "warning")
            return redirect(url_for('search.search'))

        logs = entrylogs.query.filter_by(aadhar_number=person.aadhar_number).order_by(entrylogs.entry_time.desc()).all()


        return render_template("profile.html",person = person,logs=logs)


    return render_template("search.html")