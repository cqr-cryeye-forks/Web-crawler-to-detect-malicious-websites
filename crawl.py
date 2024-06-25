import argparse
from http.client import RemoteDisconnected
import json
import time
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup
import os
import pathlib
from typing import Final


def crawl(url, output_file=None):
    for scheme in ["http://", "https://"]:
        if url.startswith(scheme):
            url = url[len(scheme):]

    start_url1 = "http://" + url
    start_url2 = "https://" + url
    urls = [start_url1, start_url2]
    visited = [start_url1, start_url2]
    data = []
    errors = []

    # Ensure directories exist
    # os.makedirs("html", exist_ok=True)
    # os.makedirs("header", exist_ok=True)
    # cnt = 0
    for url in urls:
        current_url = url

        try:
            response = urlopen(current_url)
        except Exception as e:
            error_message = f"Failed to open {current_url}: {e}"
            errors.append({"error": error_message})
            continue

        html_text = response.read()
        soup = BeautifulSoup(html_text, 'html.parser')
        # header_text = str(response.info())
        # soup_header = BeautifulSoup(header_text, 'html.parser')

        # cnt += 1
        # with open(f"html/{cnt}.html", "w") as html_file:
        #     html_file.write(soup.prettify())
        # with open(f"header/{cnt}", "w") as header_file:
        #     header_file.write(soup_header.prettify())

        links = soup.find_all('a', href=True)
        temp_links = []

        for tag in links:
            try:
                href = urljoin(current_url, tag['href'])
                if href not in visited:
                    temp_links.append(href)
                    urls.append(href)
                    visited.append(href)
            except ValueError as e:
                error_message = f"Failed to open {current_url}: {e}"
                errors.append({"error": error_message})
                continue

        data.append({"link": current_url})
        for link in temp_links:
            data.append({"link": link})

    output_data = {
        "links": data,
        "errors": errors
    }
    if output_data == {"links": [], "errors": []}:
        output_data = {
            "Error": "Nothing found by Web-crawler-to-detect-malicious-websites"
        }
    return output_data


def add_output_in_jsonfile(output_path: pathlib.Path, output_data: dict):
    try:
        with open(output_path, "r") as jf_1:
            existing_data = json.load(jf_1)
    except FileNotFoundError:
        existing_data = {}

    existing_data.update(output_data)

    with open(output_path, "w") as jf_2:
        json.dump(existing_data, jf_2, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a website and save the results.")
    parser.add_argument("--target", type=str, help="Target URL to crawl")
    parser.add_argument("--output", type=str, help="Output file name (example: data.json)")

    args = parser.parse_args()

    output_path: Final[pathlib.Path] = pathlib.Path(__file__).parent / args.output
    try:
        output_data = {
            "crawl": crawl(args.target)
        }
    except RemoteDisconnected as e:
        output_data = {
            "crawl": {
                "Error": "Remote end closed connection without response"
            }
        }
    add_output_in_jsonfile(output_path=output_path, output_data=output_data)

    print(output_data)
