"""Schema for the inventory APIs objects."""

TIME_IN_DAY = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'A particular time in a day',
    'description': 'A particular time in a day',
    'type': 'object',
    'properties': {
        'hour': {
            'description': 'The hour for the time',
            'type': 'integer',
            'minimum': 0,
            'maximum': 23,
        },
        'minute': {
            'description': 'The minute for the time',
            'type': 'integer',
            'minimum': 0,
            'maximum': 59
        },
    },
    'required': ['hour', 'minute'],
    'additionalProperties': False,
}


INTERVAL_IN_DAY = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'A particular interval in a day',
    'description': 'A particular interval in a day',
    'type': 'object',
    'properties': {
        'start': TIME_IN_DAY,
        'end': TIME_IN_DAY,
    },
    'required': ['start', 'end'],
    'additionalProperties': False,
}


# TODO(horia141): keep in sync with frontend
IMAGE_ASPECT_RATIO = 16/9
IMAGE_MIN_WIDTH = 800
IMAGE_MIN_HEIGHT = 450
IMAGE_MAX_WIDTH = 1600
IMAGE_MAX_HEIGHT = 900
IMAGE_WIDTH = IMAGE_MAX_WIDTH
IMAGE_HEIGHT = IMAGE_MAX_HEIGHT


IMAGE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Image',
    'description': 'An image',
    'type': 'object',
    'properties': {
        'orderNo': {
            'description': 'The order in which the image appears for display',
            'type': 'integer',
            'minimum': 0
        },
        'uri': {
            'description': 'The URI where the image can be retrieved',
            'type': 'string',
        },
        'width': {
            'description': 'The width of the image',
            'type': 'integer',
            'minimum': IMAGE_MIN_WIDTH,
            'maximum': IMAGE_MAX_WIDTH
        },
        'height': {
            'description': 'The height of the image',
            'type': 'integer',
            'minimum': IMAGE_MIN_HEIGHT,
            'maximum': IMAGE_MAX_HEIGHT
        }
    },
    'required': ['orderNo', 'uri', 'width', 'height'],
    'additionalProperties': False
}


IMAGE_SET = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Image set',
    'description': 'A set of images',
    'type': 'array',
    'items': IMAGE,
    'additionalItems': False
}


KEYWORDS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Keywords',
    'description': 'A set of keywords',
    'type': 'array',
    'items': {
        'type': 'string',
    },
    'additionalItems': False
}


INGREDIENTS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Food ingredients',
    'description': 'The set of ingredients for a restaurant',
    'type': 'array',
    'items': {
        'type': 'string',
    },
    'additionalItems': False
}


RESTAURANT_OPENING_HOURS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Restaurant opening hours',
    'description': 'The set of opening hours for a restaurant',
    'type': 'object',
    'properties': {
        'weekday': INTERVAL_IN_DAY,
        'saturday': INTERVAL_IN_DAY,
        'sunday': INTERVAL_IN_DAY,
    },
    'required': ['weekday', 'saturday', 'sunday'],
    'additionalProperties': False
}


RESTAURANT = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Restaurant',
    'description': 'Information about a restaurant',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the restaurant',
            'type': 'integer',
        },
        'timeCreatedTs': {
            'description': 'The time the restaurant was created, in UTC',
            'type': 'integer',
        },
        'name': {
            'description': 'The name of the restaurant',
            'type': 'string',
        },
        'description': {
            'description': 'The description of the restaurant',
            'type': 'string',
        },
        'keywords': KEYWORDS,
        'address': {
            'description': 'The address of the restaurant',
            'type': 'string',
        },
        'openingHours': RESTAURANT_OPENING_HOURS,
        'imageSet': IMAGE_SET,
    },
    'required': ['id', 'timeCreatedTs', 'name', 'description', 'keywords',
                 'address', 'openingHours', 'imageSet'],
    'additionalProperties': False
}


MENU_ITEM = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu item',
    'description': 'Information about a menu item',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the menu item',
            'type': 'integer'
        },
        'timeCreatedTs': {
            'description': 'The time the menu item was created, in UTC',
            'type': 'integer',
        },
        'name': {
            'description': 'The name of the menu item',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu item',
            'type': 'string'
        },
        'keywords': KEYWORDS,
        'ingredients': INGREDIENTS,
        'imageSet': IMAGE_SET,
    },
    'required': ['id', 'timeCreatedTs', 'name', 'description', 'keywords',
                 'ingredients', 'imageSet'],
    'additionalProperties': False
}


MENU_SECTION = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu section',
    'description': 'Information about a menu section',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the menu section',
            'type': 'integer'
        },
        'timeCreatedTs': {
            'description': 'The time the menu section was created, in UTC',
            'type': 'integer',
        },
        'name': {
            'description': 'The name of the menu section',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu section',
            'type': 'string'
        },
        'menuItems': {
            'description': 'The menu items for this section. Optional',
            'type': 'array',
            'items': MENU_ITEM
        },
    },
    'required': ['id', 'timeCreatedTs', 'name', 'description'],
    'additionalProperties': False
}


PLATFORMS_WEBSITE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Website platform',
    'description': 'Information about a website platform',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the website platform',
            'type': 'integer',
        },
        'timeCreatedTs': {
            'description': 'The time the website platform was created, in UTC',
            'type': 'integer',
        },
        'subdomain': {
            'description': 'The subdomain to assign to the website',
            'type': 'string'
        }
    },
    'required': ['id', 'timeCreatedTs', 'subdomain'],
    'additionalProperties': False
}


PLATFORMS_CALLCENTER = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Callcenter platform',
    'description': 'Information about a callcenter platform',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the callcenter platform',
            'type': 'integer',
        },
        'timeCreatedTs': {
            'description': 'The time the callcenter platform was created, in UTC',
            'type': 'integer',
        },
        'phoneNumber': {
            'description': 'The phone number to assign to the callcenter',
            'type': 'string'
        }
    },
    'required': ['id', 'timeCreatedTs', 'phoneNumber'],
    'additionalProperties': False
}


PLATFORMS_EMAILCENTER = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Emailcenter platform',
    'description': 'Information about a emailcenter platform',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the emailcenter platform',
            'type': 'integer',
        },
        'timeCreatedTs': {
            'description': 'The time the emailcenter platform was created, in UTC',
            'type': 'integer',
        },
        'emailName': {
            'description': 'The email name to assign to the emailcenter',
            'type': 'string'
        }
    },
    'required': ['id', 'timeCreatedTs', 'emailName'],
    'additionalProperties': False
}


ORG = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Org',
    'description': 'Information about an org',
    'type': 'object',
    'properties': {
        'id': {
            'description': 'The unique id assigned to the org',
            'type': 'integer',
        },
        'timeCreatedTs': {
            'description': 'The time the org was created, in UTC',
            'type': 'integer',
        }
    },
    'required': ['id', 'timeCreatedTs'],
    'additionalProperties': False
}


WEBSHOP_INFO = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Webshop info',
    'description': 'All info needed by a shop',
    'type': 'object',
    'properties': {},
    'additionalProperties': False
}


ORG_CREATION_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Org creation request',
    'description': 'Data required to create an org',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The name of the restaurant',
            'type': 'string',
        },
        'description': {
            'description': 'The description of the restaurant',
            'type': 'string',
        },
        'keywords': KEYWORDS,
        'address': {
            'description': 'The address of the restaurant',
            'type': 'string',
        },
        'openingHours': RESTAURANT_OPENING_HOURS,
        'imageSet': IMAGE_SET
    },
    'required': ['name', 'description', 'keywords', 'address', 'openingHours', 'imageSet'],
    'additionalProperties': False
}


ORG_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Org response',
    'description': 'Common response for orgs',
    'type': 'object',
    'properties': {
        'org': ORG
    },
    'required': ['org'],
    'additionalProperties': False
}


RESTAURANT_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Restaurant update request',
    'description': 'Request for updating a restaurant',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The name of the restaurant',
            'type': 'string',
        },
        'description': {
            'description': 'The description of the restaurant',
            'type': 'string',
        },
        'keywords': KEYWORDS,
        'address': {
            'description': 'The address of the restaurant',
            'type': 'string',
        },
        'openingHours': RESTAURANT_OPENING_HOURS,
        'imageSet': IMAGE_SET
    },
    'anyOf': [
        {'required': ['name']},
        {'required': ['description']},
        {'required': ['keywords']},
        {'required': ['address']},
        {'required': ['openingHours']},
        {'required': ['imageSet']}
    ],
    'additionalProperties': False
}


RESTAURANT_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Restaurant response',
    'description': 'Common response for restaurants',
    'type': 'object',
    'properties': {
        'restaurant': RESTAURANT
    },
    'required': ['restaurant'],
    'additionalProperties': False
}


MENU_SECTIONS_CREATION_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu section creation request',
    'description': 'Creation request for a menu section',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The name of the menu section',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu section',
            'type': 'string'
        },
    },
    'required': ['name', 'description'],
    'additionalProperties': False
}


MENU_SECTIONS_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu sections response',
    'description': 'Common response for menu sections',
    'type': 'object',
    'properties': {
        'menuSections': {
            'description': 'The menu sections',
            'type': 'array',
            'items': MENU_SECTION
        }
    },
    'required': ['menuSections'],
    'additionalProperties': False
}


MENU_SECTION_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu section update request',
    'description': 'Update request for a menu section',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The name of the menu section',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu section',
            'type': 'string'
        },
    },
    'anyOf': [
        {'required': ['name']},
        {'required': ['description']},
    ],
    'additionalProperties': False
}


MENU_SECTION_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu section response',
    'description': 'Common response for menu section',
    'type': 'object',
    'properties': {
        'menuSection': MENU_SECTION
    },
    'required': ['menuSection'],
    'additionalProperties': False
}


MENU_ITEMS_CREATION_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu items creation request',
    'description': 'Creation request for a menu item',
    'type': 'object',
    'properties': {
        'sectionId': {
            'description': 'The id of the section we are creating the item under',
            'type': 'integer'
        },
        'name': {
            'description': 'The name of the menu section',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu section',
            'type': 'string'
        },
        'keywords': KEYWORDS,
        'ingredients': INGREDIENTS,
        'imageSet': IMAGE_SET,
    },
    'required': ['sectionId', 'name', 'description', 'keywords',
                 'ingredients', 'imageSet'],
    'additionalProperties': False
}


MENU_ITEMS_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu items response',
    'description': 'Common response for menu items',
    'type': 'object',
    'properties': {
        'menuItems': {
            'description': 'The menu sections',
            'type': 'array',
            'items': MENU_ITEM
        }
    },
    'required': ['menuItems'],
    'additionalProperties': False
}


MENU_ITEM_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu item update request',
    'description': 'Update request for a menu item',
    'type': 'object',
    'properties': {
        'name': {
            'description': 'The name of the menu item',
            'type': 'string'
        },
        'description': {
            'description': 'The description of the menu item',
            'type': 'string'
        },
        'keywords': KEYWORDS,
        'ingredients': INGREDIENTS,
        'imageSet': IMAGE_SET
    },
    'anyOf': [
        {'required': ['name']},
        {'required': ['description']},
        {'required': ['keywords']},
        {'required': ['ingredients']},
        {'required': ['imageSet']}
    ],
    'additionalProperties': False
}


MENU_ITEM_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Menu item response',
    'description': 'Common response for menu item',
    'type': 'object',
    'properties': {
        'menuItem': MENU_ITEM
    },
    'required': ['menuItem'],
    'additionalProperties': False
}


PLATFORMS_WEBSITE_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Website platforms update request',
    'description': 'Request for updating the website platform',
    'type': 'object',
    'properties': {
        'subdomain': {
            'description': 'The subdomain of the website',
            'type': 'string',
        }
    },
    'anyOf': [
        {'required': ['subdomain']}
    ],
    'additionalProperties': False
}


PLATFORMS_WEBSITE_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Website platfrom response',
    'description': 'Common response for website platform',
    'type': 'object',
    'properties': {
        'platformsWebsite': PLATFORMS_WEBSITE
    },
    'required': ['platformsWebsite'],
    'additionalProperties': False
}


PLATFORMS_CALLCENTER_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Callcenter platforms update request',
    'description': 'Request for updating the callcenter platform',
    'type': 'object',
    'properties': {
        'phoneNumber': {
            'description': 'The phone number of the callcenter',
            'type': 'string',
        }
    },
    'anyOf': [
        {'required': ['phoneNumber']}
    ],
    'additionalProperties': False
}


PLATFORMS_CALLCENTER_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Callcenter platfrom response',
    'description': 'Common response for callcenter platform',
    'type': 'object',
    'properties': {
        'platformsCallcenter': PLATFORMS_CALLCENTER
    },
    'required': ['platformsCallcenter'],
    'additionalProperties': False
}


PLATFORMS_EMAILCENTER_UPDATE_REQUEST = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Emailcenter platforms update request',
    'description': 'Request for updating the emailcenter platform',
    'type': 'object',
    'properties': {
        'emailName': {
            'description': 'The email name of the emailcenter',
            'type': 'string',
        }
    },
    'anyOf': [
        {'required': ['emailName']}
    ],
    'additionalProperties': False
}


PLATFORMS_EMAILCENTER_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Emailcenter platfrom response',
    'description': 'Common response for emailcenter platform',
    'type': 'object',
    'properties': {
        'platformsEmailcenter': PLATFORMS_EMAILCENTER
    },
    'required': ['platformsEmailcenter'],
    'additionalProperties': False
}


WEBSHOP_INFO_RESPONSE = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Webshop info response',
    'description': 'Response for all info needed by a shop',
    'type': 'object',
    'properties': {
        'webshopInfo': WEBSHOP_INFO
    },
    'required': ['webshopInfo'],
    'additionalProperties': False
}
