# init_db_KG.py
import os
from aichatKG.appKG import db, appKG

# Session and DB config
#appKG.config['SESSION_TYPE'] = 'filesystem'  # Store session data in server files
#appKG.config['SESSION_PERMANENT'] = False
#appKG.config['SESSION_FILE_DIR'] = os.path.join(appKG.instance_path, 'flask_session')
#os.makedirs(appKG.config['SESSION_FILE_DIR'], exist_ok=True)

# Database setup
db_path = os.path.join(appKG.instance_path, 'chatlogKG.db')
#appKG.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
#appKG.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
