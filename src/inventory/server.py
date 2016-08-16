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

the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)

org_resource = inventory.OrgResource(
    the_clock=the_clock,
    sql_engine=sql_engine)

app.add_route('/org', org_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
