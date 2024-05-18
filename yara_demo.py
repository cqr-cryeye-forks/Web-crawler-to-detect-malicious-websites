import re
import yara
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)


def run_yara(filename, rules):
    matched = rules.match(filename)
    hidden_links = []

    for match in matched:
        rule_name = match.rule
        strings = match.strings

        logging.info(f"{rule_name} matched {len(strings)} times.")

        for string in strings:
            match_data = string[2]
            logging.info(f"match: {match_data}")

            if rule_name == "hidden_link":
                hidden_links.append(match_data)

    link1_color = "black"
    body1_color = "white"
    body2_color = "white"

    for v in hidden_links:
        body1 = re.search(r"background-color *: *(.*?);", v)
        if body1:
            body1_color = body1.group(1)

        body2 = re.search(r'bgcolor *= *["\'](.*?)[\'"]', v)
        if body2:
            body2_color = body2.group(1)

        link1 = re.search(r"[^-]color *: *(.*?);", v)
        if link1:
            link1_color = link1.group(1)

    if link1_color == body1_color or link1_color == body2_color:
        logging.info("Hidden link found")

    logging.info("done")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <yara_rules_file>")
        exit(1)

    rules_file = sys.argv[1]

    if not os.path.isfile(rules_file):
        print(f"Yara rules file {rules_file} does not exist.")
        exit(1)

    try:
        rules = yara.compile(rules_file)
    except yara.SyntaxError as e:
        print(f"Error compiling Yara rules: {e}")
        exit(1)

    i = 1
    while True:
        file_name = f"./html/{i}.html"
        if os.path.isfile(file_name):
            logging.info("-------------------------------------")
            logging.info(f"GOT {file_name}")
            run_yara(file_name, rules)
            i += 1
        else:
            break
