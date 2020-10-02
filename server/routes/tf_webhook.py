from flask_restful import Resource, abort
from flask import request, jsonify
from utils import typeform, sendy
from models import Registration
import traceback


class TypeformWebhook(Resource):
    def post(self):
        if typeform.authorize(request.headers["typeform-signature"], request.data):
            event = request.json
            vals = typeform.parse_responses(event)
            try:
                reg, _  = Registration.create(**vals)
            except:
                traceback.print_exc()
                abort(409, message = "Registration not recorded")
            r = sendy.add_to_mailing_list(reg)
            if r.status_code == 200:
                res = jsonify({
                    "status" : "Registration recorded"
                })
                res.status_code = 201
                return res
            else:
                abort(501, message = "Registered but unable to send email")
        abort(401, message = "Unauthorized")
