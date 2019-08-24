from models import *
from datetime import datetime
import numpy
import json
import requests
from settigs import example


async def get_all(import_id):
    await db.set_bind(postgre_url)
    founding_citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()
    data = {'data': [c.to_dict() for c in founding_citizens]}
    print(data)


def test_get_all():
    r = requests.get('http://localhost:8080/imports/14/citizens/birthdays')
    print(r)


def post_all():
    r = requests.post('http://localhost:8080/imports', json=example)
    print(r)


async def main():
    await db.set_bind(postgre_url)
    q = await Citizen.select('id').where(Citizen.citizen_id == 1 and Citizen.request_id == 1).gino.first()
    rq = await Request.create(data='123')
    id = 1

    rel = await Citizen.join(Relatives, Citizen.id == Relatives.first_id).select().where(Citizen.id == id).gino.all()
    for i in rel:
        a = i.second_id
        pass


def make_patch():
    r = requests.patch('http://localhost:8080/imports/1/citizens/1',
                       json={"town": "Москва12",
                             "street": "Льва Толстого12",
                             "building": "16к7стр521",
                             "apartment": 12,
                             "name": "Иванов Иван Иванович21",
                             "birth_date": "2.12.1986",
                             "relatives": []
                             }
                       )
    print(r)


def make_big_request():
    n = datetime.now()
    r = requests.post('http://localhost:8080/imports', json={"citizens": [
        {
            "citizen_id": i,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "apartment": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "26.12.1986",
            "gender": "male",
            "relatives": []
        } for i in range(10**4)]
    }
                      )
    t = datetime.now() - n
    print(r)
    print(t)
    pass


if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(main())
    test_get_all()
