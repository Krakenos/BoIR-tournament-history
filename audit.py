#!/usr/bin/env python

# Imports
import glob
import json
import re
import sys

# Constants
json_fields = [
    'name',
    'challonge_id',
    'challonge',
    'date',
    'notability',
    'organizer',
    'ruleset',
    'description',
    'videos',
    'matchups',
    'winner',
]
json_videos_fields = [
    'description',
    'url',
]
valid_rulesets = [
    # Most tournaments use one of the three main racing formats
    'seeded',
    'unseeded',
    'diversity',

    # A mixed tournament is where each individual set of a match is played on a different ruleset
    # The ruleset is specified in the "ruleset_per_round" field in each matchup
    # (for example, see the "BITE 2" tournament)
    'mixed',

    # Team tournaments have various rules but are not used in leaderboard calculation since each individual matchup cannot be isolated
    # (for example, see the "Four Course Racing" tournament)
    'team',

    # Some tournaments are team-based but have individual matchups that can be isolated per ruleset
    # The ruleset is specified in the "ruleset" field in each matchup
    # (for example, see the "Conjoined" tournament)
    'multiple',

    # This is a unique tournament that has custom rules and should not be counted towards the leaderboards
    'other',
]

# Global variables
racers = {}
racers2 = {}
racers3 = {}


def main():
    # This script is written for Pyhton 3
    if sys.version_info < (3, 0):
        print('Error: This script requires Python 3.')
        sys.exit(1)

    # Loop through every file in the tournaments folder
    for path in sorted(glob.glob('tournaments/*.json')):
        # Load the file
        with open(path, 'r', encoding='utf-8', newline='\n') as f:
            raw = f.read()

        # Load the JSON
        with open(path, 'r', encoding='utf-8', newline='\n') as f:
            tournament_json = json.load(f)

        # Check to see if the file is formatted properly
        formatted = json.dumps(tournament_json, indent=2) + '\n'
        # (we want the files to have a trailing newline so that they are POSIX compliant)
        if not raw == formatted:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(formatted)
            print(path + ' - Not formatted properly; automatically fixed.')

        # Check that all of the specified fields are present in each
        for field in json_fields:
            if not checkKey(tournament_json, field):
                print(path + ' - The "' + field + '" field does not exist!')
        team_event = tournament_json['ruleset'] == 'team'
        if team_event:
            if not checkKey(tournament_json, 'teams'):
                print(path + ' - The "teams" field does not exist!')

        # Check for extra fields
        for field in tournament_json:
            if field not in json_fields and field != 'teams':
                print(path + ' - ' + field + ' is unknown!')

        # Validate the ruleset
        if type(tournament_json['ruleset']) != str:
            print(path + ' - The "ruleset" field is not a string.')
        elif tournament_json['ruleset'] == '':
            print(path + ' - The "ruleset" field is empty.')
        elif tournament_json['ruleset'] not in valid_rulesets:
            print(path + ' - The "ruleset" field is set to "' + tournament_json['ruleset'] + '", which is an unknown ruleset.')

        # Validate the description
        if type(tournament_json['description']) != str:
            print(path + ' - The "description" field is not a string.')

        # Validate the videos
        if isinstance(tournament_json['videos'], list):
            for video in tournament_json['videos']:
                for field in json_videos_fields:
                    if not checkKey(video, field):
                        print(path + ' - ' + field + ' does not exist!')
                for field in video:
                    if field not in json_videos_fields:
                        print(path + ' - ' + field + ' is unknown!')
        else:
            print(path + ' - The "videos" field is not a list.')

        # Validate the winner field
        if type(tournament_json['winner']) != str:
            print(path + ' - The "winner" field is not a string.')
        elif tournament_json['winner'] == '':
            print(path + ' - The "winner" field is empty.')

        # Check for player duplicates
        for matchup in tournament_json['matchups']:
            for racer in [matchup['winner'], matchup['loser']]:
                validatePlayerName(path, team_event, racer)

        if 'teams' in tournament_json:
            # Check for player duplicates in teams and
            # check that the same player is not on two different teams
            racers4 = {}
            for team in tournament_json['teams']:
                for participant in team['participants']:
                    validatePlayerName(path, team_event, participant)
                    if tournament_json['name'] != "Real Platinum Rod":
                        if participant not in racers4:
                            racers4[participant] = True
                        else:
                            print(path + ' - "' + participant + '" is on two separate teams.')

        # Check for player duplicates in the organizers
        for organizer in tournament_json['organizer']:
            validatePlayerName(path, team_event, organizer)

        # Check for player duplicates in the winner field
        validatePlayerName(path, team_event, tournament_json['winner'])

        # Check for anomalous scores
        for matchup in tournament_json['matchups']:
            if matchup['score'] == '0-0':
                print(path + ' - ' + matchup['winner'] + ' vs ' + matchup['loser'] + ' has an score of "0-0".')
                continue

            match = re.search(r'^(\d+)-(\d+)$', matchup['score'])
            if not match:
                print(path + ' - ' + matchup['winner'] + ' vs ' + matchup['loser'] + ' has an invalid score of "' + matchup['score'] + '".')
                continue

            max_score = 15
            if int(match.group(1)) >= max_score or int(match.group(2)) >= max_score:
                print(path + ' - ' + matchup['winner'] + ' vs ' + matchup['loser'] + ' has a potentially bogus score of "' + matchup['score'] + '".')
                continue


# -----------
# Subroutines
# -----------

def validatePlayerName(path, team_event, racer):
    global racers
    global racers2
    global racers3

    # Validate null racers
    if racer == '' or racer is None:
        print(path + ' - Null racer detected.')
        return

    # Validate test racers
    if 'test' in racer:
        print(path + ' - Test racer detected.')
        return
    if 'placeholder' in racer:
        print(path + ' - Placeholder racer detected.')
        return

    # Validate case stylization
    if racer.lower() not in racers:
        racers[racer.lower()] = racer
    if racers[racer.lower()] != racer:
        print(path + ' - "' + racer + '" has the wrong capitalization. Change it to "' + racers[racer.lower()] + '".')

    # For the rest of the validation, use the lowercase version of the racer's name
    original_racer = racer
    racer = racer.lower()

    # Validate known smurf names
    if 'crazy' in racer and original_racer != 'TehCrazyDuck':
        print(path + ' - Replace "' + original_racer + '" with "antizoubilamakA".')
    if 'reid' in racer and original_racer != 'ReidMercury__' and original_racer != 'Reiden':
        print(path + ' - Replace "' + original_racer + '" with "ReidMercury__".')

    # Validate the amount of underscores
    racer_without_underscores = racer.replace('_', '')
    if racer_without_underscores not in racers2:
        racers2[racer_without_underscores] = racer
    if racers2[racer_without_underscores] != racer:
        print(path + ' - ' + original_racer + ' has the incorrect amount of underscores. There should be ' + str(racers2[racer_without_underscores].count('_')) + ' underscore(s).')

    # Validate the first X characters
    # (but skip team events since most teams will begin with "Team X")
    if team_event:
        return
    duplicate_letters = 5
    if 'bindingof' in racer:
        duplicate_letters += 5
    racer_prefix = racer[:duplicate_letters]
    if racer_prefix not in racers3:
        racers3[racer_prefix] = racer
    if racers3[racer_prefix] != racer:
        print(path + ' - ' + racer + ' is potentially a duplicate of "' + racers3[racer_prefix] + '".')


def checkKey(dict, key): 
    return key in dict.keys()


if __name__ == '__main__':
    main()
