from playhouse.flask_utils import FlaskDB

db = FlaskDB()

from .hacker import Hacker
from .registration import Registration
