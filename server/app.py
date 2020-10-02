import os
import datetime
import secrets
import dotenv
import json
import click

from flask import Flask, jsonify, request, render_template
from flask_restful import Api, abort
from flask.cli import AppGroup
from playhouse.flask_utils import FlaskDB
from peewee import *

from models import db, create_tables, Registration, Project
from utils import mail
from utils import typeform
from utils import sendy
from routes import *

config = dotenv.load_dotenv()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True

app.config['DATABASE'] = {
    'name': 'sunhacks.db',
    'engine': 'peewee.SqliteDatabase',
}
db.init_app(app)
db_cli = AppGroup('db')
app.cli.add_command(db_cli)

api = Api(app)

@app.before_request
def discord_check():
    if "discord" in request.url:
        if os.getenv("SUNBOT_SECRET", None) != request.headers["Sunbot-Secret"]:
            abort(401, message = "API only available to verified requests")

# Typeform webhook
api.add_resource(TypeformWebhook, "/typeform/webhook")

# Discord Registration
api.add_resource(Verification, "/discord/verify")
api.add_resource(CheckIn, "/discord/confirm")
api.add_resource(CheckHacker, "/discord/verified")
# Discord Voting
api.add_resource(StartVote, "/discord/startvote")
api.add_resource(GetProject, "/discord/nextproj")
api.add_resource(SubmitView, "/discord/viewproj")
api.add_resource(SubmitFlag, "/discord/flagproj")
api.add_resource(SubmitVote, "/discord/voteproj")


@db_cli.command('tf-import')
@click.argument('filename')
def import_typeform(filename):
    import csv

    fields = ["id"] + typeform.FIELDS + ["start_time","submit_time","network_id"]
    vals = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fields)
        for row in reader:
            row["first_hack"] = row["first_hack"] == "1"
            row["sponsor"] = row["sponsor"] == "1"
            row["swag"] = row["swag"] == "1"
            row["code_of_conduct"] = row["code_of_conduct"] == "1"
            row["terms_and_conditions"] = row["terms_and_conditions"] == "1"
            vals.append(row)

        create_tables()
        with db.database.atomic():
            (Registration.insert_many(vals[1:])
             .on_conflict("update", conflict_target = [Registration.id], preserve = Registration.hacker_discord).execute())
        click.echo("Uploaded {0} entries to the Registration table".format(len(vals) - 1))

@db_cli.command('dp-import')
@click.argument('filename')
def import_devpost(filename):
    import csv

    fields = ["table", "name", "url"]
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile, fields)
        vals = [row for row in reader]

    create_tables()
    with db.database.atomic():
        (Project.insert_many(vals[1:])
         .on_conflict("update", conflict_target = [Project.table], preserve = [Project.active, Project.mu, Project.sigma_sq]).execute())
    click.echo("Uploaded {0} projects to the Projects table".format(len(vals) - 1))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
