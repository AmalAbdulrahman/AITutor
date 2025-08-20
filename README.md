# AI Tutor
Customised AI Tutor using OPENAI GPT.
To learn more about how to customise the GPT instructions: https://help.openai.com/en/articles/9358033-key-guidelines-for-writing-instructions-for-custom-gpts.


## STEPS (on the server from the root folder):

1- python(3) init_db_KG.py

2- python(3) create_assistant.py

3- gunicorn -w 4 -b 0.0.0.0:8000 main:application --timeout XX

## Sync files between the server and local machine (wsl):

If your project folder is in c:\\

$rsync -avz -e "ssh -i ~/.ssh/id_edXXXXX" <your-username-on-server>@<your-server-ip>:~/<root-folder>/instance /mnt/c/<project-folder-name>/

## Working with tmux

open tmux: tmux new -s <session-name, e.g.study>

activate vm: source venv/bin/activate

run the application: gunicorn -w 4 -b 0.0.0.0:8000 main:application --timeout 12

detach: Ctrl-b, then  d

Reconnect: tmux attach -t <session-name, e.g.study>

Kill session: tmux kill-session -t <session-name, e.g.study>
