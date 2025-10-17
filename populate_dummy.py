import pandas as pd
import random
from datetime import datetime, timedelta
from main import db, app
from models import aadharinfo, entrylogs

CSV_FILE = "aadhardata.csv"

def populate_entrylogs_for_week(num_logs_per_day=200):
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
            print(f"📅 Inserting logs for {date} ...")

            for _ in range(num_logs_per_day):
                person = random.choice(people)

                # ✅ Generate random time logic
                if date == today:
                    # only before current time
                    seconds_since_midnight = (now - datetime.combine(today, datetime.min.time())).seconds
                    random_seconds = random.randint(0, seconds_since_midnight)
                else:
                    # full day range for previous days
                    random_seconds = random.randint(0, 24 * 3600 - 1)

                random_time = datetime.combine(date, datetime.min.time()) + timedelta(seconds=random_seconds)

                entry_place = random.choice(places)
                status = random.choice(["Enterd", "Exited"])

                log = entrylogs(
                    aadhar_number=person.aadhar_number,
                    entry_time=random_time,
                    entry_place=entry_place,
                    current_place=entry_place,
                    visited_places=entry_place,
                    status=status
                )
                db.session.add(log)

            db.session.commit()
            print(f"✅ Inserted {num_logs_per_day} logs for {date}.")

    print("🎉 Finished populating logs for the last 7 days.")


if __name__ == "__main__":
    populate_entrylogs_for_week(100)
