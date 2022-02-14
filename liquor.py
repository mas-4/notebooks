import os
from bs4 import BeautifulSoup
import requests
import re
import time
import random

root_url = 'https://www.liquor.com/cocktail-by-spirit-4779438'
root_dir = 'liquor'

tovisit = set()
visited = set()


def get_links(soup):
    return {l['href'] for l in soup.find_all('a', {'href': re.compile(r'/recipes/')})}


def process_link(link):
    resp = requests.get(link)
    if resp.status_code != 200:
        return []
    with open(os.path.join(root_dir, link.strip('/').split('/')[-1] + '.html'), 'wt') as f:
        f.write(resp.text)
    soup = BeautifulSoup(resp.text, 'lxml')
    return get_links(soup)


def save_state():
    with open('state.txt', 'at') as f:
        f.write('\n'.join(visited))
    with open('tovisit.txt', 'wt') as f:
        f.write('\n'.join(tovisit))


def main():
    if not tovisit:
        r = requests.get(root_url)
        tovisit.update(get_links(BeautifulSoup(r.text, 'lxml')))
        os.makedirs(root_dir, exist_ok=True)
    while len(tovisit) > 0:
        link = tovisit.pop()
        try:
            links = process_link(link)
        except:
            pass
        visited.add(link)
        tovisit.update([link for link in links if link not in visited])
        save_state()
        time.sleep(random.randint(1, 3))


if __name__ == '__main__':
    if os.path.exists('state.txt'):
        with open('state.txt', 'rt') as f:
            visited = set(f.read().splitlines())
    if os.path.exists('tovisit.txt'):
        with open('tovisit.txt', 'rt') as f:
            tovisit = set(f.read().splitlines())
    main()
