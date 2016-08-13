import unittest

import falcon.testing
from mockito import mock

import inventory.handlers as inventory


class OrgResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(OrgResourceTestCase, self).setUp()

        the_clock = mock()
        sql_engine = mock()

        org_resource = inventory.OrgResource(
            the_clock=the_clock,
            sql_engine=sql_engine)

        self.api.add_route('/org', org_resource)

    def test_get(self):
        """GET /org works."""
        pass


if __name__ == '__main__':
    unittest.main()