postgre_url = 'postgresql://postgres:postgres@localhost:5432/shop'

citizen_schem = {
    "type": "object",
    "properties": {
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
                       },  # TODO: make date validate
        "gender": {
            "type": "string",
            "enum": ["male", "female"]
        },
        "relatives": {
            "type": "array",
            "items": {"type": "integer"}
        },
    },
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

ex = {
    "citizens": [
        {
            "citizen_id": 1,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [2]
        },
        {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Сергей Иванович",
            "birth_date": "01.04.1997",
            "gender": "male",
            "relatives": [1]
        },
        {
            "citizen_id": 3,
            "town": "Керчь",
            "street": "Иосифа Бродского",
            "building": "2",
            "apartment": 11,
            "name": "Романова Мария Леонидовна",
            "birth_date": "40.11.1986",
            "gender": "female",
            "relatives": []
        },

    ]
}

if __name__ == '__main__':
    from jsonschema import validate

    validate(ex, schema)
