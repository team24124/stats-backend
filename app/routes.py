from flask import render_template
from app import app, db, api
from app.models import TeamModel, team_model_fields
from flask_restful import Resource, marshal_with, abort

from stats.opr_epa import calculate_world_epa_opr


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

api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int: team_number>')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cron/update')
def update():
    with app.app_context():
        # Calculate all statistics
        teams = calculate_world_epa_opr(season=2024)  # calculate_event_epa_opr(create_team_list("USCALAMOS", 2024), season=2024)

        # Loop through all teams and add/update teams
        with db.session.no_autoflush:
            for team in teams.values():
                model_obj = TeamModel(team)
                query: TeamModel = TeamModel.query.filter_by(team_number=team.team_number).first()

                if not query:
                    print("Found new team, adding to database.")
                    db.session.add(model_obj)
                else:
                    print("Updating existing team.")
                    query.update(team)

        db.session.commit()
    return '<p>Data successfully updated.</p>'