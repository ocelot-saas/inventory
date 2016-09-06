"""Handlers for HTTP resources for the inventory service."""

import json
import hashlib

import falcon
import slugify

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
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.Column('keywords', postgresql.ARRAY(sql.Text)),
    sql.Column('address', sql.Text()),
    sql.Column('opening_hours', postgresql.JSON()),
    sql.Column('image_set', postgresql.JSON()))

_platforms_website = sql.Table(
    'platforms_website', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('subdomain', sql.Text()))

_platforms_callcenter = sql.Table(
    'platforms_callcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('phone_number', sql.Text()))

_platforms_emailcenter = sql.Table(
    'platforms_emailcenter', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id), unique=True),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('email_name', sql.Text()))

_RESTAURANT_E2I_FIELD_NAMES = {
    'name': 'name',
    'description': 'description',
    'keywords': 'keywords',
    'address': 'address',
    'openingHours': 'opening_hours',
    'imageSet': 'image_set'
}

_PLATFORMS_WEBSITE_E2I_FIELD_NAMES = {
    'subdomain': 'subdomain'
}


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
        
        self._cors_response(resp)

        right_now = self._the_clock.now()
        user = req.context['user']

        try:
            org_creation_request_raw = req.stream.read().decode('utf-8')
            org_creation_request = \
                self._org_creation_request_validator.validate(org_creation_request_raw)
        except validation.Error as e:
            raise e
            raise falcon.HTTPBadRequest(
                title='Invalid org creation data',
                description='Invalid data "{}"'.format(org_creation_request_raw)) from e

        with self._sql_engine.begin() as conn:
            try:
                create_org = _org \
                    .insert() \
                    .values(time_created=right_now)

                result = conn.execute(create_org)
                org_id = result.inserted_primary_key[0]
                result.close()

                create_org_user = _org_user \
                    .insert() \
                    .values(org_id=org_id, user_id=user['id'], time_created=right_now)

                result = conn.execute(create_org_user)
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
                        opening_hours=org_creation_request['openingHours'],
                        image_set=org_creation_request['imageSet'])

                conn.execute(create_restaurant).close()

                # Create basic plaforms with basic info

                create_platforms_website = _platforms_website \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        subdomain=slugify.slugify(org_creation_request['name']))

                conn.execute(create_platforms_website).close()

                create_platforms_callcenter = _platforms_callcenter \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        phone_number='')

                conn.execute(create_platforms_callcenter).close()

                create_platforms_emailcenter = _platforms_emailcenter \
                    .insert() \
                    .values(
                        org_id=org_id,
                        time_created=right_now,
                        email_name='contact')

                conn.execute(create_platforms_emailcenter).close()
            except sql.exc.IntegrityError as e:
                raise falcon.HTTPConflict(
                    title='Org already exists',
                    description='Org already exists') from e

        response = {
            'org': {
                'id': org_id,
                'timeCreatedTs': int(right_now.timestamp())
            }
        }

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Retrieve a particular organization, with info for the restaurant as well."""

        self._cors_response(resp)

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            fetch_org = sql.sql \
                .select([
                    _org.c.id,
                    _org.c.time_created
                    ]) \
                .select_from(_org_user
                             .join(_org, _org.c.id == _org_user.c.org_id)) \
                .where(_org_user.c.user_id == user['id'])

            result = conn.execute(fetch_org)
            org_row = result.fetchone()
            result.close()

            if org_row is None:
                raise falcon.HTTPNotFound(
                    title='Org does not exist',
                    description='Org does not exist')

        response = {
            'org': {
                'id': org_row['id'],
                'timeCreatedTs': int(org_row['time_created'].timestamp())
            }
        }

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class RestaurantResource(object):
    """The restaurant for an organization."""

    def __init__(self, restaurant_update_request_validator, the_clock, sql_engine):
        self._restaurant_update_request_validator = restaurant_update_request_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the restaurant for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            restaurant_row = self._fetch_restaurant(conn, user['id'])

            if restaurant_row is None:
                raise falcon.HTTPNotFound(
                    title='Restaurant does not exist',
                    description='Restaurant does not exist')

        response = {
            'restaurant': {
                'id': restaurant_row['id'],
                'timeCreatedTs': int(restaurant_row['time_created'].timestamp()),
                'name': restaurant_row['name'],
                'description': restaurant_row['description'],
                'keywords': [kw for kw in restaurant_row['keywords']],
                'address': restaurant_row['address'],
                'openingHours': restaurant_row['opening_hours'],
                'imageSet': restaurant_row['image_set']
            }
        }

        jsonschema.validate(response, schemas.RESTAURANT_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the restaurant for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            restaurant_update_request_raw = req.stream.read().decode('utf-8')
            restaurant_update_request = \
                self._restaurant_update_request_validator.validate(restaurant_update_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid restaurant update data',
                description='Invalid data "{}"'.format(restaurant_update_request_raw)) from e

        with self._sql_engine.begin() as conn:
            restaurant_row = self._fetch_restaurant(conn, user['id'])

            if restaurant_row is None:
                raise falcon.HTTPNotFound(
                    title='Restaurant does not exist',
                    description='Restaurant does not exist')

            properties_to_update = dict(
                (_RESTAURANT_E2I_FIELD_NAMES[k], v) for (k, v) in restaurant_update_request.items())

            update_restaurant = _restaurant \
                .update() \
                .where(_restaurant.c.id == restaurant_row['id']) \
                .values(**properties_to_update)

            result = conn.execute(update_restaurant)
            result.close()

        response = {
            'restaurant': {
                'id': restaurant_row['id'],
                'timeCreatedTs': int(restaurant_row['time_created'].timestamp()),
                'name': restaurant_row['name'],
                'description': restaurant_row['description'],
                'keywords': [kw for kw in restaurant_row['keywords']],
                'address': restaurant_row['address'],
                'openingHours': restaurant_row['opening_hours'],
                'imageSet': restaurant_row['image_set']
            }
        }
        
        response['restaurant'].update(restaurant_update_request)

        jsonschema.validate(response, schemas.RESTAURANT_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')

    def _fetch_restaurant(self, conn, user_id):
        fetch_restaurant = sql.sql \
            .select([
                _restaurant.c.id,
                _restaurant.c.time_created,
                _restaurant.c.name,
                _restaurant.c.description,
                _restaurant.c.keywords,
                _restaurant.c.address,
                _restaurant.c.opening_hours,
                _restaurant.c.image_set,
                ]) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_restaurant, _restaurant.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_restaurant)
        restaurant_row = result.fetchone()
        result.close()

        return restaurant_row


class PlatformsWebsiteResource(object):
    """The website platform for an organization."""

    def __init__(self, platforms_website_update_request_validator, the_clock, sql_engine):
        self._platforms_website_update_request_validator = \
            platforms_website_update_request_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the website platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            platforms_website_row = self._fetch_platforms_website(conn, user['id'])

            if platforms_website_row is None:
                raise falcon.HTTPNotFound(
                    title='Website does not exist',
                    description='Website does not exist')

        response = {
            'platformsWebsite': {
                'id': platforms_website_row['id'],
                'timeCreatedTs': int(platforms_website_row['time_created'].timestamp()),
                'subdomain': platforms_website_row['subdomain']
            }
        }

        jsonschema.validate(response, schemas.PLATFORMS_WEBSITE_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the website platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            platforms_website_update_request_raw = req.stream.read().decode('utf-8')
            platforms_website_update_request = \
                self._platforms_website_update_request_validator.validate(
                    platforms_website_update_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid website update data',
                description='Invalid data "{}"'.format(platforms_website_update_request_raw)) from e

        with self._sql_engine.begin() as conn:
            platforms_website_row = self._fetch_platforms_website(conn, user['id'])

            if platforms_website_row is None:
                raise falcon.HTTPNotFound(
                    title='Website does not exist',
                    description='Website does not exist')

            properties_to_update = dict(
                (_PLATFORMS_WEBSITE_E2I_FIELD_NAMES[k], v) for (k, v)
                in platforms_website_update_request.items())

            update_platforms_website = _platforms_website \
                .update() \
                .where(_platforms_website.c.id == platforms_website_row['id']) \
                .values(**properties_to_update)

            result = conn.execute(update_platforms_website)
            result.close()

        response = {
            'platformsWebsite': {
                'id': platforms_website_row['id'],
                'timeCreatedTs': int(platforms_website_row['time_created'].timestamp()),
                'subdomain': platforms_website_row['subdomain']
            }
        }
        
        response['platformsWebsite'].update(platforms_website_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_WEBSITE_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')

    def _fetch_platforms_website(self, conn, user_id):
        fetch_platforms_website = sql.sql \
            .select([
                _platforms_website.c.id,
                _platforms_website.c.time_created,
                _platforms_website.c.subdomain
                ]) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_website,
                               _platforms_website.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_platforms_website)
        platforms_website_row = result.fetchone()
        result.close()

        return platforms_website_row
