"""Schema for the inventory APIs objects."""


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
    'definitions': {
        'time': {
            'description': 'A time in a day',
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
        },
        'interval': {
            'description': 'A daily opening interval',
            'type': 'object',
            'properties': {
                'start': {'$ref': '#definitions/time'},
                'end': {'$ref': '#definitions/time'}
            },
            'required': ['start', 'end'],
            'additionalProperties': False
        },
    },
    'type': 'object',
    'properties': {
        'weekday': {'$ref': '#definitions/interval'},
        'saturday': {'$ref': '#definitions/interval'},
        'sunday': {'$ref': '$definitions/interval'}
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
    },
    'required': ['id', 'timeCreatedTs', 'name', 'description', 'keywords',
                 'address', 'openingHours'],
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
        },
        'restaurant': RESTAURANT,
    },
    'required': ['id', 'timeCreatedTs', 'restaurant'],
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
    },
    'required': ['name', 'description', 'keywords', 'address', 'openingHours'],
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
