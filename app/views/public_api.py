from flask import jsonify
from flask import request
from flask import abort
from app import app, db
from app.helpers import check_api_auth
from app.useful_functions import *
from app.models import Urls, UrlQueue
from urllib.parse import urlsplit
import datetime
import json

# Public API calls. These are available without authentication, so that the
# general public can access them.

@app.route('/api/onion_info', methods=['GET'])
def onion_info():
    # Get the basic information about the specified onion.

    # Are we authenticated?
    # NOTE: As of right now, the returned information is the same regardless
    # of authentication. However, in the future, we might want to return
    # less data to clients without authentication.
    authenticated = False
    if check_api_auth():
        # We'll provide more information in an authenticated request.
        authenticated = True

    try:
        # Get the requested url.
        onion_request = json.loads(request.args.get('q'))['node_name']
    except:
        # Invalid request.
        abort(400)

    # Get the base onion domain.
    parts = onion_request.split('/')
    for part in parts:
        if part.endswith('.onion'):
            onion_request = part
            break

    try:
        # Get the Onion's data and send it off.
        onion = Onions.query.filter(Onions.domain == onion).first()
        return_value = {
            domain = onion.domain,
            online = onion.online,
            last_online = onion.last_online,
            scan_date = onion.scan_date,
            base_url = onion.base_url,
            title = onion.title
        }
        return json.dumps({'objects': return_value})
    except:
        # If there's an error, return nothing.
        return jsonify({"objects": []})
