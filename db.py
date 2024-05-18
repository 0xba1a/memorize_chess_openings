import json

openings_db = "db/openings_db.json"
puzzles_db = "db/puzzles_db.json"

OPENINGS = {}
PUZZLES = {}


def load_db():
    global OPENINGS, PUZZLES
    with open(openings_db, "r") as opening_db_file:
        OPENINGS = json.load(opening_db_file)

    with open(puzzles_db, "r") as puzzles_db_file:
        PUZZLES = json.load(puzzles_db_file)


def construct_key(name, variation, sub_variation, version=None):
    key = name

    if sub_variation:
        key = "{}: {}, {}".format(name, variation, sub_variation)
    elif variation:
        key = "{}: {}".format(name, variation)
    elif name:
        key = name

    if version:
        key = "{}_ver_{}".format(key, version)

    return key


def deconstruct_key(key):
    return OPENINGS[key]["name"], OPENINGS[key]["variation"], OPENINGS[key]["sub_variation"]


def get_next_version(name, variation, sub_variation, key):
    version = 0
    for o_key in OPENINGS.keys():
        if key in o_key:
            if name == OPENINGS[o_key]["name"]                        \
                and variation == OPENINGS[o_key]["variation"]         \
                and sub_variation == OPENINGS[o_key]["sub_variation"] \
                and version <= OPENINGS[o_key]["version"]:
                    version = OPENINGS[o_key]["version"] + 1
    return version


def check_for_duplicate(key, pgn):
    if key in OPENINGS:
        if pgn == OPENINGS[key]["pgn"]:
            return -1

        name, variation, sub_variation = deconstruct_key(key)
        return get_next_version(name, variation, sub_variation, key)

    else:
        return 0


def add_new_entry(key, name, variation, sub_variation, pgn, version=0):
    global OPENINGS, PUZZLES
    if key in OPENINGS:
        print("ERROR: Duplicate entry: {}".format(key))
        print("{}: {}, {}".format(name, variation, sub_variation))
        return -1

    OPENINGS[key] = {
            "pgn": pgn,
            "name": name,
            "variation": variation,
            "sub_variation": sub_variation,
            "notes": "",
            "puzzelized": False,
            "version": version
        }


def sync():
    with open(openings_db, "w") as openings_db_file:
        openings_db_file.write(json.dumps(OPENINGS))
