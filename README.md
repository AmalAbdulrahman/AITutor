# AI Tutor
Customised AI Tutor using OPENAI GPT.
To learn more about how to customise the GPT instructions: https://help.openai.com/en/articles/9358033-key-guidelines-for-writing-instructions-for-custom-gpts.


## STEPS (on the server from the root folder):

1- python(3) init_db_KG.py

2- python(3) create_assistant.py

3- gunicorn -w 4 -b 0.0.0.0:8000 main:application --timeout XX

