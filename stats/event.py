from threading import Event
from typing import List

import requests
from datetime import datetime
from stats.data import get_auth
from stats.team import Team


def create_team_list(event_code, season):
  """
  Retrieves the team list from a given event code
  :param season: Four digit year representing the season
  :param event_code: FIRST Event Code
  :return:
    Dictionary of team objects
  """

  team_response = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/teams?eventCode="+event_code, auth=get_auth())
  teams_at_comp = team_response.json()['teams']

  ranking_response = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/rankings/"+event_code, auth=get_auth())
  rankings = ranking_response.json()['rankings']

  # Print out the team numbers for each of the teams at the competition


  teams = {}

  for team in teams_at_comp:
    team_number = team['teamNumber']
    state_prov = team['stateProv']
    country = team['country']
    city = team['city']
    home_region = team['homeRegion']
    name = team['nameShort']
    teams[team_number] = Team(team_number, name, country, state_prov, city, home_region)

    # Find team rank
    event_ranking = next((rank for rank in rankings if rank["teamNumber"] == team_number), None)
    if event_ranking is not None:
      teams[team_number].update_event_rank(event_code, event_ranking['rank'])

  return teams

def validate_event(event_code, season) -> Event | None:
  """
  Validate whether a given event code exists in the current season and return an event object
  :param season: Four digit year representing the season
  :param event_code: An event code to test
  :return: An event object if the code is valid, none otherwise
  """
  if event_code == "": # Return false if empty
    return None

  event_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/events?eventCode="+event_code,
                                auth=get_auth())

  if event_response.status_code == 404: # Return false if 404 not found
    return None

  event = event_response.json()['events'][0]
  return Event(event_code, event, season)

def get_all_events_by_teams(teams: List[str], season):
  """
    Get all events played in from a list of teams
    :param season: Four digit year representing the season
    :param teams: A list of team numbers as strings
    :return: A list of objects containing the start date and event code of all events sorted from earliest to latest
    """
  valid_event = [1, 2, 3, 4, 6, 7, 17]

  event_codes = [] # Set of (event_date, event_code) objects
  event_dates = []

  print(f"Retrieving events from {len(teams)} teams")
  for team_number in teams:
    event_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/events?teamNumber="+str(team_number),
                                  auth=get_auth())
    events = event_response.json().get('events', [])
    print(f"Finding events from {team_number} ")
    if all(event in event_codes for event in events):
      continue

    for event in events:
      if int(event['type']) in valid_event:
        event_code = event['code']
        event_date = event['dateStart']

        if event_code not in event_codes:
          event_codes.append(event_code)
          event_dates.append(event_date)

  # Combine, sort by date
  combined = list(zip(event_dates, event_codes))
  combined.sort(key=lambda x: datetime.fromisoformat(x[0]))

  return combined


def get_all_events(region_code:str=""):
  """
  Get all events
  :param region_code: OPTIONAL region code to filter by
  :return: A list of objects containing the start date and event code of all events sorted from earliest to latest
  """
  # List of valid event types
  # 1 = League Meet, 2 = Qualifier, 3 = League Tournament,
  # 4 = Championship, 6 = FIRST Championship, 7 = Super Qualifier
  # 10 = Off Season, 12 = Kickoff, 13 = Workshop
  # 14 = Demo/Exhibition, 15 = Volunteer Signup, 16 = Practice Day
  # 17 = Premier
  valid_event = [1, 2, 3, 4, 6, 7, 17]

  event_response = requests.get("http://ftc-api.firstinspires.org/v2.0/2024/events", auth=get_auth())
  events = event_response.json().get('events', [])

  event_codes = []
  event_date = []

  for event in events:
    # Check if there is a region code specified and filters events by the region code
    if region_code and event['regionCode'] != region_code:
      continue

    if int(event['type']) in valid_event: # filter out events like kickoff, workshop, etc.
      event_codes.append(event['code'])
      event_date.append(event['dateStart'])

  # Combine, sort by date
  combined = list(zip(event_date, event_codes))
  combined.sort(key=lambda x: datetime.fromisoformat(x[0]))

  return combined

class Event:

  def __init__(self, event_code, event, season):
    """
    :param event_code: FTC Event Code
    :param event: JSON response from FTC API for that event
    :param season: Valid season
    """
    self.event_code = event_code
    self.name = event['name']

    # Location Info
    self.country = event['country']
    self.state_province = event['stateprov']
    self.city = event['city']

    self.team_list = create_team_list(event_code, season)