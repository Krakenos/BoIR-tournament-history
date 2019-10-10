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

    # Check for fields
    for field in json_fields:
        if not checkKey(tournament_json, field):
            print(path + ' - ' + field + ' does not exist!')
