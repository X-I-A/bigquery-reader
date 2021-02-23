import os
from flask import Flask, request, g, render_template
import google.auth
from modules.home.view import home

app = Flask(__name__)

app.register_blueprint(home)

app.config["PROJECT_ID"] = google.auth.default()[1]
app.config["DATASET"] = 'rmsp'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=int(os.environ.get('PORT', 8080)))  # pragma: no cover