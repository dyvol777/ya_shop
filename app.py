from aiohttp import web
import json
from jsonschema import validate
import numpy
import datetime
import logging

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
            if citizen['birth_date'] > datetime.date.today():
                raise web.HTTPBadRequest()
        if check != 0:
            raise web.HTTPBadRequest()

        rq = await Request.create(date=datetime.datetime.now())

        n2 = datetime.datetime.now()
        await Citizen.insert().gino.all(*[dict(**citizen, request_id=rq.id) for citizen in data['citizens']])
        citizens = {c.citizen_id: c.id for c in await Citizen.query.where(Citizen.request_id == rq.id).gino.all()}
        t2 = datetime.datetime.now() - n2
        logging.debug('Creating all citizens on time: {}'.format(t2))

        await Relatives.insert().gino.all(
            *[dict(first_id=citizens[relation[0]], second_id=citizens[relation[1]], request_id=rq.id) for relation in
              relatives])

        t = datetime.datetime.now() - n
        logging.debug('All request completed on time: {}'.format(t))
        return web.HTTPCreated(body=json.dumps({'data': {'import_id': rq.id}}))
    except Exception as e:
        logging.exception('Post data exception')
        raise web.HTTPBadRequest()


@routes.patch('/imports/{import_id}/citizens/{citizen_id}')
async def modify_citizen(request):
    try:
        import_id = int(request.match_info['import_id'])
        citizen_id = int(request.match_info['citizen_id'])
        data = await request.json()
        validate(data, patch_schem)

        cz = await Citizen.query.where(Citizen.citizen_id == citizen_id).where(
            Citizen.request_id == import_id).gino.first()
        if cz is None:
            raise web.HTTPBadRequest()

        rel = []
        if 'birth_date' in data:
            data['birth_date'] = datetime.datetime.strptime(data['birth_date'], '%d.%m.%Y').date()
            if data['birth_date'] > datetime.date.today():
                raise web.HTTPBadRequest()
        if 'relatives' in data:
            await Relatives.delete.where(Relatives.first_id == cz.id).gino.status()
            await Relatives.delete.where(Relatives.second_id == cz.id).gino.status()
            citizens = {c.citizen_id: c.id for c in
                        await Citizen.query.where(Citizen.request_id == import_id).gino.all()}
            relatives = []
            for relation in data['relatives']:
                relatives.append(dict(first_id=citizens[relation], second_id=cz.id, request_id=import_id))
                relatives.append(dict(first_id=cz.id, second_id=citizens[relation], request_id=import_id))
            await Relatives.insert().gino.all(*relatives)
            rel = data.pop('relatives')
        await cz.update(**data).apply()
        result = cz.to_dict()
        result['relatives'] = rel
        result.pop('id')
        result.pop('request_id')
        result['birth_date'] = result['birth_date'].strftime("%d.%m.%Y")
        return web.json_response(result)
    except Exception as e:
        logging.exception('Patch exception')
        raise web.HTTPBadRequest()


@routes.get('/imports/{import_id}/citizens/')
async def get_all_citizens_by_import_id(request):
    try:
        import_id = request.match_info['import_id']
        founding_citizens = await Citizen.query.where(Citizen.request_id == int(import_id)).gino.all()

        relatives = await Citizen.join(Relatives, Citizen.id == Relatives.second_id).select(). \
            where(Relatives.request_id == int(import_id)).gino.all()

        true_relatives = {}
        for rel in relatives:
            if rel.first_id in true_relatives:
                true_relatives[rel.first_id].append(rel.citizen_id)
            else:
                true_relatives[rel.first_id] = [rel.citizen_id]

        data = {'data': []}
        for c in founding_citizens:
            cit_dict = c.to_dict()
            cit_dict.pop('id')
            cit_dict.pop('request_id')
            cit_dict['birth_date'] = cit_dict['birth_date'].strftime("%d.%m.%Y")
            if c.id in true_relatives:
                cit_dict['relatives'] = true_relatives[c.id]
            else:
                cit_dict['relatives'] = []

            data['data'].append(cit_dict)
        return web.json_response(data=data)
    except Exception as e:
        logging.exception('Get all exception')
        raise web.HTTPBadRequest()


@routes.get('/imports/{import_id}/citizens/birthdays')
async def get_birthdays(request):
    try:
        import_id = int(request.match_info['import_id'])
        citizens = {c.id: c.birth_date for c in
                    await Citizen.query.where(Citizen.request_id == import_id).gino.all()}

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

        ids = await Relatives.join(Citizen, Citizen.id == Relatives.first_id).select().where(
            Relatives.request_id == import_id).gino.all()
        for cit in ids:
            month = citizens[cit.second_id].month
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
    except Exception as e:
        logging.exception('Get birthdays exception')
        raise web.HTTPBadRequest()


@routes.get('/imports/{import_id}/towns/stat/percentile/age')
async def get_stat(request):
    try:
        import_id = int(request.match_info['import_id'])

        citizens = await Citizen.query.where(Citizen.request_id == import_id).gino.all()
        town_stat = {}
        for citizen in citizens:
            if citizen.town in town_stat:
                town_stat[citizen.town].append(age(citizen.birth_date))
            else:
                town_stat[citizen.town] = [age(citizen.birth_date)]

        result = []
        for k, v in town_stat.items():
            p50, p75, p99 = numpy.percentile(v, [50, 75, 99], interpolation='linear')
            result.append({'town': k, 'p50': p50, 'p75': p75, 'p99': p99})
        return web.json_response({'data': result})
    except Exception as e:
        logging.exception('Get stat exception')
        raise web.HTTPBadRequest()


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application(middlewares=[db], client_max_size=1024 ** 3)
    db.init_app(app, config={'password': 'postgres',
                             'database': 'shop'})
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
