import os
from pathlib import Path
from flask import Flask, request, g, render_template
import google.auth
from modules.home.view import home

app = Flask(__name__)

app.register_blueprint(home)

app.config["PROJECT_ID"] = google.auth.default()[1]
app.config["DATASET"] = 'test_builder'
app.config["MODEL_PATH"] = os.path.join(Path(__file__).parent, "models")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=int(os.environ.get('PORT', 8080)))  # pragma: no cover