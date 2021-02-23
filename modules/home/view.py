import os
import base64

from functools import reduce
from flask import Blueprint, render_template, g, current_app
from bigquery_builder import Builder

home = Blueprint('home',  __name__)


@home.route('/', methods=["GET"])
def home_page():
    builder = Builder(current_app.config["MODEL_PATH"])
    report = {"name": "test1", "type": "view", "description": "Table Extraction view"}
    report["detail_url"] = "/reports/" + base64.b32encode(report["name"].encode()).decode()
    report["preview_url"] = builder.get_preview_url(current_app.config["DATASET"], report["name"])
    reports = [report]
    return render_template("index.html", title="Bigquery Explorer", reports=reports, param=g)

@home.route('/reports/<report_id>', methods=["GET"])
def display_report(report_id):
    builder = Builder(current_app.config["MODEL_PATH"])
    report_name = base64.b32decode(report_id).decode()
    parsed_data = builder.view_parser(report_name)
    all_nodes = set([node["name"] for node in parsed_data["nodes"]])
    all_ressources = set(reduce(lambda x, y: x + y, [node["dependencies"] for node in parsed_data["nodes"]]))
    all_dependencies = all_ressources - all_nodes

    report = {"name": report_name, "type": "view", "description": parsed_data["comments"], "nodes": []}
    cur_level_nodes = ["Semantics"]
    node_url = "/reports/" + report_id + "/nodes/" + base64.b32encode("Semantics".encode()).decode()
    node_dict = {"name": "Semantics", "url": node_url}
    report["nodes"].append([node_dict.copy()])
    all_nodes -= {"Semantics"}

    counter = 9
    while all_nodes or counter == 0:
        counter -= 1
        last_level_nodes = cur_level_nodes.copy()
        cur_level_nodes, cur_level_dicts = [], []
        for last_node in last_level_nodes:
            last_node_detail = [node for node in parsed_data["nodes"] if node["name"] == last_node][0]
            for node in last_node_detail.get("dependencies", []):
                if node in all_nodes:
                    cur_level_nodes.append(node)
                    node_url = "/reports/" + report_id + "/nodes/" + base64.b32encode(node.encode()).decode()
                    node_dict = {"name": node, "url": node_url}
                    cur_level_dicts.append(node_dict)
                    all_nodes -= {node}
        report["nodes"].append(cur_level_dicts)
    if all_nodes:
        cur_level_dicts = []
        for node in all_nodes:
            node_url = "/reports/" + report_id + "/nodes/" + base64.b32encode(node.encode()).decode()
            node_dict = {"name": node, "url": node_url}
            cur_level_dicts.append(node_dict)
        report["nodes"].append(cur_level_dicts)

    report["preview_url"] = builder.get_preview_url(current_app.config["DATASET"], report_name)

    counter, some_children, children = 0, [], []
    for dependency in all_dependencies:
        dataset, name = [item.strip('`"''') for item in dependency.split(".")]
        child = {"name": name, "type": "view" if dataset == current_app.config["DATASET"] else "table"}
        child["description"] = builder.view_parser(name)["comments"] if child["type"] == "view" else ""
        child["detail_url"] = "/reports/" + base64.b32encode(child["name"].encode()).decode() if child["type"] == "view" else ""
        children.append(child)

    return render_template("report.html", title="Report", report=report, children=children, param=g)

@home.route('/reports/<report_id>/nodes/<node_id>', methods=["GET"])
def display_node(report_id, node_id):
    builder = Builder(current_app.config["MODEL_PATH"])
    report_name = base64.b32decode(report_id).decode()
    node_name = base64.b32decode(node_id).decode()
    builder.create_view(current_app.config["DATASET"], report_name, node_name)
    parsed_data = builder.view_parser(report_name)
    node_detail = [node for node in parsed_data["nodes"] if node["name"] == node_name][0]
    all_nodes = set([node["name"] for node in parsed_data["nodes"]])
    node_url_root = "/reports/" + report_id + "/nodes/"

    parent_nodes, parents = node_detail["dependencies"], []
    for node in parent_nodes:
        node_url = node_url_root + base64.b32encode(node.encode()).decode() if node in all_nodes else "#"
        node_dict = {"name": node, "url": node_url}
        parents.append(node_dict.copy())

    child_nodes, children = [node["name"] for node in parsed_data["nodes"] if node_name in node["dependencies"]], []
    for node in child_nodes:
        node_url = node_url_root + base64.b32encode(node.encode()).decode()
        node_dict = {"name": node, "url": node_url}
        children.append(node_dict.copy())

    fields = [f.lower().split(" ")[-1] for f in " ".join(node_detail["select"]).split(",") if f and f[-1] != "'"]
    node_preview_url = builder.get_preview_url(current_app.config["DATASET"], report_name, node_name)
    cur_node = {"name": node_name, "description": node_detail["comments"], "fields": fields,
                "preview_url": node_preview_url, "report_url": "/reports/" + report_id}

    return render_template("node.html", title="Node", parents=parents, node=cur_node, children=children, param=g)
