# Imports
import glob
import json
import re

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

# Subroutines
def checkKey(dict, key): 
    return key in dict.keys()

# Looping through every file in the tournaments folder
racers = {}
racers2 = {}
racers3 = {}
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
            print(path + ' - ' + field + ' does not exist!')

    # Validate the winner field
    if tournament_json['winner'] == '':
        print(path + ' - winner field is empty.')

    # Check for player duplicates
    for matchup in tournament_json['matchups']:
        for racer in [matchup['winner'], matchup['loser']]:
            # Validate null racers
            if racer == '' or racer is None:
                print(path + ' - Null racer detected.')
                continue

            # Validate test racers
            if 'test' in racer:
                print(path + ' - Test racer detected.')
                continue
            if 'placeholder' in racer:
                print(path + ' - Placeholder racer detected.')
                continue

            # Validate case stylization
            if racer not in racers and racer.lower() not in racers:
                racers[racer] = True
            if racer not in racers and racer.lower() in racers:
                print(path + ' - ' + racer + ' is styled incorrectly.')

            # For the rest of the validation, use the lowercase version of the racer's name
            original_racer = racer
            racer = racer.lower()

            # Validate the amount of underscores
            racer_without_underscores = racer.replace('_', '')
            if racer_without_underscores not in racers2:
                racers2[racer_without_underscores] = racer
            if racers2[racer_without_underscores] != racer:
                print(path + ' - ' + original_racer + ' has the incorrect amount of underscores.')

            # Validate the first X characters
            # (but skip team events since most teams will begin with "Team X")
            if tournament_json['ruleset'] != 'team':
                duplicate_letters = 5
                if 'bindingof' in racer:
                    duplicate_letters = 10
                racer_prefix = racer[:duplicate_letters]
                if racer_prefix not in racers3:
                    racers3[racer_prefix] = racer
                if racers3[racer_prefix] != racer:
                    print(path + ' - ' + racer + ' is potentially a duplicate of "' + racers3[racer_prefix] + '".')

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
