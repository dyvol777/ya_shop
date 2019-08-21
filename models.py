from gino import Gino

db = Gino()


class MyEnum(db.Enum):
    one = 'male'
    two = 'female'


relatives = db.Table('relatives',
                     db.Column('request_id', db.String, db.ForeignKey('Citizen.request_id')),
                     db.Column('first_id', db.Integer, db.ForeignKey('Citizen.citizen_id')),
                     db.Column('second_id', db.Integer, db.ForeignKey('Citizen.citizen_id'))
                     )


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.String)
    data = db.Column(db.String)


class Citizen(db.Model):
    __tablename__ = 'citizens'

    request_id = db.ForeignKey('Requests.id')
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
