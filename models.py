from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, JSON
from sqlalchemy.types import ARRAY, String, Integer, Float
from flask_restful import fields

from stats.team import Team

team_model_fields = {
    'team_number': fields.Integer,
    'team_name': fields.String,
    'country': fields.String,
    'state_province': fields.String,
    'city': fields.String,
    'home_region': fields.String,
    'games_played': fields.Integer,

    'epa_total': fields.Float,
    'auto_epa_total': fields.Float,
    'tele_epa_total': fields.Float,
    'historical_epa': fields.List(fields.Float),
    'historical_auto_epa': fields.List(fields.Float),
    'historical_tele_epa': fields.List(fields.Float),

    'opr': fields.Float,
    'opr_auto': fields.Float,
    'opr_tele': fields.Float,
    'opr_end': fields.Float,
    'historical_opr': fields.List(fields.Float),
    'historical_auto_opr': fields.List(fields.Float),
    'historical_tele_opr': fields.List(fields.Float),
    'historical_end_opr': fields.List(fields.Float)
}

def get_team_model(db: SQLAlchemy):
    class TeamModel(db.Model):
        """
        Model used to define the shape of teams in the database with sqlalchemy
        """

        # General Info
        team_number = Column(Integer, primary_key=True)
        team_name = Column(String(80), nullable=False)
        country = Column(String)
        state_province = Column(String)
        city = Column(String)
        home_region = Column(String)
        games_played = Column(Integer)

        # EPA
        epa_total = Column(Float)
        auto_epa_total = Column(Float)
        tele_epa_total = Column(Float)
        historical_epa = Column(JSON)
        historical_auto_epa = Column(JSON)
        historical_tele_epa = Column(JSON)

        # OPR
        opr = Column(Float)
        opr_auto = Column(Float)
        opr_tele = Column(Float)
        opr_end = Column(Float)
        historical_opr = Column(JSON)
        historical_auto_opr = Column(JSON)
        historical_tele_opr = Column(JSON)
        historical_end_opr = Column(JSON)

        def __init__(self, team: Team):
            self.update(team)

        def update(self, team: Team):
            self.team_number = team.team_number
            self.team_name = team.name
            self.country = team.country
            self.state_province = team.state_prov
            self.city = team.city
            self.home_region = team.home_region
            self.games_played = team.games_played

            self.epa_total = team.epa_total
            self.auto_epa_total = team.epa_auto_total
            self.tele_epa_total = team.epa_tele_total
            self.historical_epa = jsonify(team.historical_epa).json
            self.historical_auto_epa = jsonify(team.historical_auto_epa).json
            self.historical_tele_epa = jsonify(team.historical_tele_epa).json

            self.opr = team.opr
            self.opr_auto = team.opr_auto
            self.opr_tele = team.opr_tele
            self.opr_end = team.opr_end
            self.historical_opr = jsonify(team.opr_total_vals).json
            self.historical_auto_opr = jsonify(team.opr_auto_vals).json
            self.historical_tele_opr = jsonify(team.opr_tele_vals).json
            self.historical_end_opr = jsonify(team.opr_end_vals).json

        def __repr__(self):
            return f"Team(number={self.team_number},name={self.team_name})"

    return TeamModel