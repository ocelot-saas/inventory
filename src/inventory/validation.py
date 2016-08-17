"""Identity validation."""

import datetime
import json

import inventory.schemas as schemas
import jsonschema


class Error(Exception):
    """Error raised by validation methods."""

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return 'Validation error! Reason:\n {}'.format(str(self._reason))


class OrgCreationRequestValidator(object):
    """Validator for an org creation request."""

    def __init__(self, restaurant_name_validataor, restaurant_description_validator,
                 restaurant_keywords_validator, restaurant_address_validator,
                 restaurant_opening_hours_validator):
        self._restaurant_name_validator = restaurant_name_validator
        self._restaurant_description_validator = restaurant_description_validator
        self._restaurant_keywords_validataor = restaurant_keywords_validator
        self._restaurant_address_validator = restaurant_address_validator
        self._restaurant_opening_hours_validator = restaurant_opening_hours_validator

    def validate(self, org_creation_request_raw):
        try:
            org_creation_request = json.loads(org_creation_request_raw)
            jsonschema.validate(org_creation_request, schemas.ORG_CREATION_REQUEST)

            org_creation_request['name'] = \
                self._restaurant_name_validator.validate(org_creation_request['name'])
            org_creation_request['description'] = \
                self._restaurant_description_validator.validate(org_creation_request['description'])
            org_creation_request['keywords'] = \
                self._restaurant_keywords_validator.validate(org_creation_request['keywords'])
            org_creation_request['address'] = \
                self._restaurant_address_validator.validate(org_creation_request['address'])
            org_creation_request['openingHours'] = \
                self._restaurant_opening_hours_validator.validate(
                    org_creation_request['openingHours'])
        except json.decoder.JSONDecodeError as e:
            raise Error('Could not decode org creation request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate org creation request') from e
        except Error as e:
            raise Error('Could not validate org creation request') from e
        except Exception as e:
            raise Error('Other error') from e

        return org_creation_request


class RestaurantNameValidator(object):
    """Validator for a restaurant name."""

    def __init__(self):
        pass

    def validate(self, name_raw):
        name = name_raw.trim()

        if name == '':
            raise Error('Name is empty')

        return name


class RestaurantDescriptionValidator(object):
    """Validator for a restaurant description."""

    def __init__(self):
        pass

    def validate(self, description_raw):
        description = description_raw.trim()

        return description


class RestaurantKeywordsValidator(object):
    """Validator for a restaurant keywords set."""

    def __init__(self):
        pass

    def validate(self, keywords_raw):
        try:
            jsonschema.validate(keywords_raw, schemas.RESTAURANT_KEYWORDS)
            keywords_unsorted = [kw.trim() for kw in keywords_raw]

            if any(kw == '' for kw in keywords_unsorted):
                raise Error('Keyword is empty')

            keywords = sorted(set(keywords))
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate keyword set') from e

        return keywords


class RestaurantAddressValidator(object):
    """Validator for a restaurant address."""

    def __init__(self):
        pass

    def validate(self, address_raw):
        address = address_raw.trim()

        return address


class RestaurantOpeningHoursValidator(object):
    """Validator for restaurant opening hours."""

    def __init__(self):
        pass

    def validate(self, opening_hours_raw):
        try:
            jsonschema.validate(opening_hours_raw, schemas.RESTAURANT_OPENING_HOURS)
            
            self._validate_interval('weekday', opening_hours_raw['weekday'])
            self._validate_interval('saturday', opening_hours_raw['saturday'])
            self._validate_interval('sunday', opening_hours_raw['sunday'])
            
            opening_hours = opening_hours_raw
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate opening hours') from e

        return opening_hours

    def _validate_interval(self, label, interval):
        start_time = datetime.time(interval['start']['hour'], interval['start']['minute'])
        end_time = datetime.time(interval['end']['hour'], interval['end']['minute'])

        if start_time >= end_time:
            raise Error(
                'Start time "{}" after end time "{}" for "{}"'.format(start_time, end_time, label))
