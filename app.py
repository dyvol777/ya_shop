import asyncio
from aiohttp import web
from gino.ext.aiohttp import Gino
import json
from jsonschema import validate
import numpy
import datetime

from models import Request, Citizen, Relatives
from settigs import *

routes = web.RouteTableDef()


def age(dob):
    today = datetime.date.today()
    years = today.year - dob.year

    try:
        birthday = datetime.date(today.year, dob.month, dob.day)
    except ValueError as e:
        if dob.month == 2 and dob.day == 29:
            birthday = datetime.date(today.year, 3, 1)
        else:
            raise e
    if today < birthday:
        years -= 1
    return years


@routes.post('/imports')
async def import_citizens(request):
    try:
        data = json.loads(request.data)
        validate(data, schema)

        relatives = []
        check = 0
        for citizen in data['citizens']:
            if len(citizen['relatives']) != 0:
                for f in citizen['relatives']:
                    if f == citizen['citizen_id']:
                        pass
                    elif (f, citizen['citizen_id'],) in relatives:
                        check -= 1
                    else:
                        check += 1
                    relatives.append((citizen['citizen_id'], f))
            citizen.pop('relatives')
        if check != 0:
            raise web.HTTPBadRequest()

        rq = await Request.create(data=request.data)
        for citizen in data['citizens']:
            await Citizen.create(**citizen, request_id=rq.id)
        for relation in relatives:
            await Relatives.create(first_id=await Citizen.selecet('id').
                                   where(Citizen.citizen_id == relation[0]
                                         and Citizen.request_id == rq.id).gino.first(),
                                   second_id=await Citizen.selecet('id').
                                   where(Citizen.citizen_id == relation[1]
                                         and Citizen.request_id == rq.id).gino.first(),
                                   request_id=rq.id)
        return web.HTTPCreated(body={'data': {'import_id': rq.id}})
    except:
        raise web.HTTPBadRequest()


@routes.patch('/imports/{import_id}/citizens/{citizen_id}')
async def modify_citizen(request):
    import_id = request.match_info['import_id']
    citizen_id = request.match_info['citizen_id']
    cz = await Citizen.query.where(Citizen.citizen_id == citizen_id and Citizen.request_id == import_id).gino.first()
    data = json.loads(request.data)
    rel = []
    if 'relatives' in data:
        Relatives.delete.where(Relatives.first_id == cz.id or Relatives.second_id == cz.id).gino.status()
        async for relation in data['relatives']:
            await Relatives.create(first_id=await Citizen.selecet('id').
                                   where(Citizen.citizen_id == relation
                                         and Citizen.request_id == import_id).gino.first(),
                                   second_id=cz.id,
                                   request_id=import_id)
            await Relatives.create(second_id=await Citizen.selecet('id').
                                   where(Citizen.citizen_id == relation
                                         and Citizen.request_id == import_id).gino.first(),
                                   first_id=cz.id,
                                   request_id=import_id)
        rel = data.pop('relatives')
    await cz.update(**request.data).apply()
    result = cz.to_dict()
    result['relatives'] = rel
    return web.json_response(result)


@routes.get('/imports/{import_id}/citizens/')
async def get_all_citizens_by_import_id(request):
    import_id = request.match_info['import_id']
    founding_citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()

    data = {'data': []}
    for c in founding_citizens:
        rel = await Relatives.join(Citizen.on(Citizen.id == Relatives.second_id)).select('citizen_id').where(Relatives.first_id == c.id).gino.all()
        cit_dict = c.to_dict()
        cit_dict['relatives'] = rel
        cit_dict.pop('id')
        data['data'].append(cit_dict)
    return web.json_response(json.dumps(data))


@routes.get('/imports/{import_id}/citizens/birthdays')
async def get_birthdays(request):
    import_id = request.match_info['import_id']
    result = {
        "1": [],
        "2": [],
        "3": [],
        "4": [],
        "5": [],
        "6": [],
        "7": [],
        "8": [],
        "9": [],
        "10": [],
        "11": [],
        "12": []
    }

    founding_citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()
    for citizen in founding_citizens:
        if citizen.relatives:
            pass  # todo:make it work
    return web.json_response()


@routes.get('/imports/{import_id}/towns/stat/percentile/age')
async def get_stat(request):
    import_id = request.match_info['import_id']
    towns = await Citizen.select('town').distinct(Citizen.town). \
        where(Citizen.request_id == import_id).gino.all()
    result = []
    for town in towns:
        birthdays = await Citizen.select('birth_date'). \
            where(Citizen.town == town[0] and Citizen.request_id == import_id).gino.all()
        ages = [age(birth[0]) for birth in birthdays]
        p50, p75, p99 = numpy.percentile(ages, [50, 75, 99])
        result.append({'town': town[0], 'p50': p50, 'p75': p75, 'p99': p99})
    return web.json_response({'data': result})


def main():
    db = Gino()
    app = web.Application(middlewares=[db])
    app['config'] = {'dsn': postgre_url}
    db.init_app(app)
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
