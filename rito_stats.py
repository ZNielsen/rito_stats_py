import json
import requests

API_KEY = ""
with open("api.key", "r") as f:
    API_KEY = f.read()

ENDPOINT = "https://na1.api.riotgames.com"

class Player:
    def __init__(self):
        summoner_name = ""
        summoner_id = 0
        lane = ""

class Game:
    def __init__(self):
        # Win or Other
        self.result = "None"
        # The members of teams. teams[team][Player]
        self.teams = dict()
        # The index of the team that cantinas the summoner of interest
        self.team_of_interest = 0

# Interested in:
# Our teams role names -> get summoner name for each role
# Result of the game (win/loss/none)
# KDA of each person?


def get_encrypted_account_id(summ_name):
    slug = "/lol/summoner/v4/summoners/by-name/" + summ_name + "?api_key=" + API_KEY
    request = ENDPOINT + slug
    print("Sending reqwest: " + request)
    req = requests.get(url = request)
    return req.json()["accountId"]

def get_matches(id, start_idx, end_idx):
    api_endpoint_base = "/lol/match/v4/matchlists/by-account"
    slug = api_endpoint_base + "/" + id + \
            "?endIndex=" + str(end_idx) +  \
            "&beginIndex=" + str(start_idx) + \
            "&api_key=" + API_KEY
    request = ENDPOINT + slug
    print("Sending reqwest: " + request)
    req = requests.get(url = request)
    return req.json()

def get_game_info(game_id):
    api_endpoint_base = "/lol/match/v4/matches/"
    slug = api_endpoint_base + str(game_id) + \
            "?api_key=" + API_KEY
    request = ENDPOINT + slug
    print("Sending reqwest: " + request)
    req = requests.get(url = request)
    return req.json()


def collect_data(summoner):
    data = list()

    enc_account_id = get_encrypted_account_id(summoner)
    print("encrypted account id: " + enc_account_id)

    more_matches = True
    # The api has a limit of 100 matches at a time. Grab 100 at a time until
    # there are no more
    start_idx = 0
    end_idx = 100
    while (more_matches):
        matches = get_matches(enc_account_id, start_idx, end_idx)
        print("matches: " + str(matches))

        # Set up the next indexes
        start_idx = end_idx+1;
        end_idx = start_idx + 100;
        print("New indexes: start: " + str(start_idx) + " end: " + str(end_idx))

        range_start = matches["startIndex"]
        range_end = matches["endIndex"]
        more_matches = range_end-range_start == 100
        print("range_start: " +  str(range_start) + \
              " range_end: " + str(range_end) + \
              " diff: " + str(range_end-range_start))
        print("more_matches: " + str(more_matches))

        games = matches["matches"];
        for a_game in games:
            game = Game()

            game_id = a_game["gameId"]
            game_info = get_game_info(game_id)

            stats = game_info["teams"]
            participant_identities = game_info["participantIdentities"]
            participants = game_info["participants"]
            assert(len(participant_identities) == len(participants))

            # Get all the participants for this game
            blue_team = []
            red_team = []
            for (participant_identity, participant) in zip(participant_identities, participants):
                participant_id_id = participant_identity["participantId"]
                player = participant_identity["player"]
                summoner_name = player["summonerName"]
                summoner_id = player["summonerId"]

                team_id: i64 = participant["teamId"]
                participant_id: i64 = participant["participantId"]
                timeline: Json = participant["timeline"]
                lane: String = timeline["lane"]

                assert(participant_id_id == participant_id)

                if summoner_name == summoner:
                    game.team_of_interest = team_id

                p = Player()
                p.lane = lane
                p.summoner_name = summoner_name
                p.summoner_id = summoner_id

                if team_id not in game.teams:
                    game.teams[team_id] = list()
                game.teams[team_id].append(p)

            data.append(game);
    return data

def analyze_data(data):
    print("Analyzed")


data = collect_data("Suq Mediq")
analyze_data(data)

