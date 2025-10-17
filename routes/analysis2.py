from flask import Blueprint, render_template
from models import db, aadharinfo, entrylogs
import pandas as pd
from datetime import date

analysis2_bp = Blueprint("analysis2", __name__)

@analysis2_bp.route("/analysis2", methods=['GET'], endpoint="analysis2")
def analysis2():
    logs = entrylogs.query.all()

    if not logs:
        return render_template("analysis2.html",
                               gender_data={},
                               age_data={},
                               district_data={})

    data = []
    for log in logs:
        person = log.card
        age = (date.today() - person.dob.date()).days // 365 if person.dob else None
        district = person.address.split(",")[-1].strip().split()[0] if person.address else "Unknown"

        data.append({
            "gender": person.gender,
            "age": age,
            "district": district
        })

    df = pd.DataFrame(data)

    gender_data = df['gender'].value_counts().to_dict()

    bins = [0, 18, 30, 45, 60, 100]
    labels = ["0-17", "18-29", "30-44", "45-59", "60+"]
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    age_data = df['age_group'].value_counts().sort_index().to_dict()


    district_data = df['district'].value_counts().to_dict()

    return render_template("analysis2.html",
                           gender_data=gender_data,
                           age_data=age_data,
                           district_data=district_data)
