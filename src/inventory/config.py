import multiprocessing
import os


# Application config.
ENV = os.getenv('ENV')
ADDRESS = os.getenv('ADDRESS')
PORT = os.getenv('PORT')
IDENTITY_SERVICE_DOMAIN = os.getenv('IDENTITY_SERVICE_DOMAIN')
MIGRATIONS_PATH = os.getenv('MIGRATIONS_PATH')
DATABASE_URL = os.getenv('DATABASE_URL')
CLIENTS = os.getenv('CLIENTS').split(',')

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
