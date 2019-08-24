import asyncio
from aiohttp import web
from gino.ext.aiohttp import Gino
import json
from jsonschema import validate
import numpy
import datetime

from models import Request, Citizen, Relatives, db
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
        data = await request.json()
        n = datetime.datetime.now()
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
            citizen['birth_date'] = datetime.datetime.strptime(citizen['birth_date'], '%d.%m.%Y').date()
        if check != 0:
            raise web.HTTPBadRequest()

        rq = await Request.create(date=datetime.datetime.now())
        citizens = {}
        n2 = datetime.datetime.now()
        for citizen in data['citizens']:
            cz = await Citizen.create(**citizen, request_id=rq.id)
            citizens[cz.citizen_id] = cz.id

        t2 = datetime.datetime.now() - n2
        print(t2)
        for relation in relatives:
            f_id = citizens[relation[0]]
            s_id = citizens[relation[1]]
            await Relatives.create(first_id=f_id,
                                   second_id=s_id,
                                   request_id=rq.id)
        t = datetime.datetime.now() - n
        print(t)
        return web.HTTPCreated(body=json.dumps({'data': {'import_id': rq.id}}))
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest()


@routes.patch('/imports/{import_id}/citizens/{citizen_id}')
async def modify_citizen(request):
    try:
        import_id = int(request.match_info['import_id'])
        citizen_id = int(request.match_info['citizen_id'])
        data = await request.json()
        print(Citizen.query.where(Citizen.citizen_id == citizen_id).where(Citizen.request_id == import_id))
        cz = await Citizen.query.where(Citizen.citizen_id == citizen_id).where(
            Citizen.request_id == import_id).gino.first()
        if cz is None:
            raise web.HTTPBadRequest()

        rel = []
        if 'birth_date' in data:
            data['birth_date'] = datetime.datetime.strptime(data['birth_date'], '%d.%m.%Y').date()
        if 'relatives' in data:
            await Relatives.delete.where(Relatives.first_id == cz.id).gino.status()
            await Relatives.delete.where(Relatives.second_id == cz.id).gino.status()
            for relation in data['relatives']:
                relative_id = await Citizen.select('id').where(Citizen.citizen_id == relation). \
                    where(Citizen.request_id == import_id).gino.first()
                await Relatives.create(first_id=relative_id[0],
                                       second_id=cz.id,
                                       request_id=import_id)
                await Relatives.create(second_id=relative_id[0],
                                       first_id=cz.id,
                                       request_id=import_id)
            rel = data.pop('relatives')
        await cz.update(**data).apply()
        result = cz.to_dict()
        result['relatives'] = rel
        result.pop('id')
        result.pop('request_id')
        result['birth_date'] = result['birth_date'].strftime("%d.%m.%Y")
        return web.json_response(result)
    except Exception as e:
        print(e)
        raise web.HTTPBadRequest()


@routes.get('/imports/{import_id}/citizens/')
async def get_all_citizens_by_import_id(request):
    try:
        import_id = request.match_info['import_id']
        founding_citizens = await Citizen.query.where(Citizen.request_id == int(import_id)).gino.all()

        data = {'data': []}
        for c in founding_citizens:
            rel = await Citizen.join(Relatives, Citizen.id == Relatives.first_id).select().where(
                Citizen.id == c.id).gino.all()
            cit_dict = c.to_dict()
            cit_dict.pop('id')
            cit_dict.pop('request_id')
            cit_dict['birth_date'] = cit_dict['birth_date'].strftime("%d.%m.%Y")

            family = []
            for f in rel:
                cit_id = await Citizen.select('citizen_id').where(Citizen.id == int(f.second_id)).gino.first() # todo: remove second request
                family.append(cit_id[0])
            cit_dict['relatives'] = family

            data['data'].append(cit_dict)
        return web.json_response(data=data)
    except:
        raise web.HTTPBadRequest


@routes.get('/imports/{import_id}/citizens/birthdays')
async def get_birthdays(request):
    try:
        import_id = int(request.match_info['import_id'])
        ids = await Relatives.join(Citizen, Citizen.id == Relatives.first_id).select().where(
            Relatives.request_id == import_id).gino.all()
        result = {
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
            6: {},
            7: {},
            8: {},
            9: {},
            10: {},
            11: {},
            12: {}
        }

        for cit in ids:
            cz = await Citizen.query.where(Citizen.id == cit.second_id).gino.first() # todo: second join and don't need second request
            month = cz.birth_date.month
            if cit.citizen_id in result[month]:
                result[month][cit.citizen_id] += 1
            else:
                result[month][cit.citizen_id] = 1
        stat = {}
        for month, d in result.items():
            stat[str(month)] = []
            for k, v in d.items():
                stat[str(month)].append({"citizen_id": k, "presents": v})

        return web.json_response({'data': stat})
    except:
        raise web.HTTPBadRequest


@routes.get('/imports/{import_id}/towns/stat/percentile/age')
async def get_stat(request):
    try:
        import_id = int(request.match_info['import_id'])
        towns = await Citizen.select('town').distinct(Citizen.town). \
            where(Citizen.request_id == import_id).gino.all()
        result = []
        for town in towns:
            birthdays = await Citizen.select('birth_date'). \
                where(Citizen.town == town[0]).where(Citizen.request_id == import_id).gino.all()
            ages = [age(birth[0]) for birth in birthdays]
            p50, p75, p99 = numpy.percentile(ages, [50, 75, 99])
            result.append({'town': town[0], 'p50': p50, 'p75': p75, 'p99': p99})
        return web.json_response({'data': result})
    except:
        raise web.HTTPBadRequest


def main():
    app = web.Application(middlewares=[db], client_max_size=1024 ** 3)
    db.init_app(app, config={'password': 'postgres',
                             'database': 'shop'})
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
