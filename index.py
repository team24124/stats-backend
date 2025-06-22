import json

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, marshal_with, abort, fields
from sqlalchemy import Column
from sqlalchemy.types import ARRAY, String, Integer, Float, JSON

from generate_data import calculate_stats
from stats.team import Team as TeamObj

from models import team_model_fields, get_team_model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

api = Api(app)
db: SQLAlchemy = SQLAlchemy(app)


team_args = reqparse.RequestParser()
team_args.add_argument('team_number',  type=int, required=True, help="Team number cannot be blank")
team_args.add_argument('team_name',  type=str, required=True, help="Team name cannot be blank")

TeamModel = get_team_model(db)


class Teams(Resource):
    @marshal_with(team_model_fields)
    def get(self):
        teams = TeamModel.query.all()
        return teams

class Team(Resource):
    @marshal_with(team_model_fields)
    def get(self, team_number):
        team = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        return team

    # Update field with given args
    @marshal_with(team_model_fields)
    def patch(self, team_number):
        args = team_args.parse_args()
        team: TeamModel = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        team.team_number = args["team_number"]
        team.team_name = args["team_name"]
        db.session.commit()
        return team

    # # Delete field
    # @marshal_with(team_fields)
    # def delete(self, team_number):
    #     team: TeamModel = TeamModel.query.filter_by(team_number=team_number).first()
    #     if not team:
    #         abort(404, message="The requested team was not found. Please try again.")
    #     db.session.delete(team)
    #     db.session.commit()
    #     return TeamModel.query.all(), 200 # 204 = Successful Deletion or 200 = Successful

api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int:team_number>')

@app.route('/')
def home():
    return '<h1>Hello World</h1>'

@app.route('/api/cron/update')
def update():
    with app.app_context():
        calculate_stats(db, TeamModel)
    return '<p>Data successfully updated.</p>'

if __name__ == '__main__':
    app.run(debug=True)
