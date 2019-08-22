from models import *
from datetime import date
import numpy
import json
import requests


async def perc(import_id):
    await db.set_bind(postgre_url)

    towns = await Citizen.select('town').distinct(Citizen.town). \
        where(Citizen.request_id == import_id).gino.all()
    result = []
    for town in towns:
        birthdays = await Citizen.select('birth_date'). \
            where(Citizen.town == town[0] and Citizen.request_id == import_id).gino.all()
        ages = [age(birth[0]) for birth in birthdays]
        p50, p75, p99 = numpy.percentile(ages, [50, 75, 99])
        result.append({'town': town[0], 'p50': p50, 'p75': p75, 'p99': p99})
    print(result)


async def get_all(import_id):
    await db.set_bind(postgre_url)
    founding_citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()
    data = {'data': [c.to_dict() for c in founding_citizens]}
    print(data)


if __name__ == '__main__':
    r = requests.get('http://localhost:8080/imports/1/citizens/')
    print(r)
