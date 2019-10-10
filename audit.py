# Imports
import glob
import json

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

    # Check for player duplicates
    for matchup in tournament_json['matchups']:
        for racer in [matchup['winner'], matchup['loser']]:
            # Validate case stylization
            if racer not in racers and racer.lower() not in racers:
                racers[racer] = True
            if racer not in racers and racer.lower() in racers:
                print(path + ' - ' + racer + ' is styled incorrectly.')

            # Validate the amount of underscores
            racer_without_underscores = racer.replace('_', '')
            if racer_without_underscores not in racers2:
                racers2[racer_without_underscores] = racer
            if racers2[racer_without_underscores] != racer:
                print(path + ' - ' + racer + ' has the incorrect amount of underscores. ' + 
                      '(It should be "' + racers2[racer_without_underscores] + '".)')

            # Validate the first X characters
            # (but skip team events since most teams will begin with "Team X")
            if tournament_json['ruleset'] != 'team':
                racer_prefix = racer[:5]
                if racer_prefix not in racers3:
                    racers3[racer_prefix] = racer
                if racers3[racer_prefix] != racer:
                    print(path + ' - ' + racer + ' is potentially a duplicate of "' + racers3[racer_prefix] + '".')
