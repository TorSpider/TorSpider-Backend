from sqlalchemy import and_, or_
from flask import jsonify
from flask import request
from flask import abort
from app import app
from app.helpers import check_api_auth
from app.models import Urls, Onions
from datetime import date, timedelta
import random
import json


@app.route("/api/next", methods=["GET"])
def next_url():
    # TODO find a better serializer function
    # We get the node name from the get param, otherwise leave it blank
    if not check_api_auth:
        abort(401)
    try:
        node_name = json.loads(request.args.get('q'))['node_name']
    except:
        node_name = None
    week_ago = (date.today() - timedelta(days=7))
    day_ago = (date.today() - timedelta(days=1))
    candidates = Urls.query.join(Onions).filter(
        or_(and_(Urls.fault == None, Urls.date < week_ago),
            and_(Onions.online == True, Onions.tries != 0, Onions.last_node != node_name),
            and_(Onions.online == False, Onions.scan_date < day_ago, Onions.last_node != node_name))).all()
    if len(candidates) is 0:
        return jsonify({'object': {}})
    random_candidate = random.choice(candidates)
    random_candidate_dict = dict(random_candidate)
    random_candidate_dict['domain_info'] = dict(random_candidate_dict['domain_info'])
    random_candidate_dict['domain_info']['urls'] = None
    return jsonify({'objects': random_candidate_dict})
