from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import db, aadharinfo, entrylogs
import pandas as pd

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analysis",methods=['GET','POST'],endpoint="analysis")
def analysis():
    logs = entrylogs.query.all()
    data = [{
        'aadhar_number': log.aadhar_number,
        'entry_time': log.entry_time,
        'entry_place': log.entry_place,
        'status': log.status,
        'name': log.card.name,
    } for log in logs]

    df = pd.DataFrame(data)
    if df.empty:
        return render_template("analysis.html",
                               total_entries=0,
                               total_exits=0,
                               daily_avg=0,
                               peak_hours=[],
                               weekly_data=[])

    df.entry_time = pd.to_datetime(df.entry_time)
    df['date'] = df.entry_time.dt.date
    df['hour'] = df.entry_time.dt.hour
    df['day'] = df.entry_time.dt.day_name()

    total_entries = df[df['status'] == 'Enterd'].shape[0]
    total_exits = df[df['status'] == 'Exited'].shape[0]

    daily_counts = df.groupby('date').size()
    daily_avg = round(daily_counts.mean(), 2)

    hourly_counts = df[df['status'] == 'Enterd'].groupby('hour').size().sort_values(ascending=False).head(5)
    peak_hours = []
    for hour, count in hourly_counts.items():
        start_hour = f"{hour:02d}:00"
        end_hour = f"{(hour + 1):02d}:00"
        time_range = f"{start_hour} - {end_hour}"
        peak_hours.append((time_range, count))

    weekdays_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly = df[df['status'] == 'Enterd'].groupby('day').size().reindex(weekdays_order, fill_value=0)
    weekly_data = list(weekly.items())

    if total_exits == 0:
        entry_exit_ratio = "∞"
    else:
        entry_exit_ratio = round(total_entries / total_exits, 2)

    return render_template("analysis.html",
                           total_entries=total_entries,
                           total_exits=total_exits,
                           daily_avg=daily_avg,
                           peak_hours=peak_hours,
                           weekly_data=weekly_data,
                           entry_exit_ratio=entry_exit_ratio)
