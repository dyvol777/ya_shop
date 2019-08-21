from gino import Gino
import asyncio
from settigs import *

db = Gino()


class MyEnum(db.Enum):
    one = 'male'
    two = 'female'


relatives = db.Table('relatives',
                     db.Column('request_id', db.String, db.ForeignKey('citizens.request_id')),
                     db.Column('first_id', db.Integer, db.ForeignKey('citizens.citizen_id')),
                     db.Column('second_id', db.Integer, db.ForeignKey('citizens.citizen_id'))
                     )


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSONB())


class Citizen(db.Model):
    __tablename__ = 'citizens'

    request_id = db.ForeignKey('requests.id')
    citizen_id = db.Column(db.Integer, nullable=False)
    town = db.Column(db.String(256), nullable=False)
    street = db.Column(db.String(256), nullable=False)
    building = db.Column(db.String(256), nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum())

    relatives: db.relationship("Citizen", secondary=relatives)

    _pk = db.PrimaryKeyConstraint('request_id', 'citizen_id', name='requestAndCitizen')


async def main():
    await db.set_bind(postgre_url)
    await db.gino.create_all()
    await db.pop_bind().close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
