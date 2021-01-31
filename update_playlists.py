import os
import json
import random
import string

def gen_id():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(16)))

background_dir = os.path.join(os.getcwd(), "sounds", "Background")
base_background_dir = "modules/dnd-extras/sounds/Background/"
combat_dir = os.path.join(os.getcwd(), "sounds", "Combat")
base_combat_dir = "modules/dnd-extras/sounds/Combat/"

pack_db = os.path.join(os.getcwd(), "packs", "combat-background-playlists.db")

combat_db = {
	"name": "Combat",
	"permission": {
		"default": 0,
		"ODc5MmQ1Y2RhY2M3": 3
	},
	"flags": {},
	"sounds": [],
	"mode": 1,
	"playing": False,
	"_id": "1muCWyszK4kILSaq"
}

background_db = {
	"name": "Background",
	"permission": {
		"default": 0,
		"ODc5MmQ1Y2RhY2M3": 3
	},
	"flags": {},
	"sounds": [],
	"mode": 1,
	"playing": False,
	"_id": "Rd29G8shPGd4cPdk"
}

item = {
	"_id": "",
	"flags": {},
	"path": "",
	"repeat": False,
	"volume": 0.25,
	"name": "",
	"playing": False,
	"streaming": False
}

# loop over background playlist
for file in os.listdir(background_dir):
	background_db["sounds"].append({
		"_id": gen_id(),
		"flags": {},
		"path": base_background_dir + file,
		"repeat": False,
		"volume": 0.25,
		"name": os.path.splitext(file)[0],
		"playing": False,
		"streaming": False
	})

# loop over background playlist
for file in os.listdir(combat_dir):
	combat_db["sounds"].append({
		"_id": gen_id(),
		"flags": {},
		"path": base_combat_dir + file,
		"repeat": False,
		"volume": 0.25,
		"name": os.path.splitext(file)[0],
		"playing": False,
		"streaming": False
	})

with open(pack_db, "w") as f:
	json.dump(background_db, f)
	f.write("\n")
	json.dump(combat_db, f)