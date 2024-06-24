import re
import json
import argparse
import pathlib
import time
from typing import Final
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def is_ip_address(url):
    return re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', url) is not None


def get_domain_info(url):
    parsed_url = urlparse(url)
    domain = parsed_url.hostname
    path = parsed_url.path
    return domain, path


def domain_length_score(domain_length):
    if 1 <= domain_length <= 4:
        return 7
    elif 4 < domain_length <= 7:
        return 6
    elif 8 <= domain_length <= 10:
        return 5
    elif domain_length > 10:
        return 3
    return 0


def url_length_score(url_length, domain_length):
    if url_length == domain_length:
        return 2
    elif url_length >= 100:
        return 8
    elif 40 < url_length <= 100:
        return 7
    elif 30 < url_length <= 40:
        return 6
    elif 20 < url_length <= 30:
        return 5
    elif 10 < url_length <= 20:
        return 4
    elif url_length <= 10:
        return 3
    return 0


def unique_character_ratio_score(ratio):
    if 0 < ratio <= 0.25:
        return 8
    elif 0.25 < ratio <= 0.40:
        return 7
    elif 0.40 < ratio <= 0.55:
        return 6
    elif 0.55 < ratio <= 0.70:
        return 5
    elif 0.70 < ratio <= 0.80:
        return 4
    elif ratio > 0.80:
        return 3
    return 0


def brand_name_score(domain, brand_names, ignore_names, malicious_names):
    flag = 0
    for brand in brand_names:
        if brand in domain:
            if domain == brand or re.match(rf".*\.{brand}\..*", domain) or re.match(rf".*\.{brand}", domain):
                return "Not phishing"
            if re.match(rf".*{brand}.*", domain):
                flag += 1

            for ignore in ignore_names:
                if re.match(rf".*\.{ignore}\..*", domain):
                    return "Not phishing"
            for malicious in malicious_names:
                if malicious in domain:
                    flag += 1
    return flag


def alexa_rank_score(url):
    try:
        alexa_data = urlopen(f"http://www.alexa.com/siteinfo/{url}").read()
        soup = BeautifulSoup(alexa_data, "lxml")
        list_rank = re.findall(r"metrics-data align-vmiddle..([0-9,]*)<\/strong>", str(soup))
        if list_rank:
            rank = int(list_rank[0].replace(',', ''))
            if 0 < rank < 50000:
                return 1, rank
            elif 50000 <= rank <= 100000:
                return 2, rank
            elif rank > 100000:
                return 8, rank
        return 10, None
    except URLError:
        return 10, None


def check_phish(url, output_path=None):
    data = {
        "url": url,
        "domain_length": 0,
        "url_length": 0,
        "unique_character_ratio": 0,
        "brand_name_score": 0,
        "alexa_rank_score": 0,
        "alexa_rank": None,
        "final_score": 0,
        "phishing_probability": 0
    }

    for scheme in ["http://", "https://"]:
        if url.startswith(scheme):
            url = url[len(scheme):]

    if is_ip_address(url):
        data["final_score"] = 0.90
        data["phishing_probability"] = 90
        # with open(output_path, 'w') as jf:
        #     json.dump(data, jf, indent=4)
        return data

    domain, path = get_domain_info(url)
    if not domain:
        data["final_score"] = "Invalid URL"
        # with open(output_path, 'w') as jf:
        #     json.dump(data, jf, indent=4)
        return data

    score = [0] * 5

    data["domain_length"] = len(domain)
    score[0] = domain_length_score(data["domain_length"])

    data["url_length"] = len(domain) + len(path)
    score[1] = url_length_score(data["url_length"], data["domain_length"])

    unique_chars = set(domain)
    data["unique_character_ratio"] = len(unique_chars) / len(domain)
    score[2] = unique_character_ratio_score(data["unique_character_ratio"])

    brand_names = ["google", "yahoo", "g00gle", "yah00", "runescape", "vogella", "v0gella"]
    ignore_names = ["google-melange", "google-styleguide", "googlesciencefair", "thinkwithgoogle",
                    "googleforentrepreneurs", "withgoogle"]
    malicious_names = ["account", "free", "membs", "membership", "hacks", "lottery", "prize", "money"]

    flag = brand_name_score(domain, brand_names, ignore_names, malicious_names)
    if isinstance(flag, str):
        data["final_score"] = flag
        # with open(output_path, 'w') as jf:
        #     json.dump(data, jf, indent=2)
        return data
    else:
        data["brand_name_score"] = flag
        if flag == 1:
            score[3] = 8
        elif flag == 2:
            score[3] = 9
        elif flag >= 3:
            score[3] = 10
        elif flag == 0:
            score[3] = 3

    score[4], data["alexa_rank"] = alexa_rank_score(url)
    data["alexa_rank_score"] = score[4]

    total_score = sum(score)
    final_score = total_score / 50
    data["final_score"] = final_score
    data["phishing_probability"] = final_score * 100

    if final_score >= 0.50:
        try:
            page_content = urlopen(url).read()
            page_soup = BeautifulSoup(page_content, "lxml")
            if page_soup.find_all(attrs={"type": "password"}):
                rev_ratio = (total_score + 9) / 60
                data["phishing_probability"] = rev_ratio * 100
        except URLError:
            data["phishing_probability"] = "Failed to open URL for password check"
    else:
        data["phishing_probability"] = final_score * 100

    # with open(output_path, 'w') as jf:
    #     json.dump(data, jf, indent=2)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phishing URL Checker")
    parser.add_argument('--target', type=str, required=True, help="Target URL to check")
    # parser.add_argument('--output', type=str, required=True, help="Output JSON file path")
    args = parser.parse_args()

    target_url = args.target
    # output_path = args.output

    # OUTPUT_JSON: Final[pathlib.Path] = pathlib.Path(__file__).parent / args.output

    data = check_phish(target_url)
    print(data)
