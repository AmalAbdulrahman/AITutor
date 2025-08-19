# init_db_KG.py
import os
from aichatKG.appKG import db, appKG

# Database setup
db_path = os.path.join(appKG.instance_path, 'chatlogKG.db')

with appKG.app_context():
    # If the DB file exists, remove it
    if os.path.exists(db_path):
        print(f"Existing database found at {db_path}. Deleting...")
        os.remove(db_path)
    else:
        print("No existing database found. Creating a new one...")

    # Create all tables
    db.create_all()
    print("New database created successfully.")

