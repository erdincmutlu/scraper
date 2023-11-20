import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from pathlib import Path

# Dict of found link as key and visited (bool) as value
links_found = {}


def get_page_content(url):
    print(f"Parsing page: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve content from {url}")
        return None


def parse_page_content(content, url):
    global links_found
    soup = BeautifulSoup(content, "html.parser")

    title = soup.title.text
    print(f"Page Title: {title}")

    write_page(soup, url)

    links = get_page_links(soup)
    for link in links:
        if link not in links_found.keys() and link.startswith(base_url):
            # Add to link found
            links_found[link] = False

    print(f"Page finished. Total links found {len(links_found)}")


def write_page(content, url):
    filename = os.path.join("output", valid_filename(url) + ".txt")

    # Writing the text content to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"URL: {url}\n")
        file.write(f"Title: {content.title.text}\n")


def valid_filename(filename):
    # Remove invalid characters from the filename
    valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    valid_filename = "".join(c if c in valid_chars else "_" for c in filename)

    return valid_filename


def get_page_links(soup):
    links = []
    for link in soup.find_all("a"):
        l = link.get("href")

        # Don't process linking to doc or pdf file
        if l.endswith(".doc") or l.endswith(".pdf"):
            continue

        if l == "/" or l == "":
            continue

        absolute = make_absolute_url(l)

        # Don't follow external links
        if not absolute.startswith(base_url):
            continue

        print(f"Found link: {absolute}")
        links.append(absolute)

    return links


def make_absolute_url(link):
    if link.startswith("http://") or link.startswith("https://"):
        return link

    if link.startswith("/"):
        link = link[1:]

    return base_url + "/" + link


def get_next_link():
    for key, value in links_found.items():
        if value is False:
            return key

    return None


def main():
    load_dotenv()

    global links_found
    global base_url
    base_url = os.getenv("base_url")

    Path("output").mkdir(parents=True, exist_ok=True)

    completed = False
    url = base_url
    while not completed:
        page_content = get_page_content(url)

        if page_content:
            parse_page_content(page_content, url)

        links_found[url] = True

        url = get_next_link()
        if url is None:
            completed = True


if __name__ == "__main__":
    main()
