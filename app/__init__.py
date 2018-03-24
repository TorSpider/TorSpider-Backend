from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.json import JSONEncoder
from contextlib import suppress
from werkzeug.contrib.fixers import ProxyFix
from celery import Celery
from app import celery_config

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.add_extension('jinja2.ext.do')
app.threaded = True

app.wsgi_app = ProxyFix(app.wsgi_app)

config_path = environ.get("CONF_PATH", "app.config.ProductionConf")
app.config.from_object(config_path)

db = SQLAlchemy(app)


def make_celery(app):
    # create context tasks in celery
    celery = Celery(
        app.import_name,
        broker=app.config['BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.config_from_object(celery_config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


celery = make_celery(app)


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        # Optional: convert datetime objects to ISO format
        with suppress(AttributeError):
            return obj.isoformat()
        return dict(obj)


app.json_encoder = MyJSONEncoder

from app import api, models
from app.views import next_url, lists, parse_scan

