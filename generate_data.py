from index import db, app, TeamModel
from models import get_team_model
from stats.event import create_team_list
from stats.opr_epa import calculate_world_epa_opr, calculate_event_epa_opr
from stats.team import Team


def calculate():
    # Calculate all statistics
    teams = calculate_event_epa_opr(create_team_list("CAABNISTM1", season=2024), season=2024, region_code="CAAB")

    # Loop through all teams and add/update teams
    for team in teams.values():
        team: Team
        print(team)

        model_obj = TeamModel(team)
        query: TeamModel = TeamModel.query.filter_by(team_number=team.team_number).first()
        if not query:
            print("Found new team, adding to database.")
            db.session.add(model_obj)
        else:
            print("Updating existing team.")
            query.update(team)

    db.session.commit()

with app.app_context():
    calculate()