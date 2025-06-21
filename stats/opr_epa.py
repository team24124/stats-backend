import requests

from stats.data import get_auth
from stats.event import create_team_list, get_all_events, get_all_events_by_teams
from stats.team import Team
from datetime import datetime
import numpy as np


def create_game_matrix(event_code, team_list, season):
    """
    Calculates the game matrix, indicating which teams played in which matches
    :param season: Four digit year representing the season
    :param event_code: Valid FIRST Event Code
    :param team_list: Valid list of teams from the event
    :return: The game matrix
    """

    response = requests.get(
        f"http://ftc-api.firstinspires.org/v2.0/{season}/matches/" + event_code + "?tournamentLevel=qual", auth=get_auth())
    matches = response.json()['matches']  # only grab from qualifiers to equally compare all teams

    game_matrix = []

    # Add 1 to row at index where team number is in list
    for match in matches:
        red_alliances = [0] * len(team_list)
        blue_allainces = [0] * len(team_list)

        # for each match find if each team is on a red or blue alliance team
        for team in match['teams']:
            alliance = team['station']
            if alliance == 'Red1' or alliance == 'Red2':
                red_alliances[team_list.index(team['teamNumber'])] = 1
            else:
                blue_allainces[team_list.index(team['teamNumber'])] = 1

        game_matrix.append(red_alliances)
        game_matrix.append(blue_allainces)

    return game_matrix


def obtain_score_data(event_code, season):
    """
    Calculates a list of the scores, broken into components

    :param season: Valid four digits representing the year of the game
    :param event_code: A valid FIRST event code
    :return: A tuple of each score component: total score, auto score, teleop score and endgame score
    """

    # Pulling a request for the scores with different parameters
    response = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/" + event_code + "/qual",
                            auth=get_auth())  # only grab from qualifiers to equally compare all teams
    score_data = response.json()['matchScores']

    auto_score = []
    teleop_score = []
    endgame_score = []
    total_score = []

    for match_score in score_data:
        red_alliance = match_score['alliances'][1]
        blue_alliance = match_score['alliances'][0]

        # Add red alliance
        total_score.append(red_alliance['preFoulTotal'])
        auto_score.append(red_alliance['autoPoints'])
        teleop_sample_spec = red_alliance['teleopSamplePoints'] + red_alliance[
            'teleopSpecimenPoints']
        teleop_score.append(teleop_sample_spec)

        endgame_score.append(red_alliance['teleopPoints'] - teleop_sample_spec)

        # Then blue alliance
        total_score.append(blue_alliance['preFoulTotal'])
        auto_score.append(blue_alliance['autoPoints'])
        teleop_sample_spec = blue_alliance['teleopSamplePoints'] + blue_alliance[
            'teleopSpecimenPoints']
        teleop_score.append(teleop_sample_spec)

        endgame_score.append(blue_alliance['teleopPoints'] - teleop_sample_spec)

    return total_score, auto_score, teleop_score, endgame_score


def calculate_start_avg(events, season):
    """
    Calculates the start of the season average for use in EPA calculations
    :param season: Valid four digits representing the year of the game
    :param events: List of (event date, event code) objects to consider
    :return: Average total score, average auto score, average teleop score
    """
    first_events = []

    for event in events:
        iso_date = event[0]
        event_code = event[1]

        date = datetime.fromisoformat(iso_date)
        if date.month == 11 or date.month == 10:  # Find events in October (10) or November (11)
            print(f"Found early event (${event_code})")
            first_events.append(event_code)

    num_games = avg_total = avg_auto = avg_teleop = 0
    # Find the averages in the first number of events
    for event in first_events:
        print(f"Parsing event scores from early event")
        event_total_scores, event_auto_scores, event_tele_scores, event_end_scorse = obtain_score_data(event, season)
        num_games += len(event_total_scores)
        avg_total += sum(event_total_scores)
        avg_auto += sum(event_auto_scores)
        avg_teleop += sum(event_tele_scores)

    avg_total /= num_games
    avg_total /= 2

    avg_auto /= num_games
    avg_auto /= 2

    avg_teleop /= num_games
    avg_teleop /= 2

    print(f"Average Total: {avg_total}, Average Auto: {avg_auto}, Average TeleOP: {avg_teleop}")
    return avg_total, avg_auto, avg_teleop

def calculate_event_epa_opr(teams, season, region_code=""):
    """
    Calculate and update epa and opr for all teams at a specified event
    :param season: Four digit year representing the season
    :param teams: List of teams participating at the event
    :param region_code: Optional, region code used to determine starting averages for EPA
    :return: A list of all teams who have participated in an event with updated statistics
    """

    events = get_all_events_by_teams(teams, season) # Get all events that the teams have participated in


    all_teams = calculate_all_epa_opr(events, season, region_code) # Calculate relevant epa/opr for all teams in those events



    print("Filtering for teams in the event")
    event_teams = {str(team): all_teams[team] for team in teams} # Filter for teams at the specified event

    print("Calculations complete!")
    return event_teams

def calculate_world_epa_opr(season, region_code=""):
    all_teams: dict[str, Team]
    all_events = get_all_events()
    all_teams = calculate_all_epa_opr(all_events, season, region_code)

    print("Calculations complete!")
    return all_teams

def calculate_all_epa_opr(events, season, region_code=""):
    """
    Calculate and update epa and opr for all teams, able to be filtered by specifying a list of events
    :param season: Four digit representing the year of the game
    :param events: List of (event start date, event code) object
    :param region_code: (OPTIONAL) Region Code to use while determining starting average
    :return: A list of all teams who have participated in atleast one of the given events with updated statistics
    """

    all_teams: dict[str, Team] = {}

    # Calculate Averages
    early_events = get_all_events() if region_code == "" else get_all_events(region_code)

    if region_code: print("Calculating Starting Averages from Region:", region_code)
    else: print("Calculating Starting Average from World Teams")

    avg_total, avg_auto, avg_teleop = calculate_start_avg(early_events, season)

    event_codes = [event[1] for event in events] # get event codes from tuple

    for event in event_codes:
        team_list = create_team_list(event, season) # List of team numbers needed
        team_number_list =  []
        print(f"Processing {len(team_list.values())} teams from event: {event}")
        for team_number in team_list:
            team = team_list[team_number]
            team_number_list.append(team.team_number)
            team.update_epa(avg_total)
            team.update_auto_epa(avg_auto)
            team.update_tele_epa(avg_teleop)

            if team_number not in all_teams.keys():
                all_teams[team.team_number] = team

            if event in team.rankings:
                all_teams[team.team_number].update_event_rank(event, team.rankings[event])
        game_matrix = create_game_matrix(event, team_number_list, season)

        if len(game_matrix) > 0:  # skip events with no games
            # Get relevant scoring data from the event
            total_match_score, auto_match_score, tele_match_score, end_match_score = obtain_score_data(event, season)

            # Calculate OPR
            total_opr = np.linalg.lstsq(game_matrix, total_match_score)[0]
            auto_opr = np.linalg.lstsq(game_matrix, auto_match_score)[0]
            tele_opr = np.linalg.lstsq(game_matrix, tele_match_score)[0]
            end_opr = np.linalg.lstsq(game_matrix, end_match_score)[0]

            for i in range(len(team_number_list)):
                team_number = team_number_list[i] # Use team number from team list to get team
                team_obj = all_teams[team_number]
                team_obj.update_opr(total_opr[i], auto_opr[i], tele_opr[i], end_opr[i])

            for i in range(0, len(game_matrix), 2):
                red_index = np.where(np.array(game_matrix[i]) == 1)[0]
                team1 = all_teams[team_number_list[red_index[0]]]
                team2 = all_teams[team_number_list[red_index[1]]]

                blue_index = np.where(np.array(game_matrix[i+1]) == 1)[0]
                team3 = all_teams[team_number_list[blue_index[0]]]
                team4 = all_teams[team_number_list[blue_index[1]]]

                # Use i as the index the red alliances score, therefore i+1 will be the index of the blue alliances'
                update_epa(team1, team2, team3, team4, total_match_score[i], total_match_score[i+1])
                update_epa_auto(team1, team2, team3, team4, auto_match_score[i], auto_match_score[i+1])
                update_epa_tele(team1, team2, team3, team4, tele_match_score[i],  tele_match_score[i+1])

    return all_teams

def get_epa_parameters(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team):
    """
    Calculate the correct m and k EPA parameters given 4 teams
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :return: m and k values for EPA calculation
    """
    k = 0.33
    m = 0
    games_played = (team_red_1.games_played + team_red_2.games_played +
                    team_blue_1.games_played + team_blue_2.games_played) / 4
    if 6 < games_played <= 12:
        k = 0.33 - (games_played - 6) / 45
    elif 12 < games_played <= 36:
        k = 0.2
        # m = (games_played - 12)/24 # Commented out due to non-defensive nature of this season's game
    elif games_played > 36:
        k = 0.2
        # m = 1

    return m, k


# Team Specific Functions
def update_epa(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
               blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Nonpenalty total score for the red alliance
    :param blue_score: Nonpenalty total score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2)

    red_epa = team_red_1.epa_total + team_red_2.epa_total
    blue_epa = team_blue_1.epa_total + team_blue_2.epa_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_epa(team_red_1.epa_total + delta_epa_red)
    team_red_2.update_epa(team_red_2.epa_total + delta_epa_red)
    team_blue_1.update_epa(team_blue_1.epa_total + delta_epa_blue)
    team_blue_2.update_epa(team_blue_2.epa_total + delta_epa_blue)


def update_epa_auto(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
                    blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Total auto score for the red alliance
    :param blue_score: Total auto score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2)

    red_epa = team_red_1.epa_auto_total + team_red_2.epa_auto_total
    blue_epa = team_blue_1.epa_auto_total + team_blue_2.epa_auto_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_auto_epa(team_red_1.epa_auto_total + delta_epa_red)
    team_red_2.update_auto_epa(team_red_2.epa_auto_total + delta_epa_red)
    team_blue_1.update_auto_epa(team_blue_1.epa_auto_total + delta_epa_blue)
    team_blue_2.update_auto_epa(team_blue_2.epa_auto_total + delta_epa_blue)


def update_epa_tele(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
                    blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Total teleop score for the red alliance
    :param blue_score: Total teleop score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2  )

    red_epa = team_red_1.epa_tele_total + team_red_2.epa_tele_total
    blue_epa = team_blue_1.epa_tele_total + team_blue_2.epa_tele_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_tele_epa(team_red_1.epa_tele_total + delta_epa_red)
    team_red_2.update_tele_epa(team_red_2.epa_tele_total + delta_epa_red)
    team_blue_1.update_tele_epa(team_blue_1.epa_tele_total + delta_epa_blue)
    team_blue_2.update_tele_epa(team_blue_2.epa_tele_total + delta_epa_blue)