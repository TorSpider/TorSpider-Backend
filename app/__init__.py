from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.add_extension('jinja2.ext.do')
app.threaded = True

config_path = environ.get("CONF_PATH", "app.config.ProductionConf")
app.config.from_object(config_path)

db = SQLAlchemy(app)

from app import api, models


