import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv("base_url")

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


def parse_page_content(content):
    global links_found
    soup = BeautifulSoup(content, "html.parser")

    title = soup.title.text
    print(f"Page Title: {title}")

    links = get_page_links(soup)
    for link in links:
        if link not in links_found.keys() and link.startswith(base_url):
            # Add to link found
            links_found[link] = False
            print(f"link added: [{link}]")
            print(f"Total len of links {len(links_found)}")


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
    global links_found
    url = base_url

    completed = False
    while not completed:
        page_content = get_page_content(url)

        if page_content:
            parse_page_content(page_content)

        links_found[url] = True

        url = get_next_link()
        if url is None:
            completed = True


if __name__ == "__main__":
    main()
