"""Inventory service main module."""

from wsgiref import simple_server

import clock
import falcon
import falcon_cors
import sqlalchemy

import identity.client as identity
import inventory.config as config
import inventory.handlers as inventory
import inventory.model as model
import inventory.validation as validation


auth_middleware = identity.AuthMiddleware(config.IDENTITY_SERVICE_DOMAIN)
cors_middleware = falcon_cors.CORS(
    allow_origins_list=config.CLIENTS,
    allow_headers_list=['Authorization', 'Content-Type'],
    allow_all_methods=True).middleware

app = falcon.API(middleware=[auth_middleware, cors_middleware])

restaurant_name_validator = validation.RestaurantNameValidator()
restaurant_description_validator = validation.RestaurantDescriptionValidator()
restaurant_keywords_validator = validation.RestaurantKeywordsValidator()
restaurant_address_validator = validation.RestaurantAddressValidator()
restaurant_opening_hours_validator = validation.RestaurantOpeningHoursValidator()
image_set_validator = validation.ImageSetValidator()
org_creation_request_validator = validation.OrgCreationRequestValidator(
    restaurant_name_validator=restaurant_name_validator,
    restaurant_description_validator=restaurant_description_validator,
    restaurant_keywords_validator=restaurant_keywords_validator,
    restaurant_address_validator=restaurant_address_validator,
    restaurant_opening_hours_validator=restaurant_opening_hours_validator,
    image_set_validator=image_set_validator)
restaurant_update_request_validator = validation.RestaurantUpdateRequestValidator(
    restaurant_name_validator=restaurant_name_validator,
    restaurant_description_validator=restaurant_description_validator,
    restaurant_keywords_validator=restaurant_keywords_validator,
    restaurant_address_validator=restaurant_address_validator,
    restaurant_opening_hours_validator=restaurant_opening_hours_validator,
    image_set_validator=image_set_validator)
menu_sections_creation_request_validator = validation.MenuSectionsCreationRequestValidator(
    name_validator=restaurant_name_validator,
    description_validator=restaurant_description_validator)
platforms_website_update_request_validator = validation.PlatformsWebsiteUpdateRequestValidator()
platforms_callcenter_update_request_validator = \
    validation.PlatformsCallcenterUpdateRequestValidator()
platforms_emailcenter_update_request_validator = \
    validation.PlatformsEmailcenterUpdateRequestValidator()
the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)
model = model.Model(the_clock, sql_engine)

org_resource = inventory.OrgResource(
    org_creation_request_validator=org_creation_request_validator,
    model=model)

restaurant_resource = inventory.RestaurantResource(
    restaurant_update_request_validator=restaurant_update_request_validator,
    model=model)

menu_sections_resource = inventory.MenuSectionsResource(
    menu_sections_creation_request_validator=menu_sections_creation_request_validator,
    model=model)

menu_section_resource = inventory.MenuSectionResource(
    model=model)

menu_items_resource = inventory.MenuItemsResource(
    model=model)

menu_item_resource = inventory.MenuItemResource(
    model=model)

platforms_website_resource = inventory.PlatformsWebsiteResource(
    platforms_website_update_request_validator=platforms_website_update_request_validator,
    model=model)

platforms_callcenter_resource = inventory.PlatformsCallcenterResource(
    platforms_callcenter_update_request_validator=platforms_callcenter_update_request_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

platforms_emailcenter_resource = inventory.PlatformsEmailcenterResource(
    platforms_emailcenter_update_request_validator=platforms_emailcenter_update_request_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

app.add_route('/org', org_resource)
app.add_route('/org/restaurant', restaurant_resource)
app.add_route('/org/menu/sections', menu_sections_resource)
app.add_route('/org/menu/sections/{section_id}', menu_section_resource)
app.add_route('/org/menu/items', menu_items_resource)
app.add_route('/org/menu/items/{item_id}', menu_item_resource)
app.add_route('/org/platforms/website', platforms_website_resource)
app.add_route('/org/platforms/callcenter', platforms_callcenter_resource)
app.add_route('/org/platforms/emailcenter', platforms_emailcenter_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
