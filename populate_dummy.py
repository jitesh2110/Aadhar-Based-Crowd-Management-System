import pandas as pd
import random
from datetime import datetime, timedelta
from main import db, app
from models import aadharinfo, entrylogs

CSV_FILE = "aadhardata.csv"


def get_last_log(aadhar_number):
    """Get the last log for a person."""
    return entrylogs.query.filter_by(aadhar_number=aadhar_number).order_by(entrylogs.entry_time.desc()).first()


def populate_entrylogs_for_week(base_logs_per_day=300):
    places = ["Ramkund", "Sita Gufa", "Panchavati", "Kapaleshwar", "Godavari Ghat"]

    with app.app_context():
        people = aadharinfo.query.all()
        if not people:
            print("⚠️ No people found in DB. Run populate_aadharinfo first.")
            return

        now = datetime.now()
        today = now.date()

        for day_offset in range(7):  # last 7 days including today
            date = today - timedelta(days=day_offset)

            # 🎯 Vary number of logs per day: base ± 50
            variation = random.randint(-100, 100)
            num_logs = max(50, base_logs_per_day + variation)  # Minimum 50 logs
            print(f"📅 Inserting {num_logs} logs for {date} (variation: {variation:+d})...")

            for _ in range(num_logs):
                person = random.choice(people)
                aadhar = person.aadhar_number

                # ✅ Get last log for this person (across all dates)
                last_log = get_last_log(aadhar)

                # Generate random time first
                if date == today:
                    seconds_since_midnight = (now - datetime.combine(today, datetime.min.time())).seconds
                    random_seconds = random.randint(0, seconds_since_midnight)
                else:
                    random_seconds = random.randint(0, 24 * 3600 - 1)

                proposed_time = datetime.combine(date, datetime.min.time()) + timedelta(seconds=random_seconds)
                entry_place = random.choice(places)

                logs_to_add = []

                # ✅ Logic to ensure proper enter/exit sequence
                if last_log is None or last_log.status == "Exited":
                    # Can only ENTER if no previous log or last was EXIT
                    log = entrylogs(
                        aadhar_number=aadhar,
                        entry_time=proposed_time,
                        entry_place=entry_place,
                        current_place=entry_place,
                        visited_places=entry_place,
                        status="Enterd"
                    )
                    logs_to_add.append(log)
                else:
                    # Last was ENTERED, so must EXIT first, then can ENTER
                    # Add EXIT log first (same place as last log, slightly earlier time)
                    exit_time = proposed_time - timedelta(seconds=random.randint(60, 600))  # 1-10 min earlier

                    exit_log = entrylogs(
                        aadhar_number=aadhar,
                        entry_time=exit_time,
                        entry_place=last_log.entry_place,
                        current_place=last_log.entry_place,
                        visited_places=last_log.visited_places,
                        status="Exited"
                    )
                    logs_to_add.append(exit_log)

                    # Now add ENTER log
                    enter_log = entrylogs(
                        aadhar_number=aadhar,
                        entry_time=proposed_time,
                        entry_place=entry_place,
                        current_place=entry_place,
                        visited_places=entry_place,
                        status="Enterd"
                    )
                    logs_to_add.append(enter_log)

                # Add all logs for this iteration
                for log in logs_to_add:
                    db.session.add(log)

            db.session.commit()
            print(f"✅ Inserted {num_logs} logs for {date}.")

    print("🎉 Finished populating logs for the last 7 days.")


if __name__ == "__main__":
    populate_entrylogs_for_week(150)
