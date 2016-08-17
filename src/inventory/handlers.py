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

    def __init__(self, org_creation_request_validator, the_clock, sql_engine):
        self._org_creation_request_validator = org_creation_request_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)

    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create the organization and restaurant for a user."""

        right_now = self._the_clock.now()

        try:
            org_creation_request = self._org_creation_request_validator.validate(req.text)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid org creation data',
                description='Invalid data "{}"'.format(req.json)) from e

        with self._sql_engine.begin() as conn:
            try:
                create_org = _org \
                    .insert() \
                    .values(time_created=right_now)

                result = conn.execute(create_org)
                org_id = result.inserted_primary_key[0]
                result.close()

                create_restaurant = _restaurant \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        name=org_creation_request['name'],
                        description=org_creation_request['description'],
                        keywords=org_creation_request['keywords'],
                        address=org_creation_request['address'],
                        opening_hours=org_creation_request['openingHours'])

                result = conn.execute(create_restaurant)
                restaurant_id = result.inserted_primary_key[0]
                result.close()
            except sql.exc.IntegrityError as e:
                raise falcon.HTTPConflict(
                    title='Org already exists',
                    description='Org already exists') from e

        response = {
            'org': {
                'id': org_id,
                'timeCreatedTs': int(right_now.timestamp()),
                'restaurant': {
                    'id': restaurant_id,
                    'timeCreatesTs': int(right_now.timestamp()),
                    'name': org_creation_request['name'],
                    'description': org_creation_request['description'],
                    'keywords': org_creation_request['keywords'],
                    'openingHours': org_creation_request['openingHours']
                }
            }
        }

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_201
        self._cors_response(resp)
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Retrieve a particular organization, with info for the restaurant as well."""

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            fetch_org_and_restaurant = sql.sql \
                .select([
                    _org.c.id.label('org_id'),
                    _org.c.time_created.label('org_time_created'),
                    _restaurant.c.id.label('restaurant_id'),
                    _restaurant.c.time_created.label('restaurant_time_created'),
                    _restaurant.c.name.label('restaurant_name'),
                    _restaurant.c.description.label('restaurant_description'),
                    _restaurant.c.keywords.label('restaurant_keywords'),
                    _restaurant.c.address.label('restaurant_address'),
                    _restaurant.c.opening_hours.label('restaurant_opening_hours'),
                    ]) \
                .select_from(_org_user
                             .join(_org, _org.c.id == _org_user.c.org_id)
                             .join(_restaurant, _restaurant.c.org_id == _org_user.c.org_id)) \
                .where(_org_user.c.user_id == user['id'])

            result = conn.execute(fetch_org_and_restaurant)
            org_and_restaurant_row = result.fetchone()
            result.close()

            if org_and_restaurant_row is None:
                raise falcon.HTTPNotFound(
                    title='Org does not exist',
                    description='Org does not exist')

        response = {
            'org': {
                'id': org_and_restaurant_row['org_id'],
                'timeCreatedTs': int(org_and_restaurant_row['org_time_created'].timestamp()),
                'restaurant': {
                    'id': org_and_restaurant_row['restaurant_id'],
                    'timeCreatesTs':
                        int(org_and_restaurant_row['restaurant_time_created'].timestamp()),
                    'name': org_and_restaurant_row['restaurant_name'],
                    'description': org_and_restaurant_row['restaurant_description'],
                    'keywords': [kw for kw in org_and_restaurant_row['restaurant_keywords']],
                    'openingHours': org_and_restaurant_row['restaurant_opening_hours']
                }
            }
        }

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
