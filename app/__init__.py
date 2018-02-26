from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.json import JSONEncoder
from contextlib import suppress

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.add_extension('jinja2.ext.do')
app.threaded = True

config_path = environ.get("CONF_PATH", "app.config.ProductionConf")
app.config.from_object(config_path)

db = SQLAlchemy(app)

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        # Optional: convert datetime objects to ISO format
        with suppress(AttributeError):
            return obj.isoformat()
        return dict(obj)

app.json_encoder = MyJSONEncoder

from app import api, models
from app.views import next_url, lists
