import argparse
import json
import time
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup
import os
import pathlib
from typing import Final


def crawl(start_url, output_file=None):
    cnt = 0

    for scheme in ["http://", "https://"]:
        if start_url.startswith(scheme):
            url = start_url[len(scheme):]

    start_url1 = "http://" + url
    start_url2 = "https://" + url
    urls = [start_url1, start_url2]
    visited = [start_url1, start_url2]
    data = []
    errors = []

    # Ensure directories exist
    os.makedirs("html", exist_ok=True)
    os.makedirs("header", exist_ok=True)

    while urls:
        current_url = urls.pop(0)

        try:
            response = urlopen(current_url)
        except URLError as e:
            error_message = f"Failed to open {current_url}: {e}"
            errors.append({"error": error_message})
            continue

        html_text = response.read()
        header_text = str(response.info())
        soup = BeautifulSoup(html_text, 'html.parser')
        soup_header = BeautifulSoup(header_text, 'html.parser')

        cnt += 1
        with open(f"html/{cnt}.html", "w") as html_file:
            html_file.write(soup.prettify())
        with open(f"header/{cnt}", "w") as header_file:
            header_file.write(soup_header.prettify())

        links = soup.find_all('a', href=True)
        temp_links = []

        for tag in links:
            href = urljoin(current_url, tag['href'])
            if href not in visited:
                temp_links.append(href)
                urls.append(href)
                visited.append(href)

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
    # with open(output_file, "w") as jf:
    #     json.dump(output_data, jf, ensure_ascii=False, indent=2)
    return output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a website and save the results.")
    parser.add_argument("--target", type=str, help="Target URL to crawl")
    # parser.add_argument("--output", type=str, help="Output file name (example: data.json)")

    args = parser.parse_args()

    # output_path: Final[pathlib.Path] = pathlib.Path(__file__).parent / args.output

    output_data = crawl(args.target)
    print(output_data)
