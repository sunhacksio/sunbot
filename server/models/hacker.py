from peewee import *
from models import db
from utils import crowd_bt

class Hacker(db.Model):
    id = CharField(unique = True, verbose_name = "Discord User ID", primary_key = True)
    username = TextField(verbose_name = "Discord Username")
    discriminator = TextField(verbose_name = "Discord Tag")
    verification = CharField(null = True)
    verification_expiration = DateTimeField(null = True)
    verified = BooleanField(default = False)

    # Voting information
    own_proj = DeferredForeignKey('Project', null = True)
    next_proj = DeferredForeignKey('Project', null = True)
    prev_proj = DeferredForeignKey('Project', null = True)
    updated_vote = DateTimeField(null = True)

    alpha = FloatField(default = crowd_bt.ALPHA_PRIOR)
    beta = FloatField(default = crowd_bt.BETA_PRIOR)

    class Meta:
        table_name = "hackers"
