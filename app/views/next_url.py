from sqlalchemy import and_, or_
from flask import jsonify
from flask import request
from flask import abort
from app import app, db
from app.helpers import check_api_auth
from app.models import Urls, UrlQueue
import json


@app.route("/api/next", methods=["GET"])
def next_url():
    # We get the node name from the get param, otherwise leave it blank
    if not check_api_auth:
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
        # Grab the details of that url
        candidate = Urls.query.filter(Urls.url == next_url.url).first()
        # If this node was the last node, let's try again until that doesn't happen
        if candidate.domain_info.last_node != node_name:
            break
    if not candidate:
        return jsonify({'object': {}})
    # Build the dict
    next_item = dict(candidate)
    next_item['domain_info'] = dict(next_item['domain_info'])
    next_item['domain_info']['urls'] = None
    # Pop the item off the queue
    try:
        db.session.delete(next_url)
        db.session.commit()
    except:
        db.session.rollback()
    # Return the dict
    return jsonify({'objects': next_item})
