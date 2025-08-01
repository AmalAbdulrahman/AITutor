import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # ensure imports work

from aichatKG.appKG import appKG, db
from aichatKG.PsychologyTutor import Assistant
from openai import OpenAI

client = OpenAI()

def create_psychology_tutor():
    with appKG.app_context():
        # Check if already exists
        record = Assistant.get_by_name("Psychology Tutor")
        if record:
            db.session.delete(record)
            db.session.commit()
            print(f"Assistant already exists and deleted: {record.assistant_id}")
            

        # Create new assistant
        assistant = client.beta.assistants.create(
            name="Psychology Tutor",
            model="gpt-4o",
            instructions="""You are a friendly and supportive psychology tutor guiding students through personality theory analysis.

                    Your objective:
                    - Help students analyse behaviour using decision-making bases retrieved from knowledge graph 
                    - Maintain structured guidance internally but present it naturally as a conversation.

                    CRITICAL BEHAVIOR RULES:
                    1. Do NOT reveal internal steps or phase names (e.g., "Introduction," "Theory Overview").
                    2. STAY ON TOPIC: Only discuss psychology, personality theories, and the student's scenario
                    3. FOLLOW THE STRUCTURED FLOW: Introduction → Theory Overview → Scenario → 6 Bases → Synthesis
                    4. LIMIT TURNS PER BASIS: Don't spend more than 4 exchanges on any single basis
                    5. USE KNOWLEDGE GRAPH: Always retrieve current theories and bases from the knowledge graph
                    6. BE FOCUSED: Guide students efficiently through the learning process

                    Always use the provided functions to get up-to-date information from the knowledge graph.
                    Be warm, supportive, clear, brief but efficient - this is structured and socratic-style learning, not casual chat."""
        )

        # Save to DB
        Assistant.create("Psychology Tutor", assistant.id)
        db.session.commit()
        print(f"Created Psychology Tutor assistant: {assistant.id}")

if __name__ == "__main__":
    create_psychology_tutor()
    print("Psychology Tutor assistant created successfully.")