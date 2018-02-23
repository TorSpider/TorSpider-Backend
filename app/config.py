import sys
import os
import logging

# DB
u = "torspider"
p = "password"
h = "127.0.0.1"
d = "TorSpider"

root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

class ProductionConf(object):
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:5432/{}".format(u, p, h, d)
    SECRET_KEY = 'CHANGE-SECRET-KEY'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'CHANGE-CSRF-SECRET-KEY'
    USETLS = False
    # Debugging stuff
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    LISTEN_PORT = 1080

