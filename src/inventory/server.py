"""Inventory service main module."""

from wsgiref import simple_server

import falcon

import clock
import identity.client as identity
import inventory.config as config
import inventory.handlers as inventory
import inventory.validation as validation
import sqlalchemy


auth_middleware = identity.AuthMiddleware(config.IDENTITY_SERVICE_DOMAIN)

app = falcon.API(middleware=[auth_middleware])

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
platforms_website_update_request_validator = validation.PlatformsWebsiteUpdateRequestValidator()
platforms_callcenter_update_request_validator = \
    validation.PlatformsCallcenterUpdateRequestValidator()
platforms_emailcenter_update_request_validator = \
    validation.PlatformsEmailcenterUpdateRequestValidator()
the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)

org_resource = inventory.OrgResource(
    org_creation_request_validator=org_creation_request_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

restaurant_resource = inventory.RestaurantResource(
    restaurant_update_request_validator=restaurant_update_request_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

menu_sections_resource = inventory.MenuSectionsResource(
    the_clock=the_clock,
    sql_engine=sql_engine)

menu_section_resource = inventory.MenuSectionResource(
    the_clock=the_clock,
    sql_engine=sql_engine)

menu_items_resource = inventory.MenuItemsResource(
    the_clock=the_clock,
    sql_engine=sql_engine)

menu_item_resource = inventory.MenuItemResource(
    the_clock=the_clock,
    sql_engine=sql_engine)

platforms_website_resource = inventory.PlatformsWebsiteResource(
    platforms_website_update_request_validator=platforms_website_update_request_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

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
app.add_route('/org/menu/sections/{section_id}/items', menu_items_resource)
app.add_route('/org/menu/sections/{section_id}/items/{item_id}', menu_item_resource)
app.add_route('/org/platforms/website', platforms_website_resource)
app.add_route('/org/platforms/callcenter', platforms_callcenter_resource)
app.add_route('/org/platforms/emailcenter', platforms_emailcenter_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
