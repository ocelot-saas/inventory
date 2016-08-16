"""Handlers for HTTP resources for the inventory service."""

import json
import hashlib

import falcon

import inventory.config as config
import inventory.validation as validation
import inventory.schemas as schemas
import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as postgresql
import jsonschema


_metadata = sql.MetaData(schema='inventory')

_org = sql.Table(
    'org', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('time_created', sql.DateTime(timezone=True)))

_org_user = sql.Table(
    'org_user', _metadata,
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('user_id', sql.Integer, unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.PrimaryKeyConstraint('org_id', 'user_id'))

_restaurant = sql.Table(
    'restaurant', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('name', sql.String(100)),
    sql.Column('description', sql.Text()),
    sql.Column('keywords', postgresql.ARRAY(sql.Text)),
    sql.Column('address', sql.Text()),
    sql.Column('opening_hours', postgresql.JSON()))


class OrgResource(object):
    """The collection of organizations."""

    def __init__(self, the_clock, sql_engine):
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)

    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create the organization and restaurant for a user."""

        # right_now = self._the_clock.now()
        # user = self._identity_client.get_user(id_token)

        # try:
        #     org_creation_data_raw = json.load(req.data)
        #     org_creation_data = jsonschema.validate(org_creation_data_raw, schemas.ORG_CREATION_DATA)
        # except:
        #     pass

        # with self._sql_engine.begin() as conn:
        #     org_row = self._fetch_org(conn, user.id)

    def on_get(self, req, resp):
        """Retrieve a particular organization, with info for the restaurant as well."""

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            x = """
SELECT
  o.id,
  o.time_created,
  r.id,
  r.time_created,
  r.name,
  r.description,
  r.keywords,
  r.address,
  r.opening_hours
FROM
  inventory.org_user ou
    JOIN
      inventory.org o
    ON
      ou.org_id = o.id
    JOIN
      inventory.restaurant r
    ON
      ou.org_id = r.id
WHERE
  ou.user_id = @user['id']
"""

        resp.status = falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(req.context['user'])

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
