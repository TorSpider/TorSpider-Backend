import sys
import os
import logging
import configparser
import uuid
from app import app
from os import environ

os.makedirs(app.instance_path, exist_ok=True)


def read_config():
    if os.path.isfile(os.path.join(app.instance_path, 'backend.cfg')):
        # Load the configuration file.
        try:
            my_config = {}
            config = configparser.ConfigParser()
            config.read(os.path.join(app.instance_path, 'backend.cfg'))
            my_config['Database'] = {
                'user': config['Database'].get('user'),
                'password': config['Database'].get('password'),
                'host': config['Database'].get('host'),
                'database': config['Database'].get('database')
            }
            my_config['Flask'] = {
                'SECRET_KEY': config['Flask'].get('SECRET_KEY'),
                'USETLS': config['Flask'].getboolean('USETLS'),
                'CERT_FILE': config['Flask'].get('CERT_FILE'),
                'CERT_KEY_FILE': config['Flask'].get('CERT_KEY_FILE'),
                'DEBUG': config['Flask'].getboolean('DEBUG'),
                'LISTEN_PORT': config['Flask'].getint('LISTEN_PORT'),
                'LISTEN_ADDR': config['Flask'].get('LISTEN_ADDR')
            }
            my_config['SQLAlchemy'] = {
                'SQLALCHEMY_ECHO': config['SQLAlchemy'].getboolean('SQLALCHEMY_ECHO'),
                'SQLALCHEMY_TRACK_MODIFICATIONS': config['SQLAlchemy'].getboolean('SQLALCHEMY_TRACK_MODIFICATIONS')
            }
            my_config['WTForms'] = {
                'WTF_CSRF_ENABLED': config['WTForms'].getboolean('WTF_CSRF_ENABLED'),
                'WTF_CSRF_SECRET_KEY': config['WTForms'].get('WTF_CSRF_SECRET_KEY')
            }
            my_config['LOGGING'] = {
                'loglevel': logging.getLevelName(config['LOGGING'].get('loglevel')),
                'apploglevel': logging.getLevelName(config['LOGGING'].get('apploglevel'))
            }
            my_config['REDIS'] = {
                'REDIS_HOST': config['REDIS'].get('REDIS_HOST'),
                'REDIS_PORT': config['REDIS'].getint('REDIS_PORT')
            }
            return my_config
        except Exception as e:
            print('Could not parse instance/backend.cfg. Please verify its syntax.')
            print('Error: {}'.format(e))
            sys.exit(0)


def make_config():
    '''
    Create the initial config file. 
    '''
    if not os.path.exists(os.path.join(app.instance_path, 'backend.cfg')):
        # If we don't yet have a configuration file, make one and tell the
        # user to set it up before continuing.
        default_config = configparser.RawConfigParser()
        default_config.optionxform = lambda option: option
        default_config['Database'] = {
            'user': 'torspider',
            'password': 'password',
            'host': '127.0.0.1',
            'database': 'TorSpider-Backend'
        }
        default_config['Flask'] = {
            'SECRET_KEY': uuid.uuid4(),
            'USETLS': True,
            'DEBUG': False,
            'LISTEN_PORT': 1080,
            'LISTENING_ADDR': '127.0.0.1',
            'CERT_FILE': '/etc/nginx/certs/torspider/backend.pem',
            'CERT_KEY_FILE': '/etc/nginx/certs/torspider/backend-key.pem'
        }
        default_config['SQLAlchemy'] = {
            'SQLALCHEMY_ECHO': False,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }
        default_config['WTForms'] = {
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_SECRET_KEY': uuid.uuid4()
        }
        default_config['LOGGING'] = {
            'loglevel': 'INFO',
            'apploglevel': 'CRITICAL'
        }
        default_config['REDIS'] = {
            'REDIS_HOST': '127.0.0.1',
            'REDIS_PORT': 6379
        }
        with open(os.path.join(app.instance_path, 'backend.cfg'), 'w') as config_file:
            default_config.write(config_file)
        print('[+] Default configuration stored in instance/backend.cfg.')
        print('[+] Please edit instance/backend.cfg before running TorSpider backend.')
    else:
        print('[!] The instance/backend.cfg file already exists.  Please delete it to create a fresh one.')


server_config = read_config()


class ProductionConf(object):
    if not server_config:
        make_config()
        server_config = read_config()
    LOG_LEVEL = server_config['LOGGING'].get('loglevel')
    APP_LOG_LEVEL = server_config['LOGGING'].get('apploglevel')
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}:5432/{}".format(server_config['Database'].get('user'),
                                                                     server_config['Database'].get('password'),
                                                                     server_config['Database'].get('host'),
                                                                     server_config['Database'].get('database'))
    SECRET_KEY = server_config['Flask'].get('SECRET_KEY')
    DEBUG = server_config['Flask'].get('DEBUG')
    LISTEN_PORT = server_config['Flask'].get('LISTEN_PORT')
    LISTEN_ADDR = server_config['Flask'].get('LISTEN_ADDR')
    USETLS = server_config['Flask'].get('USETLS')
    CERT_FILE = server_config['Flask'].get('CERT_FILE')
    CERT_KEY_FILE = server_config['Flask'].get('CERT_KEY_FILE')
    WTF_CSRF_ENABLED = server_config['WTForms'].get('SQLALCHEMY_ECHO')
    WTF_CSRF_SECRET_KEY = server_config['WTForms'].get('WTF_CSRF_SECRET_KEY')
    SQLALCHEMY_ECHO = server_config['SQLAlchemy'].get('SQLALCHEMY_ECHO')
    SQLALCHEMY_TRACK_MODIFICATIONS = server_config['SQLAlchemy'].get('SQLALCHEMY_TRACK_MODIFICATIONS')
    REDIS_HOST = server_config['REDIS'].get('REDIS_HOST')
    REDIS_PORT = server_config['REDIS'].get('REDIS_PORT')
    BROKER_URL = environ.get('REDIS_URL', "redis://{host}:{port}/0".format(host=REDIS_HOST, port=str(REDIS_PORT)))
    CELERY_RESULT_BACKEND = BROKER_URL
