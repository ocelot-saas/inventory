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


RESTAURANT_KEYWORDS = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Restaurant keywords',
    'description': 'The set of keywords for a restaurant',
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
        'keywords': RESTAURANT_KEYWORDS,
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
        'keywords': RESTAURANT_KEYWORDS,
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
        'keywords': RESTAURANT_KEYWORDS,
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
