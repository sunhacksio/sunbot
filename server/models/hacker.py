from peewee import *
from models import db

class Hacker(db.Model):
    id = CharField(unique = True, verbose_name = "Discord User ID", primary_key = True)
    username = TextField(verbose_name = "Discord Username")
    discriminator = TextField(verbose_name = "Discord Tag")
    verification = CharField(null = True)
    verification_expiration = DateTimeField(null = True)
    verified = BooleanField(default = False)

    class Meta:
        table_name = "hackers"
