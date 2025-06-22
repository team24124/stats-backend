from flask_sqlalchemy import SQLAlchemy

from stats.event import create_team_list
from stats.opr_epa import calculate_world_epa_opr, calculate_event_epa_opr
from stats.team import Team


def calculate_stats(db: SQLAlchemy, TeamModel):
    # Calculate all statistics
    teams = calculate_world_epa_opr(season=2024)#calculate_event_epa_opr(create_team_list("USCALAMOS", 2024), season=2024)

    # Loop through all teams and add/update teams
    with db.session.no_autoflush:
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