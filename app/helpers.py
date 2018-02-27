from flask import request
from app.models import Nodes


def check_api_auth():
    """
    Authenticates the api key from the spiders against the nodes table.
    Also authenticates the front-end
    """
    auth = request.headers.get('Authorization', '').lower()
    node = request.headers.get('Authorization-Node', '').lower()
    try:
        type_, api_key = auth.split(None, 1)
        if type_ != 'token':
            # invalid Authorization scheme
            return False
        my_auth = Nodes.query.filter(Nodes.api_key == api_key, Nodes.unique_id == node, Nodes.active == True).first()
        if my_auth:
            # Valid api key
            return True
        else:
            # Token/Node combo is not valid.
            return False
    except (ValueError, KeyError):
        # split failures or API key not valid
        return False
