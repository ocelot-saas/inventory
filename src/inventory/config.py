import multiprocessing
import os


def get_environ():
    environ = os.environ['ENVIRON']
    if environ in ('LOCAL', 'STAGING', 'LIVE'):
        return environ
    else:
        raise Exception('Invalid ENVIRON "{}"'.format(environ))


def by_environ(**kwargs):
    def eval_environ(val):
        if hasattr(val, '__call__'):
            return val()
        else:
            return val

    environ = get_environ()
    if environ == 'LOCAL':
        return eval_environ(kwargs['local'])
    elif environ == 'STAGING':
        return eval_environ(kwargs['staging'])
    elif environ == 'LIVE':
        return eval_environ(kwargs['live'])
    else:
        raise Exception('Invalid application state')


def local_postgres_uri():
    return 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=os.environ['OCELOT_POSTGRES_ENV_POSTGRES_USER'],
        password=os.environ['OCELOT_POSTGRES_ENV_POSTGRES_PASSWORD'],
        host=os.environ['OCELOT_POSTGRES_PORT_5432_TCP_ADDR'],
        port=os.environ['OCELOT_POSTGRES_PORT_5432_TCP_PORT'],
        database=os.environ['OCELOT_POSTGRES_ENV_POSTGRES_DB'])


# Application config.
ENVIRON = get_environ()
ADDRESS = '0.0.0.0'
PORT = by_environ(
  local='10000',
  staging=lambda: os.environ['PORT'],
  live=lambda: os.environ['PORT'])
MIGRATIONS_PATH = by_environ(
    local='/ocelot/pack/inventory/migrations',
    staging='migrations',
    live='migrations')
DATABASE_URL = by_environ(
    local=local_postgres_uri,
    staging=lambda: os.environ['DATABASE_URL'],
    live=lambda: os.environ['DATABASE_URL'])
CLIENTS = by_environ(
    local=['localhost:10000'],
    staging=['bucketeer-0657d779-f6ef-4fbe-8f88-5dfe9e308bbb.s3.amazonaws.com'],
    live=[])

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
