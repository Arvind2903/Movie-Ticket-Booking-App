from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_login import LoginManager
from flask_security import Security
from flask_caching import Cache

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"
CORS(app)
app.app_context().push()

from .config import LocalDevelopmentConfig
app.config.from_object(LocalDevelopmentConfig)

cache = Cache(app)
app.app_context().push()

from .api import *
api = Api(app)

from .models import *
security = Security(app, user_datastore)
ma.init_app(app)

from .database import db
db.init_app(app)
app.app_context().push()
db.create_all()
api.add_resource(SignUpApi, "/api/signup")
api.add_resource(UserApi, "/api/user")
api.add_resource(TheatreApi, "/api/theatre", "/api/theatre/<int:theatre_id>")
api.add_resource(LogoutApi, "/api/logout")
api.add_resource(MovieApi, "/api/movie", "/api/movie/<int:movie_id>")
api.add_resource(TheatresApi, "/api/theatres", "/api/theatres/<int:movie_id>")
api.add_resource(MoviesApi, "/api/movies", "/api/movies/<int:theatre_id>")
api.add_resource(TicketApi, "/api/ticket", "/api/ticket/<int:theatre_id>/<int:movie_id>", "/api/ticket/<int:theatre_id>")
api.add_resource(MovieSeatsApi, "/api/movie-seats", "/api/movie-seats/<int:movie_id>")
api.add_resource(TheatreSeatsApi, "/api/theatre-seats", "/api/theatre-seats/<int:theatre_id>")
api.add_resource(ExportApi, '/api/export/<int:theatre_id>')

from .workers import celery, ContextTask
celery.conf.update(
    broker_url = app.config["CELERY_BROKER_URL"],
    result_backend = app.config["CELERY_RESULT_BACKEND"]
)
celery.conf.enable_utc = False
celery.conf.timezone = "Asia/Calcutta"
celery.Task = ContextTask
app.app_context().push()

from . import tasks
from . import models

