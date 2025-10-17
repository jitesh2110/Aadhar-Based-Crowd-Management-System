from main import db, app
from models import entrylogs

with app.app_context():
    num_deleted = entrylogs.query.delete()
    db.session.commit()
    print(f"🗑️ Deleted {num_deleted} logs from entrylogs table.")