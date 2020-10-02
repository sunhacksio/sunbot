from peewee import *
from models import db, Hacker
from utils import crowd_bt
import datetime

class Project(db.Model):
    table = IntegerField(unique = True, primary_key = True)
    name = TextField()
    url = TextField()
    active = BooleanField(default = True)

    mu = FloatField(default = crowd_bt.MU_PRIOR)
    sigma_sq = FloatField(default = crowd_bt.SIGMA_SQ_PRIOR)

    class Meta:
        table_name = "projects"


class Vote(db.Model):
    hacker = ForeignKeyField(Hacker, backref="voted")
    winner = ForeignKeyField(Project, backref="wins")
    loser = ForeignKeyField(Project, backref="losses")
    time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "votes"


class View(db.Model):
    hacker = ForeignKeyField(Hacker, backref="viewed")
    project = ForeignKeyField(Project, backref="views")

    class Meta:
        table_name = "views"


class Flag(db.Model):
    hacker = ForeignKeyField(Hacker, backref="flagged")
    project = ForeignKeyField(Project, backref="reports")
    description = TextField()

    class Meta:
        table_name = "flags"
