# Imports
import dotenv
import json
import requests
import sys
import os

def main():
    # Get the path of the script
    # From: https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
    DIR = os.path.dirname(os.path.realpath(__file__))

    # Load the ".env" fle
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    API_KEY = os.environ.get('API_KEY')
    if API_KEY == '' or API_KEY is None:
        print('Error: You must specify your Challonge API key in the ".env" file.')
        sys.exit(1)

    # Check for a command line argument that specifies the tournament ID
    if len(sys.argv) == 2:
        get_tournament(sys.argv[1])
        sys.exit(0)

    while True:
        print('Type "q" to exit.')
        tourney_id = input('Enter the Challonge tournament ID: ')
        if tourney_id == 'q':
            break

        get_tournament(tourney_id)


def get_tournament(tourney_id):
    # Get the data for this tournament through the Challonge API
    url = 'https://api.challonge.com/v1/tournaments/' + tourney_id + '.json'
    params = {'api_key': API_KEY, 'include_participants': 1, 'include_matches': 1}
    api_response = requests.get(url, params=params)
    if api_response.status_code != 200:
        print('Error: The Challonge API returned an HTTP response code of "' + str(api_response.status_code) + '".')
        sys.exit(1)
    tourney_json = api_response.json()
    tourney_data = tourney_json['tournament']

    # Parse it and create a new JSON object with just the data that we need
    date = tourney_data['started_at'].split('T', 1)[0]  # YYYY-MM-DD
    parsed_json = parse_json(tourney_data, tourney_id, date)

    # Write it to a file
    json_file = ''.join(e for e in tourney_data['name'] if e not in '/\\?*"<>|:') + '.json'
    output_path = os.path.join(DIR, 'tournaments', json_file)
    with open(output_path, 'w', encoding='utf-8', newline='\n') as data_file:
        json.dump(parsed_json, data_file, indent=2)


def parse_json(tournament, t_id, date):
    parsed_json = {'name': tournament['name'],
                   'challonge_id': t_id,
                   'challonge': tournament['full_challonge_url'],
                   'date': date,
                   'notability': 'minor',
                   'organizer': [],
                   'ruleset': '',
                   'description': '',
                   'videos': [],
                   'matchups': [],
                   'winner': 'n/a'
                   }

    matches = tournament['matches']
    tournament_winner = ''
    for match in matches:
        match_data = match['match']

        # If there is no winner in the match data, then we want the score to be a draw
        if match_data['winner_id'] is None:
            # Validate that there are player IDs
            if ((match_data['player1_id'] == '' or match_data['player1_id'] is None) and
                (match_data['player2_id'] == '' or match_data['player2_id'] is None)):

               print('Error: Failed to find the player IDs for the following match: ' + match_data)
               sys.exit(1)

            # Since it was a tie, put a score of "0-0"
            # This match should be investigated later and either deleted entirely or have manual score set
            parsed_json['matchups'].append({'winner': match_data['player1_id'],
                                            'loser': match_data['player2_id'],
                                            'score': '0-0'})

        # If there is a winner, we get the score
        else:
            scores = match_data['scores_csv'].split('-')
            scores.sort(reverse=True)
            try:
                match_score = scores[0] + '-' + scores[1]
            except IndexError:
                match_score = '0-0'  # Account for when a match is forfeited
            parsed_json['matchups'].append({'winner': match_data['winner_id'],
                                            'loser': match_data['loser_id'],
                                            'score': match_score})

            # The tournament winner is not listed in the JSON that we get back from the Challonge API
            # Thus, assume that the winner of the last match is the tournament winner
            tournament_winner = match_data['winner_id']


    # Looping through participants to get their ID
    participants = tournament['participants']
    for participant in participants:
        participant_id = participant['participant']['id']
        participant_group_id = participant['participant']['group_player_ids']
        participant_name = participant['participant']['name']
        if participant_name == '' or participant_name is None:  # Sometimes the name is empty because it is tied to the Challonge account
            participant_name = participant['participant']['challonge_username']
        if participant_name == '' or participant_name is None:
            print('Error: Was not able to get the name for participant:' + participant)
            sys.exit(1)

        # Replace the ID with the player name in the parsed JSON
        for match in parsed_json['matchups']:
            winner = match['winner']
            if winner == participant_id or winner in participant_group_id:
                match['winner'] = participant_name

            loser = match['loser']
            if loser == participant_id or loser in participant_group_id:
                match['loser'] = participant_name

        # Replace the tournament winner ID
        if tournament_winner == participant_id:
            tournament_winner = participant_name

    parsed_json['winner'] = tournament_winner
    print('JSON parsed successfully.')
    return parsed_json


if __name__ == '__main__':
    main()
