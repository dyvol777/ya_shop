from gino import Gino
import asyncio
from settigs import *

db = Gino()


class MyEnum(db.Enum):
    one = 'male'
    two = 'female'


class Relatives(db.Model):
    __tablename__ = 'relatives'

    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'))
    first_id = db.Column(db.Integer, db.ForeignKey('citizens.id'))
    second_id = db.Column(db.Integer, db.ForeignKey('citizens.id'))


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String())


class Citizen(db.Model):
    __tablename__ = 'citizens'

    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'))
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    citizen_id = db.Column(db.Integer, nullable=False)
    town = db.Column(db.String(256), nullable=False)
    street = db.Column(db.String(256), nullable=False)
    building = db.Column(db.String(256), nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(MyEnum(name='gender'))

    _pk = db.Index('requestAndCitizen', 'request_id', 'citizen_id', unique=True)


async def main():
    await db.set_bind(postgre_url)
    await db.gino.create_all()
    await db.pop_bind().close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
