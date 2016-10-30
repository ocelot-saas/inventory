import unittest

import falcon.testing


class OrgResourceTestCase(falcon.testing.TestCase):
    def test_get(self):
        """GET /org works."""
        pass


if __name__ == '__main__':
    unittest.main()
