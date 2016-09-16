"""Handlers for HTTP resources for the inventory service."""

import json
import hashlib

import falcon
import jsonschema

import inventory.model as model
import inventory.validation as validation
import inventory.schemas as schemas


class OrgResource(object):
    """The collection of organizations."""

    def __init__(self, org_creation_request_validator, model):
        self._org_creation_request_validator = org_creation_request_validator
        self._model = model

    def on_post(self, req, resp):
        """Create the organization and restaurant for a user."""
        
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


class RestaurantResource(object):
    """The restaurant for an organization."""

    def __init__(self, restaurant_update_request_validator, model):
        self._restaurant_update_request_validator = restaurant_update_request_validator
        self._model = model

    def on_get(self, req, resp):
        """Get the restaurant for an organization."""

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


class MenuSectionsResource(object):
    """All the sections in the menu for an organization."""

    def __init__(self, menu_sections_creation_request_validator, model):
        self._menu_sections_creation_request_validator = menu_sections_creation_request_validator
        self._model = model

    def on_post(self, req, resp):
        """Create a menu section."""

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


class MenuSectionResource(object):
    """A section in the menu for an organization."""

    def __init__(self, menu_section_update_request_validator, model):
        self._menu_section_update_request_validator = menu_section_update_request_validator
        self._model = model

    def on_get(self, req, resp, section_id):
        """Get a particular menu section."""

        section_id = self.validate_section_id(section_id)
        user = req.context['user']

        try:
            menu_section = self._model.get_menu_section(user['id'], section_id)
        except model.MenuSectionDoesNotExistError as e:
            raise falcon.HTTPNotFound(
                title='Section does not exist',
                description='Section does not exist')

        response = {'menuSection': menu_section}

        jsonschema.validate(response, schemas.MENU_SECTION_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp, section_id):
        """Update a particular menu section."""

        section_id = self.validate_section_id(section_id)
        user = req.context['user']

        try:
            menu_section_update_request_raw = req.stream.read().decode('utf-8')
            menu_section_update_request = \
                self._menu_section_update_request_validator.validate(
                    menu_section_update_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid menu section update data',
                description='Invalid data "{}"'.format(menu_section_update_request_raw)) from e

        try:
            menu_section = self._model.update_menu_section(
                user['id'], section_id, **menu_section_update_request)
        except model.MenuSectionDoesNotExistError as e:
            raise falcon.HTTPNotFound(
                title='Section does not exist',
                description='Section does not exist')

        response = {'menuSection': menu_section}

        jsonschema.validate(response, schemas.MENU_SECTION_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_delete(self, req, resp, section_id):
        """Remove a particular menu section."""

        section_id = self._validate_section_id(section_id)
        user = req.context['user']

        try:
            self._model.delete_menu_section(user['id'], section_id)
        except model.MenuSectionDoesNotExistError as e:
            raise falcon.HTTPNotFound(
                title='Section does not exist',
                description='Section does not exist')            

        resp.status = falcon.HTTP_204

    @staticmethod
    def validate_section_id(section_id):
        try:
            return int(section_id)
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title='Invalid section id',
                description='Invalid section id "{}"'.format(section_id)) from e


class MenuItemsResource(object):
    """All the items in the menu for an organization."""

    def __init__(self, menu_items_creation_request_validator, model):
        self._menu_items_creation_request_validator = menu_items_creation_request_validator
        self._model = model

    def on_post(self, req, resp):
        """Create a menu item."""

        user = req.context['user']

        try:
            menu_items_creation_request_raw = req.stream.read().decode('utf-8')
            menu_items_creation_request = \
                self._menu_items_creation_request_validator.validate(
                    menu_items_creation_request_raw)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid menu item creation data',
                description='Invalid data "{}"'.format(menu_items_creation_request_raw)) from e

        try:
            menu_item = self._model.create_menu_item(
                user['id'], menu_items_creation_request['sectionId'], menu_items_creation_request['name'],
                menu_items_creation_request['description'], menu_items_creation_request['keywords'],
                menu_items_creation_request['ingredients'], menu_items_creation_request['imageSet'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist')

        response = {'menuItems': [menu_item]}

        jsonschema.validate(response, schemas.MENU_ITEMS_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Get a particular menu item."""

        user = req.context['user']

        try:
            menu_items = self._model.get_all_menu_items(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Org does not exist',
                description='Org does not exist')

        response = {'menuItems': menu_items}

        jsonschema.validate(response, schemas.MENU_ITEMS_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


class MenuItemResource(object):
    """A item in the menu for an organization."""

    def __init__(self, model):
        self._model = model

    def on_get(self, req, resp, item_id):
        """Get a particular menu item."""

        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'

    def on_put(self, req, resp, item_id):
        """Update a particular menu item."""

        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'

    def on_delete(self, req, resp, item_id):
        """Remove a particular menu item."""

        user = req.context['user']

        resp.status = falcon.HTTP_200
        resp.body = 'Hello MenuItemResource'


class PlatformsWebsiteResource(object):
    """The website platform for an organization."""

    def __init__(self, platforms_website_update_request_validator, model):
        self._platforms_website_update_request_validator = \
            platforms_website_update_request_validator
        self._model = model

    def on_get(self, req, resp):
        """Get the website platform for an organization."""

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


class PlatformsCallcenterResource(object):
    """The callcenter platform for an organization."""

    def __init__(self, platforms_callcenter_update_request_validator, model):
        self._platforms_callcenter_update_request_validator = \
            platforms_callcenter_update_request_validator
        self._model = model

    def on_get(self, req, resp):
        """Get the callcenter platform for an organization."""

        user = req.context['user']

        try:
            platforms_callcenter = self._model.get_platforms_callcenter(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Callcenter does not exist',
                description='Callcenter does not exist') from e

        response = {'platformsCallcenter': platforms_callcenter}

        jsonschema.validate(response, schemas.PLATFORMS_CALLCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the callcenter platform for an organization."""

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

        try:
            platforms_callcenter = self._model.update_platforms_callcenter(user['id'], **platforms_callcenter_update_request)
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Callcenter does not exist',
                description='Callcenter does not exist')

        response = {'platformsCallcenter': platforms_callcenter}
        
        response['platformsCallcenter'].update(platforms_callcenter_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_CALLCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


class PlatformsEmailcenterResource(object):
    """The emailcenter platform for an organization."""

    def __init__(self, platforms_emailcenter_update_request_validator, model):
        self._platforms_emailcenter_update_request_validator = \
            platforms_emailcenter_update_request_validator
        self._model = model

    def on_get(self, req, resp):
        """Get the emailcenter platform for an organization."""

        user = req.context['user']

        try:
            platforms_emailcenter = self._model.get_platforms_emailcenter(user['id'])
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Emailcenter does not exist',
                description='Emailcenter does not exist') from e

        response = {'platformsEmailcenter': platforms_emailcenter}

        jsonschema.validate(response, schemas.PLATFORMS_EMAILCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_put(self, req, resp):
        """Update the emailcenter platform for an organization."""

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

        try:
            platforms_emailcenter = self._model.update_platforms_emailcenter(user['id'], **platforms_emailcenter_update_request)
        except model.OrgDoesNotExist as e:
            raise falcon.HTTPNotFound(
                title='Emailcenter does not exist',
                description='Emailcenter does not exist')

        response = {'platformsEmailcenter': platforms_emailcenter}
        
        response['platformsEmailcenter'].update(platforms_emailcenter_update_request)

        jsonschema.validate(response, schemas.PLATFORMS_EMAILCENTER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)
