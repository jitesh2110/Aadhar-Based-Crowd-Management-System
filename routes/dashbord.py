from flask import Blueprint, render_template
from models import db, aadharinfo, entrylogs
import pandas as pd
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", methods=['GET'], endpoint="dashboard")
def dashboard():
    logs = entrylogs.query.all()
    data = []
    for log in logs:
        if log.card:
            data.append({
                'aadhar_number': log.aadhar_number,
                'entry_time': log.entry_time,
                'entry_place': log.entry_place,
                'status': log.status.strip().capitalize(),  # normalize
                'name': log.card.name,
            })

    df = pd.DataFrame(data)

    if df.empty:
        dash_data = {
            'total_count': 0,
            'active_count': 0,
            'today_entry_increase': 0,
            'exit_count': 0,
            'peak_count': 0,
            'peak_hour': 'N/A',
            'recent_logs': [],
            'flow_data': []
        }
        return render_template("dashboard.html", dash_data=dash_data)


    df['entry_time'] = pd.to_datetime(df['entry_time'])

    # Current active count
    latest_status = df.sort_values('entry_time').groupby('aadhar_number').last().reset_index()
    todays_active_count = latest_status[latest_status['status'] == 'Enterd']['aadhar_number'].nunique()

    # Today's entries
    today_entries = df[(df['status'] == 'Enterd') & (df['entry_time'].dt.date == date.today())]
    today_entry_count = today_entries['aadhar_number'].nunique()

    # Yesterday entries
    yesterday_entries = df[(df['status'] == 'Enterd') & (df['entry_time'].dt.date == (date.today() - pd.Timedelta(days=1)))]
    yesterday_entry_count = yesterday_entries['aadhar_number'].nunique()

    today_percent_increase = ((today_entry_count / yesterday_entry_count) * 100) if yesterday_entry_count else 0

    # Exits
    today_exits = df[(df['status'] == 'Exited') & (df['entry_time'].dt.date == date.today())]
    today_exit_count = today_exits['aadhar_number'].nunique()

    # Peak hour
    df['hour'] = df['entry_time'].dt.floor('H')
    hourly_count = df[df['status'] == 'Enterd'].groupby('hour').size().reset_index(name='count')
    if not hourly_count.empty:
        peak_row = hourly_count.loc[hourly_count['count'].idxmax()]
        peak_count = peak_row['count']
        peak_hour = peak_row['hour'].strftime('%H:%M')
    else:
        peak_count = 0
        peak_hour = 'N/A'

    # Flow data
    today_df = df[df['entry_time'].dt.date == date.today()]
    hourly = today_df.groupby(['hour', 'status']).size().reset_index(name='count')
    pivoted_hourly = hourly.pivot_table(index='hour', columns='status', values='count', fill_value=0).reset_index()
    if 'Enterd' not in pivoted_hourly.columns:
        pivoted_hourly['Enterd'] = 0
    if 'Exited' not in pivoted_hourly.columns:
        pivoted_hourly['Exited'] = 0
    flow_data = list(pivoted_hourly[['hour', 'Enterd', 'Exited']].itertuples(index=False, name=None))

    # Recent logs
    recent_logs = df.sort_values(by='entry_time', ascending=False).head(5)
    recent_logs['entry_time'] = recent_logs['entry_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    recent_logs = recent_logs.to_dict(orient='records')

    dash_data = {
        'total_count': today_entry_count,
        'active_count': todays_active_count,
        'today_entry_increase': round(today_percent_increase, 2),
        'exit_count': today_exit_count,
        'peak_count': peak_count,
        'peak_hour': peak_hour,
        'recent_logs': recent_logs,
        'flow_data': flow_data
    }

    return render_template("dashbord.html", dash_data=dash_data)
