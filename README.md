# The Binding of Isaac: Rebirth Tournaments

This is a [historical archive](https://github.com/Krakenos/BoIR-trueskill/tree/master/tournaments) of every *[The Binding of Isaac: Rebirth](http://store.steampowered.com/app/250900/The_Binding_of_Isaac_Rebirth/)* tournament that has ever been played. (This includes tournaments for the two DLCs, *[The Binding of Isaac: Afterbirth](https://store.steampowered.com/app/401920/The_Binding_of_Isaac_Afterbirth/)* and *[The Binding of Isaac: Afterbirth+](https://store.steampowered.com/app/570660/The_Binding_of_Isaac_Afterbirth/)*.)

These tournaments are used to calculate TrueSkill ratings for players on [isaacrankings.com](https://isaacrankings.com/). The source code for the site can be found [here](https://github.com/Krakenos/BoIR-trueskill-site).

The "tournament_json_creator.py" script can be used to automatically convert a Challonge bracket to a JSON file. To use it:
* `pip install -r requirements.txt`
* `python tournament_json_creator.py`
