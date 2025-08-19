from rara_meta_extractor.constants.data_classes import TEXT_BLOCKS, MetaField
TEXT_CLASSIFIER_SCHEMA = [
    {
        "name": MetaField.TEXT_TYPE,
        "item_restrictions": {
            "enum": TEXT_BLOCKS,
        },
        "list_restrictions": {
            "maxItems": 1,
            "minItems": 1
        }
    }
]

META_SCHEMA = [
    {
        "name": "title",
        "item_restrictions": {}
    },
    {
        "name": "original title",
        "item_restrictions": {}
    },
    {
        "name": "title part number",
        "item_restrictions": {}
    },
    {
        "name": "edition",
        "item_restrictions": {}
    },
    {
        "name": "publisher",
        "item_restrictions": {}
    },
    {
        "name": "publication year",
        "item_restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "publication place",
        "item_restrictions": {}
    },
    {
        "name": "manufacture name",
        "item_restrictions": {}
    },
    {
        "name": "manufacture place",
        "item_restrictions": {}
    },
    {
        "name": "manufacture year",
        "item_restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "distribution name",
        "item_restrictions": {}
    },
    {
        "name": "distribution place",
        "item_restrictions": {}
    },
    {
        "name": "distribution year",
        "item_restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "publication place",
        "item_restrictions": {}
    },
    {
        "name": "copyright year",
        "item_restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "country",
        "item_restrictions": {}
    },
    {
        "name": "isbn",
        "item_restrictions": {
            "maxLength": 13,
            "minLength": 13,
            "type": "integer"
        }
    },
    {
        "name": "issn",
        "item_restrictions": {
            "maxLength": 8,
            "minLength": 8,
            "type": "integer"
        }
    }
]

AUTHORS_SCHEMA = [
    {
        "name": "author",
        "item_restrictions": {}
    },
    {
        "name": "story adaptor",
        "item_restrictions": {}
    },
    {
        "name": "foreword author",
        "item_restrictions": {}
    },
    {
        "name": "translator",
        "item_restrictions": {}
    },
    {
        "name": "illustrator",
        "item_restrictions": {}
    },
    {
        "name": "editor",
        "item_restrictions": {}
    },
    {
        "name": "designer",
        "item_restrictions": {}
    },
    {
        "name": "photographer",
        "item_restrictions": {}
    },
    {
        "name": "language editor",
        "item_restrictions": {}
    }
]
