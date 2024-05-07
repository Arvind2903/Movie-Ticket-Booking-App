from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from .database import db


ma = Marshmallow()


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))
    def __init__(self, name):
        super().__init__()
        self.name = name


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.Integer(), nullable=True)
    admin = db.Column(db.Boolean(), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), nullable=False, unique=True) # Used to generate auth token
    theatre = db.relationship('Theatre', cascade='all, delete-orphan', back_populates='theatre_admin')
    movie = db.relationship('Movie', cascade='all, delete-orphan', back_populates='movie_admin')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    activity = db.relationship('Activity', cascade='all, delete-orphan', back_populates='active_user')
    def __init__(self, email, name, phone, admin , password, username, active, fs_uniquifier):
        self.username = username
        self.email = email
        self.name = name
        self.phone = phone
        self.admin = admin
        self.active = active
        self.fs_uniquifier = fs_uniquifier
        self.password = password


class Theatre(db.Model):
    __tablename__ = 'theatre'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text(), nullable=False)
    wheelchair = db.Column(db.Boolean(), nullable=False)
    parking = db.Column(db.Boolean(), nullable=False)
    fnb = db.Column(db.Boolean(), nullable=False)
    total_seats = db.Column(db.Integer(), nullable=False)
    max_shows = db.Column(db.Integer(), nullable=False)
    img = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    theatre_admin = db.relationship('User', back_populates='theatre', lazy='subquery')
    def __init__(self, name, address, wheelchair, parking, fnb, img, total_seats, max_shows, user_id):
        self.name = name
        self.address = address
        self.wheelchair = wheelchair
        self.parking = parking
        self.fnb = fnb
        self.img = img
        self.total_seats = total_seats
        self.max_shows = max_shows
        self.user_id = user_id


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(25), nullable=False)
    subtitles = db.Column(db.String(25), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    genre = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    runtime = db.Column(db.Integer(), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    img = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    movie_admin = db.relationship('User', back_populates='movie', lazy='subquery')
    def __init__(self, name, date, subtitles, price, genre, rating, img, runtime, language,user_id):
        self.name = name
        self.date = date
        self.subtitles = subtitles
        self.price = price
        self.genre = genre
        self.rating = rating
        self.runtime = runtime
        self.img = img
        self.language = language
        self.user_id = user_id


class MovieSchedule(db.Model):
    __tablename__ = 'movie_schedule'
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer(), db.ForeignKey('theatre.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer(), db.ForeignKey('movie.id', ondelete='CASCADE'))
    time = db.Column(db.String(10))
    def __init__(self, theatre_id, movie_id, time):
        self.theatre_id = theatre_id
        self.movie_id = movie_id
        self.time = time


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    theatre_id = db.Column(db.Integer(), db.ForeignKey('theatre.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer(), db.ForeignKey('movie.id', ondelete='CASCADE'))
    date = db.Column(db.String(25))
    time = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime())
    number_of_tickets = db.Column(db.Integer())
    def __init__(self, user_id, theatre_id, movie_id, date, time, timestamp, number_of_tickets):
        self.user_id = user_id
        self.theatre_id = theatre_id
        self.movie_id = movie_id
        self.date = date
        self.time = time
        self.timestamp = timestamp
        self.number_of_tickets = number_of_tickets


class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime())
    active_user = db.relationship('User', back_populates='activity')
    def __init__(self, activity, timestamp, user_id):
        self.activity = activity
        self.timestamp = timestamp
        self.user_id = user_id


class MovieSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    date = fields.Str()
    subtitles = fields.Str()
    total_seats = fields.Int()
    filled_seats = fields.Int()
    genre = fields.Str()
    rating =  fields.Float()
    runtime = fields.Int()
    price =  fields.Int()
    img = fields.Str()
    language = fields.Str()
    theatre_id = fields.Int()
    user_id = fields.Int()
    class Meta:
        include_fk = True
        include_relationships = True


class TheatreSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    address = fields.Str()
    cancellation = fields.Bool()
    wheelchair = fields.Bool()
    parking = fields.Bool()
    fnb = fields.Bool()
    img = fields.Str()
    max_shows = fields.Int()
    total_seats = fields.Str()
    user_id = fields.Int()
    class Meta:
        include_fk = True
        include_relationships = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    email = fields.Str()
    name = fields.Str()
    phone = fields.Int()
    admin = fields.Bool()
    password = fields.Str()
    username = fields.Str()
    theatres = fields.Nested(TheatreSchema, many=True)
    movies = fields.Nested(MovieSchema, many=True)
    class Meta:
        include_fk = True
        include_relationships = True


class MovieScheduleSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    theatre_id = fields.Int()
    movie_id = fields.Int()
    time = fields.Str()
    class Meta:
        include_fk = True
        include_relationships = True


class TicketSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    theatre_id = fields.Int()
    movie_id = fields.Int()
    date = fields.Str()
    time = fields.Str()
    timestamp = fields.Str()
    filled_seats = fields.Int()
    class Meta:
        include_fk = True
        include_relationships = True


class ActivitySchema(ma.SQLAlchemyAutoSchema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    activity = fields.Str()
    timestamp = fields.Str()
    class Meta:
        include_fk = True
        include_relationships = True


activity_schema = ActivitySchema()
ticket_schema = TicketSchema()
movie_schedule_schema = MovieScheduleSchema()
movie_schedules_schema = MovieScheduleSchema(many=True)
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
theatre_schema = TheatreSchema()
theatres_schema = TheatreSchema(many=True)
user_schema = UserSchema()


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
