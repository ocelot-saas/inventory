"""Identity validation."""

import datetime
import json

import jsonschema
import slugify

import inventory.schemas as schemas


class Error(Exception):
    """Error raised by validation methods."""

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return 'Validation error! Reason:\n {}'.format(str(self._reason))


class ImageSetValidator(object):
    """Validator for an image set."""

    def __init__(self):
        pass

    def validate(self, image_set_raw):
        try:
            jsonschema.validate(image_set_raw, schemas.IMAGE_SET)

            for i in range(len(image_set_raw)):
                if image_set_raw[i]['orderNo'] != i:
                    raise Error('Image set not properly ordered')

                image_set_raw[i]['uri'] = image_set_raw[i]['uri'].strip()

                if image_set_raw[i]['uri'] == '':
                    raise Error('Image set url is empty')
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate image set') from e

        return image_set_raw
    

class RestaurantNameValidator(object):
    """Validator for a restaurant name."""

    MAX_NAME_SIZE = 100

    def __init__(self):
        pass

    def validate(self, name_raw):
        name = name_raw.strip()

        if name == '':
            raise Error('Name is empty')

        if len(name) > self.MAX_NAME_SIZE:
            raise Error('Name is too long')

        return name


class RestaurantDescriptionValidator(object):
    """Validator for a restaurant description."""

    MAX_DESCRIPTION_SIZE = 1000

    def __init__(self):
        pass

    def validate(self, description_raw):
        description = description_raw.strip()

        if len(description) > self.MAX_DESCRIPTION_SIZE:
            raise Error('Description is too long')

        return description


class RestaurantKeywordsValidator(object):
    """Validator for a restaurant keywords set."""

    MAX_KEYWORD_SIZE = 100

    def __init__(self):
        pass

    def validate(self, keywords_raw):
        try:
            jsonschema.validate(keywords_raw, schemas.RESTAURANT_KEYWORDS)
            keywords_unsorted = [kw.strip() for kw in keywords_raw]

            if any(kw == '' for kw in keywords_unsorted):
                raise Error('Keyword is empty')

            for kw in keywords_unsorted:
                if len(kw) > self.MAX_KEYWORD_SIZE:
                    raise Error('Keyword "{}" is too long'.format(kw))

            keywords = sorted(set(keywords_unsorted))
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate keyword set') from e

        return keywords


class RestaurantAddressValidator(object):
    """Validator for a restaurant address."""

    MAX_ADDRESS_SIZE = 100

    def __init__(self):
        pass

    def validate(self, address_raw):
        address = address_raw.strip()

        if len(address) > self.MAX_ADDRESS_SIZE:
            raise Error('Address is too long')

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


class OrgCreationRequestValidator(object):
    """Validator for an org creation request."""

    def __init__(self, restaurant_name_validator, restaurant_description_validator,
                 restaurant_keywords_validator, restaurant_address_validator,
                 restaurant_opening_hours_validator, image_set_validator):
        self._restaurant_name_validator = restaurant_name_validator
        self._restaurant_description_validator = restaurant_description_validator
        self._restaurant_keywords_validator = restaurant_keywords_validator
        self._restaurant_address_validator = restaurant_address_validator
        self._restaurant_opening_hours_validator = restaurant_opening_hours_validator
        self._image_set_validator = image_set_validator

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

            org_creation_request['imageSet'] = \
                self._image_set_validator.validate(org_creation_request['imageSet'])
        except ValueError as e:
            raise Error('Could not decode org creation request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate org creation request') from e
        except Error as e:
            raise Error('Could not validate org creation request') from e
        except Exception as e:
            raise Error('Other error') from e

        return org_creation_request


class RestaurantUpdateRequestValidator(object):
    """Validator for a restaurant update request."""

    def __init__(self, restaurant_name_validator, restaurant_description_validator,
                 restaurant_keywords_validator, restaurant_address_validator,
                 restaurant_opening_hours_validator, image_set_validator):
        self._restaurant_name_validator = restaurant_name_validator
        self._restaurant_description_validator = restaurant_description_validator
        self._restaurant_keywords_validator = restaurant_keywords_validator
        self._restaurant_address_validator = restaurant_address_validator
        self._restaurant_opening_hours_validator = restaurant_opening_hours_validator
        self._image_set_validator = image_set_validator

    def validate(self, restaurant_update_request_raw):
        try:
            restaurant_update_request = json.loads(restaurant_update_request_raw)
            jsonschema.validate(restaurant_update_request, schemas.RESTAURANT_UPDATE_REQUEST)

            if 'name' in restaurant_update_request:
                restaurant_update_request['name'] = \
                    self._restaurant_name_validator.validate(restaurant_update_request['name'])

            if 'description' in restaurant_update_request:
                restaurant_update_request['description'] = \
                    self._restaurant_description_validator.validate(
                        restaurant_update_request['description'])

            if 'keywords' in restaurant_update_request:
                restaurant_update_request['keywords'] = \
                    self._restaurant_keywords_validator.validate(
                        restaurant_update_request['keywords'])

            if 'address' in restaurant_update_request:
                restaurant_update_request['address'] = \
                    self._restaurant_address_validator.validate(
                        restaurant_update_request['address'])

            if 'openingHours' in restaurant_update_request:
                restaurant_update_request['openingHours'] = \
                    self._restaurant_opening_hours_validator.validate(
                        restaurant_update_request['openingHours'])

            if 'imageSet' in restaurant_update_request:
                restaurant_update_request['imageSet'] = \
                    self._image_set_validator.validate(
                        restaurant_update_request['imageSet'])
        except ValueError as e:
            raise Error('Could not decode restaurant update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate restaurant update request') from e
        except Error as e:
            raise Error('Could not validate restaurant update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return restaurant_update_request


class PlatformsWebsiteUpdateRequestValidator(object):
    """Validator for a website platform."""

    def __init__(self):
        pass

    def validate(self, platforms_website_update_request_raw):
        try:
            platforms_website_update_request = json.loads(platforms_website_update_request_raw)
            jsonschema.validate(
                platforms_website_update_request,
                schemas.PLATFORMS_WEBSITE_UPDATE_REQUEST)

            if 'subdomain' in platforms_website_update_request:
                subdomain = platforms_website_update_request['subdomain']

                if not subdomain == slugify.slugify(subdomain):
                    raise Error('Subdomain {} is not valid'.format(subdomain))
        except ValueError as e:
            raise Error('Could not decode website update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate website update request') from e
        except Error as e:
            raise Error('Could not validate website update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return platforms_website_update_request
