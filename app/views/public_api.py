from app.useful_functions import *
from flask import jsonify
from flask import request
from flask import abort
from app import app, db
from app.helpers import check_api_auth
from app.models import Onions
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
    onion_domain = ''
    for part in parts:
        if part.endswith('.onion'):
            onion_domain = part
            break

    try:
        # Get the Onion's data and send it off.
        onion = Onions.query.filter(Onions.domain == onion_domain).first()
        return_value = {
            "domain": onion.domain,
            "online": onion.online,
            "last_online": onion.last_online,
            "scan_date": onion.scan_date,
            "base_url": onion.base_url,
            "title": onion.title
        }
        return json.dumps({'objects': return_value})
    except:
        # If there's an error, return nothing.
        return jsonify({"objects": []})

@app.route('/api/submit_url', methods=['PUT','POST'])
def submit_url():
    # Add a new url to the database if it doesn't already exist.

    try:
        # Get the requested url.
        submitted_url = json.loads(request.args.get('q'))['node_name']
    except:
        # Invalid request.
        abort(400)

    try:
        # Add the url and its base onion to the list of urls to be scanned.

        # Add the url as-is.
        new_url = Urls()
        new_url.url = fix_url(submitted_url)

        # Add the base onion as both http and https.
        onion_url_http = Urls()
        onion_url_https = Urls()
        parts = submitted_url.split('/')
        for part in parts:
            if part.endswith('.onion'):
                onion_url_http.url = 'http://{}/'.format(part)
                onion_url_https.url = 'https://{}/'.format(part)
                break

        result = {
                'URL': 'Success',
                'HTTP': 'Success',
                'HTTPS': 'Success'
        }
        # Try adding the new_url.
        try:
            db.session.add(new_url)
            db.session.commit()
        except:
            db.session.rollback()
            result['URL'] = 'Failure'
        # Try adding the onion_url_http.
        try:
            db.session.add(new_url)
            db.session.commit()
        except:
            db.session.rollback()
            result['HTTP'] = 'Failure'
        # Try adding the onion_url_https.
        try:
            db.session.add(new_url)
            db.session.commit()
        except:
            db.session.rollback()
            result['HTTPS'] = 'Failure'

        return json.dumps({'objects': result})
    except:
        # If there's an error, return nothing.
        return jsonify({"objects": []})
