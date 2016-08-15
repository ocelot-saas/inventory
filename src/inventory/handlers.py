"""Handlers for HTTP resources for the inventory service."""

import json
import hashlib

import falcon

import inventory.config as config
import inventory.validation as validation
import inventory.schemas as schemas
import sqlalchemy as sql
import jsonschema


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

        try:
            id_token = self._id_token_header_validator.validate(req.auth)
        except identity.validation.Error:
            raise falcon.HTTPBadRequest(
                title='Invalid Authorization header',
                description='Invalid value "{}" for Authorization header'.format(req.auth))        

        right_now = self._the_clock.now()
        user = self._identity_client.get_user(id_token)

        try:
            org_creation_data_raw = json.load(req.data)
            org_creation_data = jsonschema.validate(org_creation_data_raw, schemas.ORG_CREATION_DATA)
        except:
            pass

        with self._sql_engine.begin() as conn:
            org_row = self._fetch_org(conn, user.id)

    def on_get(self, req, resp):
        """Retrieve a particular organization."""

        resp.status = falcon.HTTP_200
        self._cors_response(resp)
        resp.body = 'A-OK'

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
