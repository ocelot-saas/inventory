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

        right_now = self._the_clock.now()

        try:
            org_creation_data = self._org_creation_data_validator.validate(req.json)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid org creation data',
                description='Invalid data "{}"'.format(req.json)) from e

        with self._sql_engine.begin() as conn:
            org_and_restaurant_row = self._fetch_org_and_restaurant(conn, user['id'])

            if org_and_restaurant_row is None:
                is_new = True

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
                        name=org_creation_data['name'],
                        description=org_creation_data['description'],
                        keywords=org_creation_data['keywords'],
                        address=org_creation_data['address'],
                        opening_hours=org_creation_data['openingHours'])

                result = conn.execute(create_restaurant)
                restaurant_id = result.inserted_primary_key[0]
                result.close()
            else:
                is_new = False

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

        resp.status = falcon.HTTP_201 if is_new else falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(response)        

    def on_get(self, req, resp):
        """Retrieve a particular organization, with info for the restaurant as well."""

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            org_and_restaurant_row = self._fetch_org_and_restaurant(conn, user['id'])

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

        resp.status = falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(response)

    def _fetch_org_and_restaurant(self, conn, user_id):
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
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_org_and_restaurant)
        org_and_restaurant_row = result.fetchone()
        result.close()

        return org_and_restaurant_row

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
