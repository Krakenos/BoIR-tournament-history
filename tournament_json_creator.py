import json
import requests
import os
import dotenv

# Get the path of the script
# From: https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
DIR = os.path.dirname(os.path.realpath(__file__))

# Load the ".env" fle
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
API_KEY = os.environ.get('API_KEY')


def main():
    while True:
        print('Type q to exit')
        tourney_id = input('enter the tournament id:')
        if tourney_id == 'q':
            break

        # Get the data for this tournament through the Challonge API
        url = 'https://api.challonge.com/v1/tournaments/' + tourney_id + '.json'
        params = {'api_key': API_KEY, 'include_participants': 1, 'include_matches': 1}
        tourney = requests.get(url, params=params).json()
        tourney_data = tourney['tournament']
        date = tourney_data['started_at'].split('T', 1)[0]  # YYYY-MM-DD
        json_file += ''.join(e for e in tourney_data['name'] if e not in '/\\?*"<>|:') + '.json'
        output_path = path.join(DIR, 'tournaments', json_file)
        parsed_json = json_parser(tourney_data, tourney_id, date)
        with open(output_path, 'w', encoding='utf-8', newline='\n') as data_file:
            json.dump(parsed_json, data_file, indent=2)


def json_parser(tournament, t_id, date):
    matches = tournament['matches']
    participants = tournament['participants']
    parsed_json = {'name': tournament['name'],
                   'challonge_id': t_id,
                   'challonge': tournament['full_challonge_url'],
                   'date': date,
                   'notability': 'minor',
                   'organizer': [],
                   'ruleset': '',
                   'description': '',
                   'videos': [],
                   'matchups': []
                   }
    for match in matches:
        match_data = match['match']

        # If there is no winner in the match data, then we want the score to be a draw
        if match_data['winner_id'] is None:
            parsed_json['matchups'].append({'winner': match_data['player1_id'],
                                            'loser': match_data['player2_id'],
                                            'score': 'draw'})

        # If there is a winner, we get the score
        else:
            scores = match_data['scores_csv'].split('-')
            scores.sort(reverse=True)
            try:
                match_score = scores[0] + '-' + scores[1]
            except IndexError:
                match_score = '3-0'   # scenario where match is forfeited
            parsed_json['matchups'].append({'winner': match_data['winner_id'],
                                            'loser': match_data['loser_id'],
                                            'score': match_score})

    # Looping through participants to get their ID
    for participant in participants:
        participant_id = participant['participant']['id']
        participant_group_id = participant['participant']['group_player_ids']
        participant_name = participant['participant']['name']
        if participant_name == '':  # Sometimes name is empty because it's tied to Challonge account
            participant_name = participant['participant']['challonge_username']

        # Replace the ID with the player name in the parsed JSON
        for match in parsed_json['matchups']:
            winner = match['winner']
            loser = match['loser']
            if winner == participant_id or winner in participant_group_id:
                match['winner'] = participant_name
            if loser == participant_id or loser in participant_group_id:
                match['loser'] = participant_name

    print('JSON parsed successfully.')
    return parsed_json


if __name__ == '__main__':
    main()
