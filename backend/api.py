import datetime
from flask import request, jsonify
from flask_restful import Resource
from . import models
from flask_security import current_user, auth_required, logout_user, roles_required
import hashlib
import os
import numpy as np
from . import tasks
from jinja2 import Template
from email_validator import validate_email, EmailNotValidError
from . import cache


mainDirectory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
imgSaveDirectory = os.path.join(mainDirectory, 'frontend', "src", "assets", "images")
graphSaveDirectory = os.path.join(mainDirectory, 'frontend', "src", "assets", "graphs")
if not os.path.exists(imgSaveDirectory):
    os.makedirs(imgSaveDirectory)
if not os.path.exists(graphSaveDirectory):
    os.makedirs(graphSaveDirectory)


# To SignUp
class SignUpApi(Resource):

    #Invalid Requests
    def get(self):
        return "", "404 Invalid Request"

    def put(self):
        return "", "404 Invalid Request"

    def delete(self):
        return "", "404 Invalid Request"

    # Signing up User
    def post(self):
        username = request.json['username']
        email = request.json['email']
        admin = request.json['admin']
        try:
            v = validate_email(email)
            email = v["email"]
        except EmailNotValidError as e:
            return "", "406 {e}".format(e=str(e))
        name = request.json['name']
        phone = request.json['phone']
        password = request.json['password']
        username_val = models.User.query.filter_by(username=username).first()
        if username_val:
            return "", "405 Username Already Exists"
        email_val = models.User.query.filter_by(email=email).first()
        if email_val:
            return "", "404 Email Already Exists"

        user = models.User(email=email, name=name, phone=phone, admin=admin, password=password, username=username,
                           active=True, fs_uniquifier = hashlib.md5(email.encode('utf-8')).hexdigest())
        if admin:
            user.roles.append(models.Role(name='Admin'))
        models.db.session.add(user)
        models.db.session.commit()

        with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                               'WelcomeTemplate.html')) as file_:
            template = Template(file_.read())
            message = template.render(user=user)
        tasks.sendEmail(to_address=email, subject="Welcome to MovieBuddy", message=message, attachments=[])
        return "", "200 Successfully Signed Up"

# For User
class UserApi(Resource):

    # Getting logged in user
    @auth_required('token')
    def get(self):
        activity = models.Activity(user_id=current_user.id, activity='login', timestamp=datetime.datetime.today())
        models.db.session.add(activity)
        models.db.session.commit()
        return models.user_schema.jsonify(current_user)

    # To delete the user profile
    @auth_required('token')
    def delete(self):
        user = models.User.query.get(current_user.id)
        models.db.session.delete(user)
        activities = models.Activity.query.filter_by(user_id=current_user.id).all()
        if activities:
            for activity in activities:
                models.db.session.delete(activity)
        tickets = models.Ticket.query.filter_by(user_id=current_user.id).all()
        if tickets:
            for ticket in tickets:
                models.db.session.delete(ticket)
        theatres = models.Theatre.query.filter_by(user_id=current_user.id).all()
        if theatres:
            for theatre in theatres:
                os.remove(theatre.img)
                models.db.session.delete(theatre)
        movies = models.Movie.query.filter_by(user_id=current_user.id).all()
        if movies:
            for movie in movies:
                os.remove(movie.img)
                models.db.session.delete(movie)
        role = models.UserRoles.query.filter_by(user_id=current_user.id).first()
        if role:
            models.db.session.delete(role)
        models.db.session.commit()
        return "", "200 User Deleted Successfully"

    # Editing profile
    @auth_required('token')
    def put(self):
        username = request.json['username']
        name = request.json['name']
        phone = request.json['phone']
        user = models.User.query.get(current_user.id)
        user.username = username
        user.name = name
        user.phone = phone
        models.db.session.commit()
        return models.user_schema.jsonify(user)

    # Invalid requests
    def post(self):
        return "", "404 Invalid Request"


# For Theatre
class TheatreApi(Resource):

    # Viewing a particular theatre
    @auth_required('token')
    def get(self, theatre_id):
        theatre = models.Theatre.query.get(theatre_id)
        return models.theatre_schema.jsonify(theatre)

    # Adding a theatre
    @auth_required('token')
    @roles_required('Admin')
    def post(self):
        name = request.form.get('name')
        address = request.form.get('address')
        wheelchair = request.form.get('wheelchair')=='true'
        parking = request.form.get('parking')=='true'
        fnb = request.form.get('fnb')=='true'
        total_seats = request.form.get('total_seats')
        max_shows = request.form.get('max_shows')
        image = request.files['image']
        theatre = models.Theatre(name=name, address=address, wheelchair=wheelchair, parking=parking, fnb=fnb,
                                 img='',total_seats=total_seats , max_shows=max_shows, user_id=current_user.id)
        models.db.session.add(theatre)
        models.db.session.commit()
        image.save(os.path.join(imgSaveDirectory, (str(theatre.name) + ".png")))
        theatre.img = os.path.join(imgSaveDirectory, str(theatre.name) + ".png")
        models.db.session.commit()
        activity = models.Activity(user_id=current_user.id, activity='added theatre',
                                   timestamp=datetime.datetime.today())
        models.db.session.add(activity)
        models.db.session.commit()
        return "", "200 Theatre Successfully Added"

    # Editing an existing theatre
    @auth_required('token')
    @roles_required('Admin')
    def put(self, theatre_id):
        theatre = models.Theatre.query.get(theatre_id)
        name = request.form.get('name')
        address = request.form.get('address')
        wheelchair = request.form.get('wheelchair') == 'true'
        parking = request.form.get('parking') == 'true'
        fnb = request.form.get('fnb') == 'true'
        total_seats = request.form.get('total_seats')
        if "image" in request.files:
            image = request.files['image']
            os.remove(os.path.join(imgSaveDirectory, str(name) + ".png"))
            image.save(os.path.join(imgSaveDirectory, str(name) + ".png"))
        theatre.name = name
        theatre.address = address
        theatre.wheelchair = wheelchair
        theatre.parking = parking
        theatre.fnb = fnb
        theatre.total_seats = total_seats
        models.db.session.commit()
        return "", "200 Theatre Successfully Edited"

    # Deleting an existing theatre
    @auth_required('token')
    @roles_required('Admin')
    def delete(self, theatre_id):
        theatre = models.Theatre.query.get(theatre_id)
        os.remove(os.path.join(imgSaveDirectory, str(theatre.name) + ".png"))
        models.db.session.delete(theatre)
        schedules = models.MovieSchedule.query.filter_by(theatre_id=theatre_id).all()
        if schedules:
            for schedule in schedules:
                models.db.session.delete(schedule)
        tickets = models.Ticket.query.filter_by(theatre_id=theatre_id).all()
        if tickets:
            for ticket in tickets:
                models.db.session.delete(ticket)
        models.db.session.commit()
        return "", "200 Theatre Successfully Removed"


# For Theatres
class TheatresApi(Resource):

    # Get all theatres in app
    @auth_required('token')
    @cache.cached(timeout=10)
    def get(self):
        theatres = models.Theatre.query.all()
        return models.theatres_schema.dump(theatres)

    # Get all theatres managed by the current user
    @auth_required('token')
    @roles_required('Admin')
    def post(self):
        theatres = models.Theatre.query.filter_by(user_id=current_user.id)
        return models.theatres_schema.dump(theatres)

    # Get all theatres where the movie is run
    @auth_required('token')
    def put(self, movie_id):
        schedules = models.MovieSchedule.query.filter_by(movie_id=movie_id)
        theatre_ids = list(set([x.theatre_id for x in schedules]))
        theatres = []
        for theatre_id in theatre_ids:
            theatres.append(models.Theatre.query.get(theatre_id))
        return models.theatres_schema.dump(theatres)

    # Invalid requests
    def delete(self):
        return "", "404 Invalid Request"


# For Movie
class MovieApi(Resource):

    # Viewing a particular movie
    @auth_required('token')
    def get(self, movie_id):
        movie = models.Movie.query.get(movie_id)
        return models.movie_schema.jsonify(movie)

    # Adding a new movie
    @auth_required('token')
    @roles_required('Admin')
    def post(self):
        name = request.form.get('name')
        date = request.form.get('date')
        subtitles = request.form.get('subtitles')
        price = request.form.get('price')
        genre = request.form.get('genre')
        rating = request.form.get('rating')
        runtime = request.form.get('runtime')
        image = request.files['image']
        theatres = request.form.get('theatres').split(',')
        language = request.form.get('language')
        movie = models.Movie(name=name, date=date, subtitles=subtitles,price=price, genre=genre, language=language,
                             img='', rating=rating, runtime=runtime, user_id=current_user.id)
        models.db.session.add(movie)
        models.db.session.commit()
        image.save(os.path.join(imgSaveDirectory, str(name) + ".png"))
        movie.img = os.path.join(imgSaveDirectory, str(name) + ".png")
        models.db.session.commit()
        for theatre_id in theatres:
            theatre = models.Theatre.query.get(theatre_id)
            times = np.linspace(10,22,theatre.max_shows)
            times = [round(item, 2) for item in times]
            def numToTime(n):
                h = int(n // 1)
                m = n % 1
                mins = int(m * 60)
                if mins == 0:
                    mins = '00'
                return str(h) + ":" + str(mins)
            times = list(map(numToTime, times))
            for time in times:
                movie_schedule = models.MovieSchedule(theatre_id=theatre_id, movie_id=movie.id, time=time)
                models.db.session.add(movie_schedule)
                models.db.session.commit()
        activity = models.Activity(user_id=current_user.id, activity='added movie',
                                   timestamp=datetime.datetime.today())
        models.db.session.add(activity)
        models.db.session.commit()

    # Editing an existing movie
    @auth_required('token')
    @roles_required('Admin')
    def put(self, movie_id):
        movie = models.Movie.query.get(movie_id)
        name = request.form.get('name')
        date = request.form.get('date')
        subtitles = request.form.get('subtitles')
        price = request.form.get('price')
        genre = request.form.get('genre')
        rating = request.form.get('rating')
        runtime = request.form.get('runtime')
        language = request.form.get('language')
        existing_theatres = list(set([obj.theatre_id for obj in models.MovieSchedule.query.filter_by(movie_id=movie_id)]))
        theatres = request.form.get('theatres').split(',')
        for theatre_id in existing_theatres:
            schedules = models.MovieSchedule.query.filter_by(theatre_id=theatre_id).all()
            for schedule in schedules:
                models.db.session.delete(schedule)
        if theatres:
            for theatre_id in theatres:
                theatre = models.Theatre.query.get(theatre_id)
                times = np.linspace(10, 22, theatre.max_shows)
                times = [round(item, 2) for item in times]

                def numToTime(n):
                    h = int(n // 1)
                    m = n % 1
                    mins = int(m * 60)
                    if mins == 0:
                        mins = '00'
                    return str(h) + ":" + str(mins)

                times = list(map(numToTime, times))
                for time in times:
                    movie_schedule = models.MovieSchedule(theatre_id=theatre_id, movie_id=movie.id, time=time)
                    models.db.session.add(movie_schedule)
        if "image" in request.files:
            image = request.files['image']
            os.remove(os.path.join(imgSaveDirectory, str(name) + ".png"))
            image.save(os.path.join(imgSaveDirectory, str(name) + ".png"))
        movie.name = name
        movie.date = date
        movie.subtitles = subtitles
        movie.price = price
        movie.genre = genre
        movie.rating = rating
        movie.runtime = runtime
        movie.language = language
        models.db.session.commit()
        return "", "200 Movie Successfully Edited"

    # Deleting an existing movie
    @auth_required('token')
    @roles_required('Admin')
    def delete(self, movie_id):
        movie = models.Movie.query.get(movie_id)
        os.remove(os.path.join(imgSaveDirectory, str(movie.name) + ".png"))
        models.db.session.delete(movie)
        schedules = models.MovieSchedule.query.filter_by(movie_id=movie_id).all()
        if schedules:
            for schedule in schedules:
                models.db.session.delete(schedule)
        tickets = models.Ticket.query.filter_by(movie_id=movie_id).all()
        if tickets:
            for ticket in tickets:
                models.db.session.delete(ticket)
        models.db.session.commit()
        return "", "200 Theatre Successfully Removed"


# For Movies
from . import cache
class MoviesApi(Resource):

    # Get all movies by theatre
    @auth_required('token')
    def get(self, theatre_id):
        schedules = models.MovieSchedule.query.filter_by(theatre_id=theatre_id)
        return models.movie_schedules_schema.dump(schedules)

    # Get all movies by user
    @auth_required('token')
    def post(self):
        movies = models.Movie.query.filter_by(user_id=current_user.id)
        return models.movies_schema.dump(movies)

    # Get all theatres in app
    @auth_required('token')
    def put(self):
        theatres = models.Movie.query.all()
        return models.movies_schema.dump(theatres)

    # Invalid Requests
    def delete(self):
        return "", "404 Invalid Request"


# For Ticket
class TicketApi(Resource):

    # Obtain the times of each theatre
    @auth_required('token')
    def get(self, theatre_id, movie_id):
        schedules = models.MovieSchedule.query.filter_by(theatre_id=theatre_id, movie_id=movie_id)
        return models.movie_schedules_schema.dump(schedules)

    # To book a ticket
    @auth_required('token')
    def post(self):
        date = request.json['date']
        number_of_tickets = request.json['number_of_tickets']
        time = request.json['time']
        theatre_id = request.json['theatre_id']
        movie_id = request.json['movie_id']
        movie = models.Movie.query.get(movie_id)
        theatre = models.Theatre.query.get(movie_id)
        total_seats = models.Theatre.query.get(theatre_id).total_seats
        tickets = models.Ticket.query.filter_by(theatre_id=theatre_id, movie_id=movie_id, time=time, date=date).all()
        if not tickets:
            if int(number_of_tickets) <= total_seats:
                ticket = models.Ticket(date=date, number_of_tickets=number_of_tickets, time=time,theatre_id=theatre_id,
                                       movie_id=movie_id, user_id=current_user.id, timestamp=datetime.datetime.now())
                models.db.session.add(ticket)
                activity = models.Activity(user_id=current_user.id, activity="booked tickets",
                                           timestamp=datetime.datetime.today())
                models.db.session.add(activity)

                with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                                       'TicketConfirmationTemplate.html')) as file_:
                    template = Template(file_.read())
                    message = template.render(user=current_user, n=number_of_tickets, movie=movie.name,
                                              theatre=theatre.name, time=time)
                tasks.sendEmail(to_address=current_user.email, subject="Ticket Confirmation",
                                message=message, attachments=[])
                models.db.session.commit()
                return "", "200 Successfully Added Tickets"
            else:
                return "", "405 You Have Exceeded Theatre Capacity"
        else:
            print([ticket.number_of_tickets for ticket in tickets])
            filled_seats = sum([ticket.number_of_tickets for ticket in tickets])
            print(filled_seats)
            print(number_of_tickets)
            print(total_seats)
            if filled_seats + int(number_of_tickets) <= total_seats:
                ticket = models.Ticket(date=date, number_of_tickets=number_of_tickets, time=time,theatre_id=theatre_id,
                                       movie_id=movie_id, user_id=current_user.id, timestamp=datetime.datetime.now())
                models.db.session.add(ticket)
                activity = models.Activity(user_id=current_user.id, activity="booked tickets",
                                           timestamp=datetime.datetime.today())
                models.db.session.add(activity)

                with open(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'templates',
                                       'TicketConfirmationTemplate.html')) as file_:
                    template = Template(file_.read())
                    message = template.render(user=current_user.name, n=number_of_tickets, movie=movie.name,
                                              theatre=theatre.name, time=time)
                tasks.sendEmail(to_address=current_user.email, subject="Ticket Confirmation",
                                message=message, attachments=[])
                models.db.session.commit()

                return "", "200 Successfully Added Tickets"
            else:
                return "", "405 You Have Exceeded Theatre Capacity"

    # Invalid Requests
    def put(self):
        return "", "404 Invalid Request"

    def delete(self):
        return "", "404 Invalid Request"


# For Theatre Seats
class TheatreSeatsApi(Resource):

    # To obtain the number of seats available on a day, theatre
    @auth_required('token')
    def post(self, theatre_id):
        date = request.json['date']
        times = list(set(request.json['times']))
        movie_ids = request.json['movie_ids']
        theatre = models.Theatre.query.get(theatre_id)
        seats = {}
        total_seats = theatre.total_seats
        for movie_id in movie_ids:
            seats[movie_id] = {}
            for time in times:
                tickets = models.Ticket.query.filter_by(date=date, theatre_id=theatre_id, movie_id=movie_id,
                                                        time=time).all()
                if not tickets:
                    seats[movie_id][time] = total_seats
                else:
                    filled_seats = sum([ticket.number_of_tickets for ticket in tickets])
                    seats[movie_id][time] = total_seats - filled_seats
        return jsonify(seats)

    # Invalid Requests
    def get(self):
        return "", "404 Invalid Request"

    def put(self):
        return "", "404 Invalid Request"

    def delete(self):
        return "", "404 Invalid Request"


# For Movie Seats
class MovieSeatsApi(Resource):

    # To obtain the number of seats available on a day, movie
    @auth_required('token')
    def post(self, movie_id):
        date = request.json['date']
        theatre_ids = request.json['theatre_ids']
        seats = {}
        for theatre_id in theatre_ids:
            theatre = models.Theatre.query.get(theatre_id)
            total_seats = theatre.total_seats
            seats[theatre_id] = {}
            times = [obj.time for obj in models.MovieSchedule.query.filter_by(theatre_id=theatre_id,
                                                                          movie_id=movie_id).all()]
            for time in times:
                tickets = models.Ticket.query.filter_by(date=date, theatre_id=theatre_id, movie_id=movie_id,
                                                        time=time).all()
                if not tickets:
                    seats[theatre_id][time] = total_seats
                else:
                    filled_seats = sum([ticket.number_of_tickets for ticket in tickets])
                    seats[theatre_id][time] = total_seats - filled_seats
        return jsonify(seats)


# For Theatre Export
class ExportApi(Resource):

    @auth_required('token')
    @roles_required('Admin')
    def get(self, theatre_id):
        user_id = current_user.id
        r = tasks.generateCSV.delay(theatre_id=theatre_id, user_id=user_id)
        r.get()
        return "", "200 Successfully Exported Data"


#For logging out
class LogoutApi(Resource):

    @auth_required('token')
    def get(self):
        logout_user()
        return "", "200 Successfully Logged Out User"

    # Invalid Requests
    def post(self):
        return "", "404 Invalid Request"

    def put(self):
        return "", "404 Invalid Request"

    def delete(self):
        return "", "404 Invalid Request"
