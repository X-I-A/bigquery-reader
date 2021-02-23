import json
import base64
from urllib.parse import quote_plus
from flask import Blueprint, render_template, g, current_app

home = Blueprint('home',  __name__)


@home.route('/', methods=["GET"])
def home_page():
    report = {"name": "dummy", "type": "view", "description": "Dummy view"}
    report["detail_url"] = "/reports/" + base64.b32encode(report["name"].encode()).decode()
    preview_config = json.dumps({"projectId": current_app.config["PROJECT_ID"],
                                 "datasetId": current_app.config["DATASET"],
                                 "tableId": report["name"],
                                 "billingProjectId": current_app.config["PROJECT_ID"],
                                 "connectorType": "BIG_QUERY",
                                 "sqlType": "STANDARD_SQL"}, ensure_ascii=False)
    report["preview_url"] = "https://datastudio.google.com/u/0/explorer?config=" + quote_plus(preview_config)
    reports = [report]
    return render_template("index.html", title="Bigquery Explorer", reports=reports, param=g)

@home.route('/reports/<report_id>', methods=["GET"])
def display_report(report_id):
    report = {"name": "123", "type": "view", "description": "456"}
    children = [
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}],
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}]
    ]
    return render_template("report.html", title="Report", report=report, children=children, param=g)

@home.route('/reports/<report_id>/nodes/<node_id>', methods=["GET"])
def display_node(report_id, node_id):
    parents = [
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}],
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}]
    ]
    node = {"name": "123", "type": "view", "description": "456"}
    children = [
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}],
        [{"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"},
         {"name": "123", "type": "view", "description": "456"}]
    ]
    return render_template("node.html", title="Node", parents=parents, node=node, children=children, param=g)

