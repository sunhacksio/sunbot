import os

from flask import Flask, jsonify, request, render_template
from playhouse.flask_utils import FlaskDB
from peewee import *
from models import db, Registration, Hacker
from utils import mail
import datetime
import secrets

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True

app.config['DATABASE'] = {
    'name': 'sunhacks.db',
    'engine': 'peewee.SqliteDatabase',
}
db.init_app(app)

@app.route('/api/discord/verify', methods=['POST'])
def start_verification():
    """
    Verifies users with an id and verification code
    Code  | HTTP  | Description
    -----------------------
    0       201     Code sent
    1       409     Hacker already verified
    2       409     Registration started with another hacker
    3       501     Error sending email
    4       404     Registration not found
    """
    email = request.args['email']
    # Gets or creates a new entry for a hacker
    hacker, created = Hacker.get_or_create(
        id = request.args['id'],
        username = request.args['username'],
        discriminator = request.args['discriminator']
    )
    # If the account exists and is verified return an error
    if not created and hacker.verified:
        res = jsonify({
            "error" : "Hacker already verified",
            "code" : 1
        })
        res.status_code = 409
        return res

    # Get all registration entries under that email
    entries = Registration.select().where(Registration.email == email).order_by(Registration.submit_time)
    if entries.exists():
        if entries[0].hacker_discord != None and entries[0].hacker_discord != hacker:
            res = jsonify({
                "error" : "Registration verification started with another hacker",
                "code" : 2
            })
            res.status_code = 409
            return res
        # Start hacker verification
        hacker.verification = secrets.token_hex(8)
        hacker.verification_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        hacker.save()
        query = Registration.update(hacker_discord = hacker).where(Registration.email == email)

        # Email hacker!
        response = mail.send_verification_email(entry[0], hacker.verification)
        if response:
            res = jsonify({
                "status" : "Email sent!"
                "code" : 0
            })
            res.status_code = 201
            return res
        else:
            res = jsonify({
                "error" : "Unable to send email",
                "code" : 3
            })
            res.status_code = 501
            return res
    else:
        res = jsonify({
            "error" : "Unable to find registration",
            "code" : 4
        })
        res.status_code = 404
        return res

@app.route('/api/discord/confirm', methods=['POST'])
def verify():
    """
    Verifies users with an id and verification code
    Code  | HTTP  | Description
    -----------------------
    0       201     Verified
    1       409     Hacker already verified
    2       409     Verification not started
    3       403     Invalid or expired code
    """
    id = request.args['id']
    code = request.args['code']
    try:
        hacker = Hacker.get_by_id(id)
        # If the account exists and is verified return an error
        if hacker.verified:
            res = jsonify({
                "error" : "Hacker already verified",
                "code" : 1
            })
            res.status_code = 409
            return res
    except DoesNotExist:
        res = jsonify({
            "error" : "Verification not started",
            "code" : 2
        })
        res.status_code = 409
        return res

    if code == hacker.verification and datetime.datetime.now() < hacker.verification_expiration:
        hacker.verified = True
        hacker.save()
        res = jsonify({
            "status" : "Hacker verified"
            "code" : 0
        })
        res.status_code = 201
        return res
    res = jsoninfy({
        "error" : "Invalid or expired code",
        "code" : 3
    })
    res.status_code = 403
    return res

if __name__ == '__main__':
    app.run()
