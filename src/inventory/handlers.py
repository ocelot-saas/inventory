"""Handlers for HTTP resources for the inventory service."""

import json
import hashlib

import falcon
import jsonschema
import slugify
import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as postgresql

import inventory.config as config
import inventory.model as model
import inventory.validation as validation
import inventory.schemas as schemas


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

_menu_section = sql.Table(
    'menu_section', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('org_id', sql.Integer, sql.ForeignKey(_org.c.id)),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.UniqueConstraint('id', 'org_id', name='menu_section_uk_id_org_id'))

_menu_item = sql.Table(
    'menu_item', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('section_id', sql.Integer),
    sql.Column('org_id', sql.Integer),
    sql.Column('time_created', sql.DateTime(timezone=True)),
    sql.Column('time_archived', sql.DateTime(timezone=True), nullable=True),
    sql.Column('name', sql.Text()),
    sql.Column('description', sql.Text()),
    sql.Column('keywords', postgresql.ARRAY(sql.Text)),
    sql.Column('ingredients', postgresql.JSON()),
    sql.Column('image_set', postgresql.JSON()),
    sql.ForeignKeyConstraint(['section_id', 'org_id'], [_menu_section.c.id, _menu_section.c.org_id]),
    sql.UniqueConstraint('id', 'section_id', 'org_id'))

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
    

_PLATFORMS_WEBSITE_E2I_FIELD_NAMES = {
    'subdomain': 'subdomain'
}


_PLATFORMS_CALLCENTER_E2I_FIELD_NAMES = {
    'phoneNumber': 'phone_number'
}


_PLATFORMS_EMAILCENTER_E2I_FIELD_NAMES = {
    'emailName': 'email_name'
}


class OrgResource(object):
    """The collection of organizations."""

    def __init__(self, org_creation_request_validator, model):
        self._org_creation_request_validator = org_creation_request_validator
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)

    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create the organization and restaurant for a user."""
        
        self._cors_response(resp)

        user = req.context['user']

        try:
            org_creation_request_raw = req.stream.read().decode('utf-8')
            org_creation_request = \
                self._org_creation_request_validator.validate(org_creation_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid org creation data',
                description='Invalid data "{}"'.format(org_creation_request_raw)) from e

        try:
            org = self._model.create_org(
                user['id'], org_creation_request['name'], org_creation_request['description'],
                org_creation_request['keywords'], org_creation_request['address'],
                org_creation_request['openingHours'], org_creation_request['imageSet'])
        except model.OrgAlreadyExistsError as e:
            raise falcon.HTTPConflict(
                title='Org already exists',
                description='Org already exists') from e

        response = {'org': org}

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Retrieve a particular organization, with info for the restaurant as well."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            org = self._model.get_org(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist') from e

        response = {'org': org}

        jsonschema.validate(response, schemas.ORG_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class RestaurantResource(object):
    """The restaurant for an organization."""

    def __init__(self, restaurant_update_request_validator, model):
        self._restaurant_update_request_validator = restaurant_update_request_validator
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the restaurant for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            restaurant = self._model.get_restaurant(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Restaurant does not exist',
                description='Restaurant does not exist')

        response = {'restaurant': restaurant}

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

        try:
            restaurant = self._model.update_restaurant(user['id'], **restaurant_update_request)
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Restaurant does not exist',
                description='Restaurant does not exist')

        response = {'restaurant': restaurant}

        jsonschema.validate(response, schemas.RESTAURANT_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class MenuSectionsResource(object):
    """All the sections in the menu for an organization."""

    def __init__(self, menu_sections_creation_request_validator, model):
        self._menu_sections_creation_request_validator = menu_sections_creation_request_validator
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create a menu section."""

        self._cors_response(resp)

        right_now = self._the_clock.now()
        user = req.context['user']

        try:
            menu_sections_creation_request_raw = req.stream.read().decode('utf-8')
            menu_sections_creation_request = \
                self._menu_sections_creation_request_validator.validate(
                    menu_sections_creation_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid menu section creation data',
                description='Invalid data "{}"'.format(menu_sections_creation_request_raw)) from e

        try:
            menu_section = self._model.create_menu_section(
                user['id'], menu_sections_creation_request['name'],
                menu_sections_creation_request['description'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist')

        response = {'menuSections': [menu_section]}

        jsonschema.validate(response, schemas.MENU_SECTIONS_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Get a particular menu section."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            menu_sections = self._model.get_all_menu_sections(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist')

        response = {'menuSections': menu_sections}

        jsonschema.validate(response, schemas.MENU_SECTIONS_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class MenuSectionResource(object):
    """A section in the menu for an organization."""

    def __init__(self, model):
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp, section_id):
        """Get a particular menu section."""

        self._cors_response(resp)

        section_id = self._validate_section_id(section_id)
        user = req.context['user']

        try:
            menu_section = self._model.get_menu_section(user['id'], section_id)
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist')
        except model.SectionDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Section does not exist',
                description='Section does not exist')

        response = {'menuSection': menuSection}

        jsonschema.validate(response, schemas.MENU_SECTION_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp, section_id):
        """Update a particular menu section."""

        self._cors_response(resp)
        
        section_id = self._validate_section_id(section_id)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuSectionResource'

    def on_delete(self, req, resp, section_id):
        """Remove a particular menu section."""

        self._cors_response(resp)

        section_id = self._validate_section_id(section_id)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuSectionResource'


    @staticmethod
    def _validate_section_id(section_id):
        try:
            return int(section_id)
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title='Invalid section id',
                description='Invalid section id "{}"'.format(section_id)) from e

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT, DELETE')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class MenuItemsResource(object):
    """All the items in the menu for an organization."""

    def __init__(self, model):
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create a menu item."""

        self._cors_response(resp)
        user = req.context['user']

        resp.status = falcon.HTTP_201
        resp.body = 'Hello MenuItemsResource'        

    def on_get(self, req, resp):
        """Get a particular menu item."""

        self._cors_response(resp)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemsResource'

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class MenuItemResource(object):
    """A item in the menu for an organization."""

    def __init__(self, model):
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp, item_id):
        """Get a particular menu item."""

        self._cors_response(resp)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'

    def on_put(self, req, resp, item_id):
        """Update a particular menu item."""

        self._cors_response(resp)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'

    def on_delete(self, req, resp, item_id):
        """Remove a particular menu item."""

        self._cors_response(resp)
        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT, DELETE')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class PlatformsWebsiteResource(object):
    """The website platform for an organization."""

    def __init__(self, platforms_website_update_request_validator, model):
        self._platforms_website_update_request_validator = \
            platforms_website_update_request_validator
        self._model = model

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the website platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            platforms_website = self._model.get_platforms_website(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Website does not exist',
                description='Website does not exist') from e

        response = {'platformsWebsite': platforms_website}

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

        try:
            platforms_website = self._model.update_platforms_website(user['id'], **platforms_website_update_request)
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Website does not exist',
                description='Website does not exist')

        response = {'platformsWebsite': platforms_website}
        
        response['platformsWebsite'].update(platforms_website_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_WEBSITE_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')


class PlatformsCallcenterResource(object):
    """The callcenter platform for an organization."""

    def __init__(self, platforms_callcenter_update_request_validator, the_clock, sql_engine):
        self._platforms_callcenter_update_request_validator = \
            platforms_callcenter_update_request_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the callcenter platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            platforms_callcenter_row = self._fetch_platforms_callcenter(conn, user['id'])

            if platforms_callcenter_row is None:
                raise falcon.HTTPNotFound(
                    title='Callcenter does not exist',
                    description='Callcenter does not exist')

        response = {
            'platformsCallcenter': {
                'id': platforms_callcenter_row['id'],
                'timeCreatedTs': int(platforms_callcenter_row['time_created'].timestamp()),
                'phoneNumber': platforms_callcenter_row['phone_number']
            }
        }

        jsonschema.validate(response, schemas.PLATFORMS_CALLCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the callcenter platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            platforms_callcenter_update_request_raw = req.stream.read().decode('utf-8')
            platforms_callcenter_update_request = \
                self._platforms_callcenter_update_request_validator.validate(
                    platforms_callcenter_update_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid callcenter update data',
                description='Invalid data "{}"'.format(platforms_callcenter_update_request_raw)) from e

        with self._sql_engine.begin() as conn:
            platforms_callcenter_row = self._fetch_platforms_callcenter(conn, user['id'])

            if platforms_callcenter_row is None:
                raise falcon.HTTPNotFound(
                    title='Callcenter does not exist',
                    description='Callcenter does not exist')

            properties_to_update = dict(
                (_PLATFORMS_CALLCENTER_E2I_FIELD_NAMES[k], v) for (k, v)
                in platforms_callcenter_update_request.items())

            update_platforms_callcenter = _platforms_callcenter \
                .update() \
                .where(_platforms_callcenter.c.id == platforms_callcenter_row['id']) \
                .values(**properties_to_update)

            result = conn.execute(update_platforms_callcenter)
            result.close()

        response = {
            'platformsCallcenter': {
                'id': platforms_callcenter_row['id'],
                'timeCreatedTs': int(platforms_callcenter_row['time_created'].timestamp()),
                'phoneNumber': platforms_callcenter_row['phone_number']
            }
        }
        
        response['platformsCallcenter'].update(platforms_callcenter_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_CALLCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')

    def _fetch_platforms_callcenter(self, conn, user_id):
        fetch_platforms_callcenter = sql.sql \
            .select([
                _platforms_callcenter.c.id,
                _platforms_callcenter.c.time_created,
                _platforms_callcenter.c.phone_number
                ]) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_callcenter,
                               _platforms_callcenter.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_platforms_callcenter)
        platforms_callcenter_row = result.fetchone()
        result.close()

        return platforms_callcenter_row


class PlatformsEmailcenterResource(object):
    """The emailcenter platform for an organization."""

    def __init__(self, platforms_emailcenter_update_request_validator, the_clock, sql_engine):
        self._platforms_emailcenter_update_request_validator = \
            platforms_emailcenter_update_request_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)
        
    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_get(self, req, resp):
        """Get the emailcenter platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        with self._sql_engine.begin() as conn:
            platforms_emailcenter_row = self._fetch_platforms_emailcenter(conn, user['id'])

            if platforms_emailcenter_row is None:
                raise falcon.HTTPNotFound(
                    title='Emailcenter does not exist',
                    description='Emailcenter does not exist')

        response = {
            'platformsEmailcenter': {
                'id': platforms_emailcenter_row['id'],
                'timeCreatedTs': int(platforms_emailcenter_row['time_created'].timestamp()),
                'emailName': platforms_emailcenter_row['email_name']
            }
        }

        jsonschema.validate(response, schemas.PLATFORMS_EMAILCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the emailcenter platform for an organization."""

        self._cors_response(resp)

        user = req.context['user']

        try:
            platforms_emailcenter_update_request_raw = req.stream.read().decode('utf-8')
            platforms_emailcenter_update_request = \
                self._platforms_emailcenter_update_request_validator.validate(
                    platforms_emailcenter_update_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid emailcenter update data',
                description='Invalid data "{}"'.format(platforms_emailcenter_update_request_raw)) from e

        with self._sql_engine.begin() as conn:
            platforms_emailcenter_row = self._fetch_platforms_emailcenter(conn, user['id'])

            if platforms_emailcenter_row is None:
                raise falcon.HTTPNotFound(
                    title='Emailcenter does not exist',
                    description='Emailcenter does not exist')

            properties_to_update = dict(
                (_PLATFORMS_EMAILCENTER_E2I_FIELD_NAMES[k], v) for (k, v)
                in platforms_emailcenter_update_request.items())

            update_platforms_emailcenter = _platforms_emailcenter \
                .update() \
                .where(_platforms_emailcenter.c.id == platforms_emailcenter_row['id']) \
                .values(**properties_to_update)

            result = conn.execute(update_platforms_emailcenter)
            result.close()

        response = {
            'platformsEmailcenter': {
                'id': platforms_emailcenter_row['id'],
                'timeCreatedTs': int(platforms_emailcenter_row['time_created'].timestamp()),
                'emailName': platforms_emailcenter_row['email_name']
            }
        }
        
        response['platformsEmailcenter'].update(platforms_emailcenter_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_EMAILCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, GET, PUT')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')

    def _fetch_platforms_emailcenter(self, conn, user_id):
        fetch_platforms_emailcenter = sql.sql \
            .select([
                _platforms_emailcenter.c.id,
                _platforms_emailcenter.c.time_created,
                _platforms_emailcenter.c.email_name
                ]) \
            .select_from(_org_user
                         .join(_org, _org.c.id == _org_user.c.org_id)
                         .join(_platforms_emailcenter,
                               _platforms_emailcenter.c.org_id == _org_user.c.org_id)) \
            .where(_org_user.c.user_id == user_id)

        result = conn.execute(fetch_platforms_emailcenter)
        platforms_emailcenter_row = result.fetchone()
        result.close()

        return platforms_emailcenter_row
