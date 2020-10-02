from playhouse.flask_utils import FlaskDB

db = FlaskDB()

from .hacker import Hacker
from .registration import Registration
from .voting import View, Flag, Project, Vote

def create_tables():
    db.database.create_tables([Hacker, Registration, View, Flag, Project, Vote])
