from flask_restless import ProcessingException
from flask_restless_swagger import SwagAPIManager as APIManager
from app import app, db
from app.models import Onions, Urls, Pages, Forms, Links, Nodes
from flask import request

# Flask- Restless
manager = APIManager(app, flask_sqlalchemy_db=db)


# Define the different pre_processors to limit API access


def authenticated_preprocessor(search_params=None, **kwargs):
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
            raise ProcessingException(description='Not Authorized', code=401)
        my_auth = Nodes.query.filter(Nodes.api_key == api_key, Nodes.unique_id == node, Nodes.active == True).first()
        if my_auth:
            # Valid api key
            return True
        else:
            # Token/Node combo is not valid.
            raise ProcessingException(description='Not Authorized', code=401)
    except (ValueError, KeyError):
        # split failures or API key not valid
        raise ProcessingException(description='Not Authorized', code=401)


# Endpoints available at /api/<table_name>
manager.create_api(Onions, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))

manager.create_api(Urls, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))

manager.create_api(Pages, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))

manager.create_api(Forms, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))

manager.create_api(Links, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))

manager.create_api(Nodes, methods=['POST', 'GET', 'PUT', 'PATCH', 'DELETE'], results_per_page=0,
                   allow_patch_many=True, allow_functions=True, allow_delete_many=True,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor],
                                      POST=[authenticated_preprocessor],
                                      PUT=[authenticated_preprocessor],
                                      PATCH=[authenticated_preprocessor],
                                      DELETE=[authenticated_preprocessor]))
