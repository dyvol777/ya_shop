import asyncio
from aiohttp import web
import json
from jsonschema import validate
import numpy
from datetime import date

from models import Request, Citizen, db
from utils import age
from settigs import *

routes = web.RouteTableDef()


@routes.post('/imports')
async def import_citizens(request):
    try:
        data = json.loads(request.data)
        validate(data, schema)
        rq = await Request.create(data=request.data)
        for citizen in data['citizens']:
            await Citizen.create(**citizen, request_id=rq.id)  # todo: fix relatives
        return web.HTTPCreated(body={'data': {'import_id': rq.id}})
    except:
        raise web.HTTPBadRequest()


@routes.patch('/imports/{import_id}/citizens/{citizen_id}')
async def modify_citizen(request):
    import_id = request.match_info['import_id']
    citizen_id = request.match_info['citizen_id']
    cz = await Citizen.query.where(Citizen.citizen_id == citizen_id and Citizen.request_id == import_id).gino.first()
    await cz.update(**request.data).apply() # todo: fix relatives
    return web.json_response(cz.__dict__)


@routes.get('/imports/{import_id}/citizens/')
async def get_all_citizens_by_import_id(request):
    import_id = request.match_info['import_id']
    founding_citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()
    data = {'data': [c.__dict__ for c in founding_citizens]}
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
    await db.set_bind(postgre_url)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
