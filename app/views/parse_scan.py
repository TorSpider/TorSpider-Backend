# Parse the scan data returned by the spider.
# TODO: Fill in all necessary updates in order to process returned data.

from app import app, db
from app.helpers import check_api_auth
from app.models import *
from flask import jsonify
from flask import request
from flask import abort
import json
from sqlalchemy import and_, or_


@app.route("/api/parse_scan", methods=["PUT", "POST"])
def parse_scan():
    if not check_api_auth():
        abort(401)  # Unauthorized.
    try:
        scan_result = json.loads(request.args.get('q'))
    except:
        # Could not load the scan_result from the query.
        abort(400)  # Bad request.
    return "Success!"
