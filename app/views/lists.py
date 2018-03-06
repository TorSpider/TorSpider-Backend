from app.models import TopLists
from app.helpers import check_api_auth, top_twenty_inlinks, top_twenty_outlinks, top_twenty_page_count
from flask import jsonify
from flask import abort
from app import app, db
import json

@app.route("/api/top20", methods=["GET"])
def top_twenty():
    abort(404)


@app.route("/api/top20/pages/live", methods=["GET"])
def api_top_twenty_page_count_live():
    if not check_api_auth(frontend_only=True):
        abort(401)
    return top_twenty_page_count()


@app.route("/api/top20/pages", methods=["GET"])
def api_top_twenty_page_count():
    if not check_api_auth(frontend_only=True):
        abort(401)
    thelist = db.session.query(TopLists.list_data).filter(TopLists.list_name == 'pages').first()
    if thelist:
        return thelist[0]
    else:
        return jsonify({"objects": []})


@app.route("/api/top20/outlinks/live", methods=["GET"])
def api_top_twenty_outlinks_live():
    if not check_api_auth(frontend_only=True):
        abort(401)
    return top_twenty_outlinks()


@app.route("/api/top20/outlinks", methods=["GET"])
def api_top_twenty_outlinks():
    if not check_api_auth(frontend_only=True):
        abort(401)
    thelist = db.session.query(TopLists.list_data).filter(TopLists.list_name == 'outlinks').first()
    if thelist:
        return thelist[0]
    else:
        return jsonify({"objects": []})


@app.route("/api/top20/inlinks/live", methods=["GET"])
def api_top_twenty_inlinks_live():
    if not check_api_auth(frontend_only=True):
        abort(401)
    return top_twenty_inlinks()


@app.route("/api/top20/inlinks", methods=["GET"])
def api_top_twenty_inlinks():
    if not check_api_auth(frontend_only=True):
        abort(401)
    thelist = db.session.query(TopLists.list_data).filter(TopLists.list_name == 'inlinks').first()
    if thelist:
        return thelist[0]
    else:
        return jsonify({"objects": []})
