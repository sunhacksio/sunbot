from flask_restful import Resource, abort
from flask import request, jsonify
from utils import mail
from models import Registration, Hacker
import secrets
import datetime
from peewee import DoesNotExist

class Verification(Resource):
    def post(self):
        email = request.args['email']
        # Gets or creates a new entry for a hacker
        hacker, created = Hacker.get_or_create(
            id = request.args['id'],
            username = request.args['username'],
            discriminator = request.args['discriminator']
        )
        # If the account exists and is verified return an error
        if not created and hacker.verified:
            abort(409, message = "Hacker already verified")

        # Get all registration entries under that email
        entries = Registration.select().where(Registration.email == email).order_by(Registration.submit_time)
        if entries.exists():
            if entries[0].hacker_discord != None and entries[0].hacker_discord != hacker:
                abort(409, message = "Registration verification started with another hacker")
            # Start hacker verification
            hacker.verification = secrets.token_hex(8)
            hacker.verification_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
            hacker.save()
            query = Registration.update(hacker_discord = hacker).where(Registration.email == email)

            # Email hacker!
            response = mail.send_verification_email(entries[0], hacker.verification)
            if response:
                query.execute()
                res = jsonify({
                    "status" : "Email sent!",
                    "code" : 0
                })
                res.status_code = 201
                return res
            else:
                abort(501, message = "Unable to send email")
        else:
            abort(404, message = "Unable to find registration")

class CheckIn(Resource):
    def post(self):
        id = request.args['id']
        code = request.args['code']
        try:
            hacker = Hacker.get_by_id(id)
            # If the account exists and is verified return an error
            if hacker.verified:
                abort(409, message = "Hacker already verified")
        except DoesNotExist:
            abort(409, message = "Verification not started")

        if code == hacker.verification and datetime.datetime.now() < hacker.verification_expiration:
            hacker.verified = True
            hacker.save()
            res = jsonify({
                "status" : "Hacker verified",
                "code" : 0
            })
            res.status_code = 201
            return res
        abort(403, message = "Invalid or expired code")

class CheckHacker(Resource):
    def get(self):
        id = request.args['id']
        try:
            hacker = Hacker.get_by_id(id)
            if hacker.verified:
                res = jsonify({
                    "verified" : "True"
                })
                res.status_code = 200
                return res
            raise DoesNotExit()
        except DoesNotExist:
            res = jsonify({
                "verified" : "False"
            })
            res.status_code = 200
            return res
