import time
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
import time
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db = SQLAlchemy()

class PsychologyTutor:
    def __init__(self, client: OpenAI):
        self.client = client
        self.assistant_id = self._get_assistant_id()

    def _get_assistant_id(self):
        """Global assistant shared by all users"""

        try:
            # Check if assistant already exists
            assistant = Assistant.get_by_name("Psychology Tutor")
            if not assistant:
                raise RuntimeError("Assistant not found. Run create_assistant.py first.")
            return assistant.assistant_id
        except Exception as e:
            logger.error(f"Error retrieving assistant ID: {e}")
            raise RuntimeError("Failed to retrieve Psychology Tutor assistant. Ensure it is created first.")


    def _get_or_create_thread_for_user(self, user_id):
        """Get or create thread for specific UID"""
        try:
            session = UserSession.get(user_id)
            if session:
                logger.debug(f"Using existing thread for user {user_id}: {session.thread_id}")
                return session.thread_id
            
            # If no session exists, create a new thread
            thread = self.client.beta.threads.create()
            # Save the mapping in database
            UserSession.create(user_id=user_id, assistant_id=self.assistant_id, thread_id=thread.id)
            logger.info(f"Created new thread for user {user_id}: {thread.id}")
            return thread.id
                
        except Exception as e:
            logger.error(f"Error getting or creating thread for user {user_id}: {e}")
            raise
            
    def log_message(self, user_id, message, response, response_time=None):
        log_entry = ChatLog(user_id=user_id, user_message=message, bot_response=response, response_time=response_time)
        logger.info(f"Logging message for user {user_id}: {message} -> {response}")
        db.session.add(log_entry)
        db.session.commit()

    def send_message(self, user_id, message):
        """Send message to assistant and get reply"""
        if not user_id or not message:
            logger.warning("Invalid user_id or message")
            return None
        try:   
            start_time = time.time()
            thread_id = self._get_or_create_thread_for_user(user_id)          

            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )

            # Poll for completion
            while True:
                status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if status.status == "completed":
                    break
                elif status.status in ["failed", "expired"]:
                    return "Error: Assistant failed to respond."
                time.sleep(1)
            end_time = time.time()
            # Get last assistant message
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            response = messages.data[0].content[0].text.value
            response_time = end_time - start_time
            # Log assistant reply
            self.log_message(user_id, message, response,response_time)
            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return "Error: Unable to process your request at this time."    
    
    

#------Assistant Model------
class Assistant(db.Model):
    __tablename__ = "assistants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    assistant_id = db.Column(db.String, nullable=False)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def create(cls, name, assistant_id):
        # Check if an assistant with the same name already exists
        existing = cls.query.filter_by(name=name).first()
        if existing:
            return existing  # Return existing record instead of creating a duplicate
        new_assistant = cls(name=name, assistant_id=assistant_id)
        db.session.add(new_assistant)

        return new_assistant

#------User Session Model------
class UserSession(db.Model):
    __tablename__ = "user_sessions"
    user_id = db.Column(db.String, primary_key=True)
    assistant_id = db.Column(db.String, nullable=False)
    thread_id = db.Column(db.String, nullable=False)

    @classmethod
    def get(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def create(cls, user_id, assistant_id, thread_id):
        existing = cls.get(user_id)
        if existing:
            existing.thread_id = thread_id
            existing.assistant_id = assistant_id
            db.session.commit()
            return existing

        session = cls(user_id=user_id, assistant_id=assistant_id, thread_id=thread_id)
        db.session.add(session)
        db.session.commit()
        return session

    def update_thread(self, thread_id):
        self.thread_id = thread_id
        db.session.commit()

# ------Chat Log Model------
class ChatLog(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, nullable=False)           # Foreign key to UserSession.user_id (optional)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    response_time = db.Column(db.Float, nullable=True)  # Time taken for the response
    timestamp = db.Column(db.DateTime, default=db.func.now())

