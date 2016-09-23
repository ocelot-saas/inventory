"""Identity validation."""

import datetime
import json

import jsonschema
import phonenumbers
import slugify
import validate_email

import inventory.schemas as schemas


class Error(Exception):
    """Error raised by validation methods."""

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return 'Validation error! Reason:\n {}'.format(str(self._reason))


class IdValidator(object):
    """Validate an id."""

    def __init__(self):
        pass

    def validate(self, id):
        if id <= 0:
            raise Error('Id is negative')

        return id


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


class KeywordsValidator(object):
    """Validator for a restaurant keywords set."""

    MAX_KEYWORD_SIZE = 100

    def __init__(self):
        pass

    def validate(self, keywords_raw):
        try:
            jsonschema.validate(keywords_raw, schemas.KEYWORDS)
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


class IngredientsValidator(object):
    """Validator for a restaurant ingredients set."""

    MAX_INGREDIENT_SIZE = 100

    def __init__(self):
        pass

    def validate(self, ingredients_raw):
        try:
            jsonschema.validate(ingredients_raw, schemas.INGREDIENTS)
            ingredients_unsorted = [kw.strip() for kw in ingredients_raw]

            if any(kw == '' for kw in ingredients_unsorted):
                raise Error('Ingredient is empty')

            for kw in ingredients_unsorted:
                if len(kw) > self.MAX_INGREDIENT_SIZE:
                    raise Error('Ingredient "{}" is too long'.format(kw))

            ingredients = sorted(set(ingredients_unsorted))
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate ingredient set') from e

        return ingredients


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
                 keywords_validator, restaurant_address_validator,
                 restaurant_opening_hours_validator, image_set_validator):
        self._restaurant_name_validator = restaurant_name_validator
        self._restaurant_description_validator = restaurant_description_validator
        self._keywords_validator = keywords_validator
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
                self._keywords_validator.validate(org_creation_request['keywords'])
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
                 keywords_validator, restaurant_address_validator,
                 restaurant_opening_hours_validator, image_set_validator):
        self._restaurant_name_validator = restaurant_name_validator
        self._restaurant_description_validator = restaurant_description_validator
        self._keywords_validator = keywords_validator
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
                    self._keywords_validator.validate(
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


class MenuSectionsCreationRequestValidator(object):
    """Validator for a menu section creation request."""

    def __init__(self, name_validator, description_validator):
        self._name_validator = name_validator
        self._description_validator = description_validator

    def validate(self, menu_sections_creation_request_raw):
        try:
            menu_sections_creation_request = json.loads(menu_sections_creation_request_raw)
            jsonschema.validate(
                menu_sections_creation_request,
                schemas.MENU_SECTIONS_CREATION_REQUEST)

            menu_sections_creation_request['name'] = \
                self._name_validator.validate(menu_sections_creation_request['name'])
            menu_sections_creation_request['description'] = \
                self._description_validator.validate(
                    menu_sections_creation_request['description'])
        except ValueError as e:
            raise Error('Could not decode org creation request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate menu section creation request') from e
        except Error as e:
            raise Error('Could not validate menu section creation request') from e
        except Exception as e:
            raise Error('Other error') from e

        return menu_sections_creation_request


class MenuSectionUpdateRequestValidator(object):
    """Validator for a menu section update request."""

    def __init__(self, name_validator, description_validator):
        self._name_validator = name_validator
        self._description_validator = description_validator

    def validate(self, menu_section_update_request_raw):
        try:
            menu_section_update_request = json.loads(menu_section_update_request_raw)
            jsonschema.validate(
                menu_section_update_request,
                schemas.MENU_SECTION_UPDATE_REQUEST)

            if 'name' in menu_section_update_request:
                menu_section_update_request['name'] = \
                    self._name_validator.validate(menu_section_update_request['name'])

            if 'description' in menu_section_update_request:
                menu_section_update_request['description'] = \
                    self._description_validator.validate(menu_section_update_request['description'])
        except ValueError as e:
            raise Error('Could not decode menu section update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate menu section update request') from e
        except Error as e:
            raise Error('Could not validate menu section update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return menu_section_update_request


class MenuItemsCreationRequestValidator(object):
    """Validator for a menu item creation request."""

    def __init__(self, id_validator, name_validator, description_validator,
                 keywords_validator, ingredients_validator, image_set_validator):
        self._id_validator = id_validator
        self._name_validator = name_validator
        self._description_validator = description_validator
        self._keywords_validator = keywords_validator
        self._ingredients_validator = ingredients_validator
        self._image_set_validator = image_set_validator

    def validate(self, menu_items_creation_request_raw):
        try:
            menu_items_creation_request = json.loads(menu_items_creation_request_raw)
            jsonschema.validate(menu_items_creation_request, schemas.MENU_ITEMS_CREATION_REQUEST)

            menu_items_creation_request['sectionId'] = \
                self._id_validator.validate(menu_items_creation_request['sectionId'])
            menu_items_creation_request['name'] = \
                self._name_validator.validate(menu_items_creation_request['name'])
            menu_items_creation_request['description'] = \
                self._description_validator.validate(menu_items_creation_request['description'])
            menu_items_creation_request['keywords'] = \
                self._keywords_validator.validate(menu_items_creation_request['keywords'])
            menu_items_creation_request['ingredients'] = \
                self._ingredients_validator.validate(menu_items_creation_request['ingredients'])
            menu_items_creation_request['imageSet'] = \
                self._image_set_validator.validate(menu_items_creation_request['imageSet'])
        except ValueError as e:
            raise Error('Could not decode menu items creation request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate menu items creation request') from e
        except Error as e:
            raise Error('Could not validate menu items creation request') from e
        except Exception as e:
            raise Error('Other error') from e

        return menu_items_creation_request


class MenuItemUpdateRequestValidator(object):
    """Validator for a menu item update request."""

    def __init__(self, id_validator, name_validator, description_validator,
                 keywords_validator, ingredients_validator, image_set_validator):
        self._id_validator = id_validator
        self._name_validator = name_validator
        self._description_validator = description_validator
        self._keywords_validator = keywords_validator
        self._ingredients_validator = ingredients_validator
        self._image_set_validator = image_set_validator

    def validate(self, menu_item_update_request_raw):
        try:
            menu_item_update_request = json.loads(menu_item_update_request_raw)
            jsonschema.validate(
                menu_item_update_request,
                schemas.MENU_ITEM_UPDATE_REQUEST)

            if 'name' in menu_item_update_request:
                menu_item_update_request['name'] = \
                    self._name_validator.validate(menu_item_update_request['name'])

            if 'description' in menu_item_update_request:
                menu_item_update_request['description'] = \
                    self._description_validator.validate(menu_item_update_request['description'])

            if 'keywords' in menu_item_update_request:
                menu_item_update_request['keywords'] = \
                    self._keywords_validator.validate(menu_item_update_request['keywords'])

            if 'ingredients' in menu_item_update_request:
                menu_item_update_request['ingredients'] = \
                    self._ingredients_validator.validate(menu_item_update_request['ingredients'])

            if 'imageSet' in menu_item_update_request:
                menu_item_update_request['imageSet'] = \
                    self._image_set_validator.validate(menu_item_update_request['imageSet'])
        except ValueError as e:
            raise Error('Could not decode menu item update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate menu item update request') from e
        except Error as e:
            raise Error('Could not validate menu item update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return menu_item_update_request


class PlatformsWebsiteUpdateRequestValidator(object):
    """Validator for a website platform."""

    MAX_DOMAIN_SIZE = 100

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

                if len(subdomain) > self.MAX_DOMAIN_SIZE:
                    raise Error('Subdomain is too long'.format(subdomain))

                if not subdomain == slugify.slugify(subdomain):
                    raise Error('Subdomain {} is not valid'.format(subdomain))
        except ValueError as e:
            raise Error('Could not decode website update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate website update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return platforms_website_update_request


class PlatformsCallcenterUpdateRequestValidator(object):
    """Validator for a callcenter platform."""

    def __init__(self):
        pass

    def validate(self, platforms_callcenter_update_request_raw):
        try:
            platforms_callcenter_update_request = \
                json.loads(platforms_callcenter_update_request_raw)
            jsonschema.validate(
                platforms_callcenter_update_request,
                schemas.PLATFORMS_CALLCENTER_UPDATE_REQUEST)

            if 'phoneNumber' in platforms_callcenter_update_request:
                phone_number_raw = platforms_callcenter_update_request['phoneNumber']
                phone_number = phonenumbers.parse(phone_number_raw, "RO")

                if not phonenumbers.is_possible_number(phone_number) or \
                   not phonenumbers.is_valid_number(phone_number):
                    raise Error('Phone number {} is not valid'.format(phone_number))

                platforms_callcenter_update_request['phoneNumber'] = \
                    phonenumbers.format_number(
                        phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        except ValueError as e:
            raise Error('Could not decode callcenter update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate callcenter update request') from e
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise Error('Could not parse phone number') from e
        except Exception as e:
            raise Error('Other error') from e

        return platforms_callcenter_update_request


class PlatformsEmailcenterUpdateRequestValidator(object):
    """Validator for a emailcenter platform."""

    MAX_EMAIL_NAME_SIZE = 100

    def __init__(self):
        pass

    def validate(self, platforms_emailcenter_update_request_raw):
        try:
            platforms_emailcenter_update_request = \
                json.loads(platforms_emailcenter_update_request_raw)
            jsonschema.validate(
                platforms_emailcenter_update_request,
                schemas.PLATFORMS_EMAILCENTER_UPDATE_REQUEST)

            if 'emailName' in platforms_emailcenter_update_request:
                email_name = platforms_emailcenter_update_request['emailName']

                if len(email_name) > self.MAX_EMAIL_NAME_SIZE:
                    raise Error('Email name is too long'.format(email_name))

                if not validate_email.validate_email('{}@example.com'.format(email_name)):
                    raise Error('Email name {} is invalid'.format(email_name))
        except ValueError as e:
            raise Error('Could not decode emailcenter update request') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not structurally validate emailcenter update request') from e
        except Exception as e:
            raise Error('Other error') from e

        return platforms_emailcenter_update_request
