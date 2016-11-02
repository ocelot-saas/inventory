import json
import multiprocessing
import os


# Application config.
ENV = os.getenv('ENV')
ADDRESS = os.getenv('ADDRESS')
PORT = os.getenv('PORT')
IDENTITY_SERVICE_DOMAIN = os.getenv('IDENTITY_SERVICE_DOMAIN')
MIGRATIONS_PATH = os.getenv('MIGRATIONS_PATH')
DATABASE_URL = os.getenv('DATABASE_URL')
CLIENTS = ['http://{}'.format(c) for c in os.getenv('CLIENTS').split(',')]

if ENV == 'LOCAL':
    with open('/ocelot/var/secrets.json') as f:
        secrets = json.load(f)
else:
    pass

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
