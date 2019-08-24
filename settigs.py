postgre_url = 'postgresql://postgres:postgres@localhost:5432/shop'

props = {
        "citizen_id": {"type": "integer"},
        "town": {"type": "string",
                 "minLength": 1,
                 "maxLength": 256
                 },
        "street": {"type": "string",
                   "minLength": 1,
                   "maxLength": 256},
        "building": {"type": "string",
                     "minLength": 1,
                     "maxLength": 256},
        "apartment": {"type": "integer"},
        "name": {"type": "string",
                 "minLength": 1,
                 "maxLength": 256},
        "birth_date": {"type": "string",
                       "format": "date"
                       },
        "gender": {
            "type": "string",
            "enum": ["male", "female"]
        },
        "relatives": {
            "type": "array",
            "items": {"type": "integer"}
        },
    }

citizen_schem = {
    "type": "object",
    "properties": props,
    "required": [
        "citizen_id",
        "town",
        "street",
        "building",
        "apartment",
        "name",
        "birth_date",
        "gender",
        "relatives",
    ]
}

patch_schem = {
    "type": "object",
    "properties": props
}

schema = {
    "description": "Schema validating info",
    "type": "object",
    "properties": {
        "citizens": {
            "description": "Schema validating info",
            "type": "array",
            "items": citizen_schem,
        }
    },
    "required": ["citizens"]
}
