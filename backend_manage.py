#! /usr/bin/env python3
from os import environ
import os
import sys
import uuid
import hashlib
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import or_
from app import app
from app.models import *
import logging
from logging.handlers import TimedRotatingFileHandler

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
manager = Manager(app)


class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata


migrate = Migrate(app, DB(db.metadata))
manager.add_command('db', MigrateCommand)


def create_api_key():
    """
    Create an API key from a random string
    :return: A sha1 hash
    """
    return hashlib.sha1(uuid.uuid4().hex.encode('utf-8')).hexdigest()


def create_unique_id():
    """
    Create a unique ID that is used by the nodes
    :return: A unqiue 16 character ID.
    """
    return uuid.uuid4().hex[:16]


@manager.command
def run():
    """
    Start the server. 
    """
    if not os.path.isdir(os.path.join(script_dir, 'logs')):
        os.makedirs(os.path.join(script_dir, 'logs'))
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = TimedRotatingFileHandler(os.path.join(script_dir, 'logs', 'TorSpider-Backend.log'), when='midnight',
                                       interval=1)
    handler.setLevel(app.config['LOG_LEVEL'])
    handler.setFormatter(formatter)
    log = logging.getLogger('werkzeug')
    log.setLevel(app.config['LOG_LEVEL'])
    log.addHandler(handler)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['APP_LOG_LEVEL'])
    port = int(environ.get('PORT', app.config['LISTEN_PORT']))
    addr = environ.get('LISTEN_ADDR', app.config['LISTEN_ADDR'])
    if app.config['USETLS']:
        context = (os.path.join(script_dir, 'certs', 'server.crt'), os.path.join(script_dir, 'certs', 'server.key'))
        app.run(host=addr, port=port, threaded=True, ssl_context=context)
    else:
        app.run(host=addr, port=port, threaded=True)


@manager.command
def initdb():
    """
    Initialize the database and create all tables.
    """
    print("[+] Initializing database...")
    print("[+] Creating tables...")
    db.create_all(bind=None)
    print('[+] Done!')


@manager.command
def create_frontend_node():
    """
    Create the node for the front-end that is required for API communications.
    """
    check_exists = Nodes.query.filter(Nodes.owner == 'FrontEnd').first()
    if check_exists:
        print('[-] There is already a frontend node in the database.')
        sys.exit(0)
    newnode = Nodes()
    newnode.owner = 'FrontEnd'
    newnode.api_key = create_api_key()
    newnode.unique_id = create_unique_id()
    newnode.active = True
    check_dup = True
    # Keep trying to create unique keys until they don't exist in the db.  This should really only run once.
    # Collisions should be very low.
    while check_dup:
        check_dup = Nodes.query.filter(
            or_(Nodes.unique_id == newnode.unique_id, Nodes.api_key == newnode.api_key)).first()
    try:
        db.session.add(newnode)
        db.session.commit()
        print('[+] Node created.')
        print('[+] Node id: {}'.format(newnode.unique_id))
        print('[+] API Key: {}'.format(newnode.api_key))
        print('[+] You can also view this node\'s info in the Frontend UI.')
        return True
    except Exception as e:
        print('[!] Failed to create Node.  Please try again.')
        db.session.rollback()
        raise e


@manager.command
def seed():
    """
    Seed the database with the initial data required.
    """
    # We'll populate the database with some default values. These
    # pages are darknet indexes, so they should be a good starting
    # point.
    print('[+] Splinkle sprinkle!!!')
    # TODO: Clean this up with relationships
    seeds = [
        # The Uncensored Hidden Wiki
        # http://zqktlwi4fecvo6ri.onion/wiki/Main_Page
        (Onions(domain='zqktlwi4fecvo6ri.onion'),
         Urls(domain='zqktlwi4fecvo6ri.onion', url='http://zqktlwi4fecvo6ri.onion/wiki/Main_Page'),
         Pages(domain='zqktlwi4fecvo6ri.onion', url='http://zqktlwi4fecvo6ri.onion/wiki/Main_Page')),
        # OnionDir
        # http://auutwvpt2zktxwng.onion/index.php
        (Onions(domain='auutwvpt2zktxwng.onion'),
         Urls(domain='auutwvpt2zktxwng.onion', url='http://auutwvpt2zktxwng.onion/index.php'),
         Pages(domain='auutwvpt2zktxwng.onion', url='http://auutwvpt2zktxwng.onion/index.php')),
        # Wiki links
        # http://wikilink77h7lrbi.onion/
        (Onions(domain='wikilink77h7lrbi.onion'),
         Urls(domain='wikilink77h7lrbi.onion', url='http://wikilink77h7lrbi.onion/'),
         Pages(domain='wikilink77h7lrbi.onion', url='http://wikilink77h7lrbi.onion/')),
        # Deep Web Links
        # http://wiki5kauuihowqi5.onion/
        (Onions(domain='wiki5kauuihowqi5.onion'),
         Urls(domain='wiki5kauuihowqi5.onion', url='http://wiki5kauuihowqi5.onion/'),
         Pages(domain='wiki5kauuihowqi5.onion', url='http://wiki5kauuihowqi5.onion/')),
        # OnionDir Deep Web Directory
        # http://dirnxxdraygbifgc.onion/
        (Onions(domain='dirnxxdraygbifgc.onion'),
         Urls(domain='dirnxxdraygbifgc.onion', url='http://dirnxxdraygbifgc.onion/'),
         Pages(domain='dirnxxdraygbifgc.onion', url='http://dirnxxdraygbifgc.onion/')),
        # The Onion Crate
        # http://7cbqhjnlkivmigxf.onion/
        (Onions(domain='7cbqhjnlkivmigxf.onion'),
         Urls(domain='7cbqhjnlkivmigxf.onion', url='http://7cbqhjnlkivmigxf.onion/'),
         Pages(domain='7cbqhjnlkivmigxf.onion', url='http://7cbqhjnlkivmigxf.onion/')),
        # Fresh Onions
        # http://zlal32teyptf4tvi.onion/
        (Onions(domain='zlal32teyptf4tvi.onion'),
         Urls(domain='zlal32teyptf4tvi.onion', url='http://zlal32teyptf4tvi.onion/'),
         Pages(domain='zlal32teyptf4tvi.onion', url='http://zlal32teyptf4tvi.onion/'))
    ]

    for seed in seeds:
        # Sprinkle!!!!
        db.session.add(seed[0])
        db.session.commit()
        db.session.add(seed[1])
        db.session.commit()
        db.session.add(seed[2])
        db.session.commit()

    print('[+] Done.')


@manager.command
def list_routes():
    import urllib.parse
    from flask import url_for
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


if __name__ == '__main__':
    if sys.version_info[0] < 3:
        raise Exception("Please use Python version 3 to run this script.")
    manager.run()
