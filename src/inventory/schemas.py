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
    'additionalPropertiers': False,
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
