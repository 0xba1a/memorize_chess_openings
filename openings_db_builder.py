import sys
import getopt
import re

import db


shortopts = "f:h:u:"
longopts = ["file=", "help", "user_input"]


def usage():
    print("{} [--file=<input_tsv_file>] [--help] [user_input]".format(sys.argv[0]))


def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err:
        print("ERROR: ", err)
        usage()
        sys.exit(-1)

    return opts, args


def parse_opening(s):
    # try:
        # pattern = r'(\w+(?:\s+\w+)*)(?::\s+(\w+(?:\s+\w+)*))?(?:,\s+(\w+(?:\s+\w+)*))?'
        # tokens = re.findall(pattern, re.escape(s))
    # except Exception as e:
        # print("ERROR: {}\nString: {}".format(e, s))
        # sys.exit(-1)

    name = variation = sub_variation = ""

    # Special Case: c.tsv -> Vienna Gambit, with Max Lange Defense

    if ':' not in s:
        name = s.strip()
    else:
        name = s.split(':')[0].strip()
        ss = s.split(':')[1].strip()

        if ',' not in ss:
            variation = ss
        else:
            variation = ss.split(',')[0].strip()
            sub_variation = ss.split(',', 1)[1].strip()

    # print(name, variation, sub_variation)
    return name, variation, sub_variation


def parse_and_build_db(input_file):
    # First line of the input_file which starts with eco should be ignored
    # From next line onwards the line format is as below
    # <name> [: <variation>, <sub_variation>] pgn
    with open(input_file, "r") as input_db_file:
        lines = input_db_file.readlines()

    for line in lines:
        if line.startswith("eco"):
            continue

        tokens = line.split('\t')

        pgn = tokens[-1].strip()
        eco = tokens[0].strip()

        name, variation, sub_variation = parse_opening(tokens[1])

        key = db.construct_key(name, variation, sub_variation)

        version = db.check_for_duplicate(key, pgn)

        if version >= 0:
            key = db.construct_key(name, variation, sub_variation, version)
            db.add_new_entry(key, name, variation, sub_variation, pgn, version)
        else:
            print("Duplicate entry! Ignoring...\n")

    db.sync()



def main():
    opts, _ = parse_options()

    db.load_db()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

        elif opt in ("-f", "--file"):
            input_file = arg
            parse_and_build_db(input_file)

        elif opt in ("-u", "--user_input"):
            capture_user_inputs_and_build_db()



if __name__ == "__main__":
    main()
