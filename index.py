from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class TeamModel(db.Model):
    team_number = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"Team(number={self.team_number},name={self.team_name})"

team_args = reqparse.RequestParser()
team_args.add_argument('team_number',  type=int, required=True, help="Team number cannot be blank")
team_args.add_argument('team_name',  type=str, required=True, help="Team name cannot be blank")

team_fields = {
    'team_number':fields.Integer,
    'team_name':fields.String
}

class Teams(Resource):
    @marshal_with(team_fields)
    def get(self):
        teams = TeamModel.query.all()
        return teams

    @marshal_with(team_fields)
    def post(self):
        args = team_args.parse_args()
        team = TeamModel(team_number=args['team_number'], team_name=args['team_name'])
        db.session.add(team)
        db.session.commit()
        teams = TeamModel.query.all()
        return teams, 201 # Successful creation

class Team(Resource):
    @marshal_with(team_fields)
    def get(self, team_number):
        team = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        return team

    # Update field with given args
    @marshal_with(team_fields)
    def patch(self, team_number):
        args = team_args.parse_args()
        team: TeamModel = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        team.team_number = args["team_number"]
        team.team_name = args["team_name"]
        db.session.commit()
        return team

    # Delete field
    @marshal_with(team_fields)
    def delete(self, team_number):
        team: TeamModel = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        db.session.delete(team)
        db.session.commit()
        return TeamModel.query.all(), 200 # 204 = Successful Deletion or 200 = Successful

api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int:team_number>')

@app.route('/')
def home():
    return '<h1>Hello Flask</h1>'


if __name__ == '__main__':
    app.run(debug=True)
