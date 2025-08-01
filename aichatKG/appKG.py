from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import logging
from dotenv import load_dotenv
import time
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from aichatKG.PsychologyTutor import db, PsychologyTutor, UserSession, ChatLog

# Simple Flask app
appKG = Flask(__name__,instance_relative_config=True)
# Ensure instance path exists before using it
if not os.path.exists(appKG.instance_path):
    os.makedirs(appKG.instance_path, exist_ok=True)

# Always resolve the .venv file relative to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, ".venv")
# Load .venv file explicitly
load_dotenv(dotenv_path=ENV_PATH)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure main logger
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG only when debugging
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("aichatKG")

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Session and DB config
appKG.config['SESSION_TYPE'] = 'filesystem'  # Store session data in server files
appKG.config['SESSION_PERMANENT'] = False
appKG.config['SESSION_FILE_DIR'] = os.path.join(appKG.instance_path, 'flask_session')
os.makedirs(appKG.config['SESSION_FILE_DIR'], exist_ok=True)

# Database setup
db_path = os.path.join(appKG.instance_path, 'chatlogKG.db')
appKG.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
appKG.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(appKG)

# Create the database (if it doesn't exist)

# with appKG.app_context():
#     if not os.path.exists(db_path):        
#         db.create_all()
#         logger.info("Database created.")
#     else:
#         logger.info("Database already exists.")
#     #tutor = PsychologyTutor(client) 
#     #logger.info(f"Psychology Tutor {tutor.assistant_id} initialized.")

    

# @@@@@@@@@@@@@@@@ Routes and Handlers @@@@@@@@@@@@@@@@
@appKG.route('/')
def index():
    return render_template("chatKG.html")


@appKG.route('/ask', methods=['POST'])
def ask():
    tutor = PsychologyTutor(client) # retrieve assistant_id from DB
    """Handle user messages"""
    user_id = request.args.get("UID")
    message = request.json.get("message")

    if not user_id:
        return jsonify({"response": "Missing user_id or UID"}), 400
    
    reply = tutor.send_message(user_id, message)
    return jsonify({"response": reply})

if __name__ == '__main__':
    appKG.run(debug=True)


# --- Route to retrieve all user sessions ---
@appKG.route("/sessions")
def get_sessions():
    try:
        sessions = UserSession.query.order_by(UserSession.user_id.asc()).all()        
        return render_template("sessions.html", sessions=sessions)
    except Exception as e:
        return {"error": str(e)}, 500

# --- Route to retrieve chat logs for a specific user ---
@appKG.route("/logs")
def get_all_logs():
    """Retrieve all chat logs for all users, ordered by user_id and timestamp"""
    try:
        logs = ChatLog.query.order_by(ChatLog.user_id.asc(), ChatLog.timestamp.asc()).all()

        logs_data = [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_message": log.user_message,
                "bot_response": log.bot_response,
                "response_time": log.response_time,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]

        return render_template("logs.html", logs=logs_data)
    except Exception as e:
        return {"error": str(e)}, 500
