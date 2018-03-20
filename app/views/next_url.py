from flask import jsonify
from flask import request
from flask import abort
from app import app, db
from app.helpers import check_api_auth
from app.models import Urls, UrlQueue
from urllib.parse import urlsplit
import json


@app.route("/api/next", methods=["GET"])
def next_url():
    # We get the node name from the get param, otherwise leave it blank
    if not check_api_auth():
        abort(401)
    try:
        node_name = json.loads(request.args.get('q'))['node_name']
    except:
        node_name = None
    # There's a situation where this could loop forever, so we'll put a safetynet here.
    retries = 0
    while retries <= 30:
        retries += 1
        # Grab a random item from the queue
        next_url = UrlQueue.query.order_by(db.func.random()).first()
        if not next_url:
            return jsonify({'object': {}})
        if not is_http(next_url.url):
            # Make sure we only send http/https urls.
            continue
        # Grab the details of that url
        candidate = Urls.query.filter(Urls.url == next_url.url).first()
        # If this node was the last node, let's try again until that doesn't happen
        if candidate.domain_info.last_node != node_name:
            break
    if not candidate:
        return jsonify({'object': {}})
    # Build the dict
    next_item = {'url': candidate.url, 'hash': candidate.hash}
    # Pop the item off the queue
    try:
        db.session.delete(next_url)
        db.session.commit()
    except:
        db.session.rollback()
    # Return the dict
    return jsonify({'objects': next_item})


def is_http(url):
    # Determine whether the link is an http/https scheme or not.
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    return True if 'http' in scheme else False
