from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask import Flask

# Import the two apps
from aichat.app import app as app
from aichatKG.appKG import appKG as appKG

# Optional root app (can return 404 or a basic message)
root_app = Flask("root")

@root_app.route("/")
def home():
    return "This is the root of the server. Try /aichat or /aichatKG."

# Combine the apps using DispatcherMiddleware
application = DispatcherMiddleware(root_app, {
    '/aichat': app,
    '/aichatKG': appKG
})

# Run the apps via Werkzeug for development
if __name__ == "__main__":
    run_simple("0.0.0.0", 8000, application, use_reloader=True, use_debugger=True)
