from app import app, db
from app.helpers import check_api_auth
from app.models import ParseQueue
from app.tasks.parse_scans import parse_scan
from flask import request
from flask import abort
import json



@app.route("/api/parse", methods=["POST"])
def queue_parse():
    """
    This function adds the result data to a queue table of items to parse, which offloads this job to a periodically
    schedule script using celery.  This performs ensures that the parse doesn't block the response to the request
    so the spiders can just continue on to the next url.
    :return: Success of Failure Dict.
    """
    if not check_api_auth():
        abort(401)  # Unauthorized.

    # Get the scan_result from the query.
    try:
        # Grab the data from the body of the request
        scan_result = request.data
        # Add the data to the queue
        new_parse = ParseQueue()
        new_parse.parse_data = scan_result
        db.session.add(new_parse)
        db.session.commit()
        parse_scan.apply_async(args=[new_parse.id])
        return json.dumps({"status": "success"})
    except:
        # Could not load the scan_result from the query.
        db.session.rollback()
        abort(400)  # Bad request.



