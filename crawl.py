import argparse
import json
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup
import os
import pathlib
from typing import Final


def crawl(start_url, output_file):
    cnt = 0
    urls = [start_url]
    visited = [start_url]
    data = []
    errors = []

    # Ensure directories exist
    os.makedirs("html", exist_ok=True)
    os.makedirs("header", exist_ok=True)

    while urls:
        current_url = urls.pop(0)
        print("--")
        print("Current URL:", current_url)

        try:
            response = urlopen(current_url)
        except URLError as e:
            error_message = f"Failed to open {current_url}: {e}"
            print(error_message)
            errors.append({"error": error_message})
            continue

        html_text = response.read()
        header_text = str(response.info())
        soup = BeautifulSoup(html_text, 'html.parser')
        soup_header = BeautifulSoup(header_text, 'html.parser')

        cnt += 1
        with open(f"html/{cnt}.html", "w", encoding="utf-8") as html_file:
            html_file.write(soup.prettify())
        with open(f"header/{cnt}", "w", encoding="utf-8") as header_file:
            header_file.write(soup_header.prettify())

        links = soup.find_all('a', href=True)
        temp_links = []

        for tag in links:
            href = urljoin(current_url, tag['href'])
            if href not in visited:
                temp_links.append(href)
                urls.append(href)
                visited.append(href)

        print(f"{current_url} has {len(temp_links)} links.")
        data.append({"link": current_url})
        for link in temp_links:
            print(link)
            data.append({"link": link})

    print(f"{len(visited)} sites are visited\n")
    for site in visited:
        print(site, "\n")

    output_data = {
        "links": data,
        "errors": errors
    }
    if output_data == {"links": [], "errors": []}:
        output_data = {
            "Error": "Nothing found by Web-crawler-to-detect-malicious-websites"
        }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a website and save the results.")
    parser.add_argument("--target", type=str, help="Target URL to crawl")
    parser.add_argument("--output", type=str, help="Output file name (example: data.json)")

    args = parser.parse_args()

    output_path: Final[pathlib.Path] = pathlib.Path(__file__).parent / args.output

    crawl(args.target, output_path)
