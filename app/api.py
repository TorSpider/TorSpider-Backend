from flask_restless import ProcessingException
from flask_restless_swagger import SwagAPIManager as APIManager
from flask_login import current_user
from app import app, db
from app.models import Onions, Urls, Pages, Forms, Links

# Flask- Restless
manager = APIManager(app, flask_sqlalchemy_db=db)


# Define the different pre_processors to limit API access


def authenticated_preprocessor(search_params=None, **kwargs):
    # Bypass auth for now
    return True
    if not current_user.is_authenticated():
        raise ProcessingException(description='Access Denied!', code=401)
    return True


# Endpoints available at /api/<table_name>
manager.create_api(Onions, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor]))

manager.create_api(Urls, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor]))

manager.create_api(Pages, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor]))

manager.create_api(Forms, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor]))

manager.create_api(Links, methods=['POST', 'GET', 'PUT', 'PATCH'], results_per_page=0,
                   preprocessors=dict(GET_SINGLE=[authenticated_preprocessor],
                                      GET_MANY=[authenticated_preprocessor]))
