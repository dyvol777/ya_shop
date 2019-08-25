from datetime import datetime
import json
import requests
ip = 'http://84.201.136.227:8080'

example = {
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
            "birth_date": "20.11.1986",
            "gender": "female",
            "relatives": []
        },

    ]
}


def post_all():
    r = requests.post(f'{ip}/imports', json=example)
    print(r.text)
    json.loads(r.text)
    return json.loads(r.text)['data']['import_id']


def test_get_all(id):
    r = requests.get(f'{ip}/imports/{id}/citizens/')
    print(r.text)


def make_patch(id):
    r = requests.patch(f'{ip}/imports/{id}/citizens/1',
                       json={"town": "Москва12",
                             "street": "Льва Толстого12",
                             "building": "16к7стр521",
                             "apartment": 12,
                             "name": "Иванов Иван Иванович21",
                             "birth_date": "2.12.1986",
                             "relatives": [3]
                             }
                       )
    print(r.text)


def test_get_birthdays(id):
    r = requests.get(f'{ip}/imports/{id}/citizens/birthdays')
    print(r.text)


def test_get_stat(id):
    r = requests.get(f'{ip}/imports/{id}/towns/stat/percentile/age')
    print(r.text)


def make_big_request():
    n = datetime.now()
    r = requests.post(f'{ip}/imports', json={"citizens": [
        {
            "citizen_id": i,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": [i]
        } for i in range(10**4)]
    }
                      )
    t = datetime.now() - n
    print(t)

    print(r)
    print(r.text)
    json.loads(r.text)
    return json.loads(r.text)['data']['import_id']


if __name__ == '__main__':
    t = datetime.now()
    id = post_all()
    test_get_all(id)
    test_get_birthdays(id)
    make_patch(id)
    test_get_all(id)
    test_get_birthdays(id)
    test_get_stat(id)
    print(datetime.now() - t)
