#!/usr/bin/env python
from os import environ
import os
import sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app
from app.models import *
import logging
import configparser
from logging.handlers import TimedRotatingFileHandler

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
manager = Manager(app)


class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata


migrate = Migrate(app, DB(db.metadata))
manager.add_command('db', MigrateCommand)


@manager.command
def run():
    '''
    Start the server. 
    '''
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
    '''
    Initialize the database and create all tables.
    '''
    print("[+] Initializing database...")
    print("[+] Creating tables...")
    db.create_all(bind=None)
    print('[+] Done!')


@manager.command
def seed():
    '''
    Seed the database with the initial data required.
    '''
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


if __name__ == '__main__':
    if sys.version_info[0] < 3:
        raise Exception("Please use Python version 3 to run this script.")
    manager.run()
