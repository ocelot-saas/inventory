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

# /org
#   POST creates the general info about the organization and restaurant
#   GET retrieves general information about the organization and the restaurant
app = falcon.API(middleware=[auth_middleware])

restaurant_name_validator = validation.RestaurantNameValidator()
restaurant_description_validator = validation.RestaurantDescriptionValidator()
restaurant_keywords_validator = validation.RestaurantKeywordsValidator()
restaurant_address_validator = validation.RestaurantAddressValidator()
restaurant_opening_hours_validator = validation.RestaurantOpeningHoursValidator()
org_creation_request_validator = validation.OrgCreationRequestValidator(
    restaurant_name_validator=restaurant_name_validator,
    restaurant_description_validator=restaurant_description_validator,
    restaurant_keywords_validator=restaurant_keywords_validator,
    restaurant_address_validator=restaurant_address_validator,
    restaurant_opening_hours_validator=restaurant_opening_hours_validator)
restaurant_update_request_validator = validation.RestaurantUpdateRequestValidator(
    restaurant_name_validator=restaurant_name_validator,
    restaurant_description_validator=restaurant_description_validator,
    restaurant_keywords_validator=restaurant_keywords_validator,
    restaurant_address_validator=restaurant_address_validator,
    restaurant_opening_hours_validator=restaurant_opening_hours_validator)
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

app.add_route('/org', org_resource)
app.add_route('/org/restaurant', restaurant_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
