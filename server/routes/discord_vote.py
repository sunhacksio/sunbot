import datetime

import traceback
from flask_restful import Resource, abort
from flask import request, jsonify
from random import random, shuffle
from utils import mail, crowd_bt
from models import Hacker, Project, Vote, View, Flag

MIN_VIEWS = 2
TIMEOUT = 5.0

class StartVote(Resource):
    def post(self):
        id = request.args['id']
        table = request.args.get('table', None)
        try:
            hacker = Hacker.get_by_id(id)
        except:
            abort(404, message = "Hacker not found")
        hacker.updated_vote = datetime.datetime.utcnow()
        if table != None:
            try:
                hacker.own_proj = Project.get_by_id(table)
                View.create(hacker = hacker, project = hacker.own_proj)
            except:
                abort(404, message = "Project not found")
        try:
            hacker.save()
        except:
            abort(501, message = "Unable to create hacker entry")
        status = {"status": "Setup hacker to start voting"}
        if table != None:
            status["title"] = Project.get_by_id(table).name
        res = jsonify(status)
        res.status_code = 201
        return res

class GetProject(Resource):
    def preferred_items(self, hacker):
        seen = {i.project.table for i in View.select().where(View.hacker == hacker)}
        # They haven't even seen the last one we gave them!
        if hacker.next_proj != None and hacker.next_proj.table not in seen:
            return [hacker.next_proj]
        if seen:
            items = Project.select().where(Project.active, ~Project.table.in_(seen))
        else:
            items = Project.select().where(Project.active)

        hackers = Hacker.select().where(Hacker.next_proj != None, Hacker.updated_vote != None)
        busy = {i.next_proj.table for i in hackers if ((datetime.datetime.utcnow() - i.updated_vote).total_seconds() < TIMEOUT * 60)}
        if busy:
            items = items.select().where(~Project.table.in_(busy))

        less_items = [i for i in items if len(i.views) < MIN_VIEWS]
        return less_items if less_items else [i for i in items]

    def choose_next(self,hacker):
        items = self.preferred_items(hacker)
        if len(items) == 1:
            return items[0]
        shuffle(items)
        if items:
            # RANDOM!
            if random() < crowd_bt.EPSILON or hacker.prev_proj == None:
                return items[0]
            else:
                return crowd_bt.argmax(lambda i: crowd_bt.expected_information_gain(
                    hacker.alpha,
                    hacker.beta,
                    hacker.prev_proj.mu,
                    hacker.prev_proj.sigma_sq,
                    i.mu,
                    i.sigma_sq), items)
        else:
            return None

    def get(self):
        id = request.args['id']
        try:
            hacker = Hacker.get_by_id(id)
        except:
            abort(404, message = "Hacker not found")
        item = self.choose_next(hacker)
        if item != None:
            try:
                if hacker.next_proj != None and hacker.next_proj != item:
                    hacker.prev_proj = hacker.next_proj
                hacker.next_proj = item
                hacker.save()
            except:
                abort(409, message = "Unable to save next project to hacker")
            res = jsonify({
                "table": item.table,
                "title": item.name,
                "url": item.url
            })
            res.status_code = 200
            return res
        else:
            res = jsonify({"table": None})
            res.status_code = 200
            return res

class SubmitView(Resource):
    def post(self):
        id = request.args['id']
        try:
            hacker = Hacker.get_by_id(id)
        except:
            abort(404, message = "Hacker not found")
        if hacker.next_proj.table == int(request.args['table']):
            try:
                View.create(hacker = hacker, project = hacker.next_proj)
                res = jsonify({"status" : "View recorded"})
                res.status_code = 201
                return res
            except:
                abort(409, message = "Unable to submit view")
        else:
            abort(409, message = "Submission and database mismatch")

class SubmitFlag(Resource):
    def post(self):
        id = request.args['id']
        try:
            hacker = Hacker.get_by_id(id)
        except:
            abort(404, message = "Hacker not found")
        if hacker.next_proj.table == int(request.args['table']):
            try:
                View.create(hacker = hacker, project = hacker.next_proj)
                Flag.create(hacker = hacker, project = hacker.next_proj, description = request.data)
                hacker.next_proj = None
                hacker.save()
                res = jsonify({"status" : "Flag recorded"})
                res.status_code = 201
                return res
            except:
                abort(409, message = "Unable to submit flag")
        else:
            abort(409, message = "Submission and database mismatch")

class SubmitVote(Resource):
    def perform_vote(self, voter, next_won):
        if next_won:
            winner = voter.next_proj
            loser = voter.prev_proj
        else:
            winner = voter.prev_proj
            loser = voter.next_proj
        u_alpha, u_beta, u_winner_mu, u_winner_sigma_sq, u_loser_mu, u_loser_sigma_sq = crowd_bt.update(
            voter.alpha,
            voter.beta,
            winner.mu,
            winner.sigma_sq,
            loser.mu,
            loser.sigma_sq
        )
        voter.alpha = u_alpha
        voter.beta = u_beta
        winner.mu = u_winner_mu
        winner.sigma_sq = u_winner_sigma_sq
        loser.mu = u_loser_mu
        loser.sigma_sq = u_loser_sigma_sq
        voter.save()
        winner.save()
        loser.save()

    def post(self):
        id = request.args['id']
        next_won = request.args['next_won'] == 'True'
        try:
            hacker = Hacker.get_by_id(id)
        except:
            abort(404, message = "Hacker not found")
        if hacker.prev_proj.table == int(request.args['prev_table']) and hacker.next_proj.table == int(request.args['next_table']):
            if hacker.prev_proj.active and hacker.next_proj.active:
                self.perform_vote(hacker, next_won)
                if next_won:
                    Vote.create(hacker = hacker, winner = hacker.next_proj, loser = hacker.prev_proj)
                else:
                    Vote.create(hacker = hacker, winner = hacker.prev_proj, loser = hacker.next_proj)
            hacker.prev_proj = None
            hacker.save()
            res = jsonify({"status" : "Vote recorded"})

            res.status_code = 201
            return res
        else:
            abort(409, message = "Submission and database mismatch")

# class FlagProject(Resource):
#     def post(self):
#         id = request.args['id']
#         table = request.args['table']
