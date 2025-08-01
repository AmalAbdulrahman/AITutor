# AITutor
Customised AI Tutor using OPENAI GPT

## STEPS (on the server from the root folder):

1- python(3) init_db_KG.py

2- python(3) create_assistant.py

3- gunicorn -w 4 -b 0.0.0.0:8000 main:application --timeout XX

