import os.path
import time

import bs4
import requests as r

save_path = '.'

headers = {'User-Agent': 'Mozilla/5.0'}

def page(url): 
    site = None
    i = 0
    while site == None:
        try:
            site = r.get(url, headers=headers, timeout=100)
        except ConnectionError:
            i += 1
            time.sleep(2)
            if i == 5:
                return
    page_html = site.content
    page = bs4.BeautifulSoup(page_html, "html.parser")
    return page


def xml(url):
    site = r.get(url)
    page_html = site.text
    page = bs4.BeautifulSoup(page_html, "lxml")
    return page


def file(file_name):
    file = open(file_name, "w", encoding="utf-8")
    return file


def req(url):
    try:
        req = r.get(url, headers=headers, timeout=100)

    except ConnectionResetError:
        print('connection reset error')
        time.sleep(2)
        return
    except r.exceptions.Timeout:
        print('requests.exceptions timeout error')
        time.sleep(2)
        return
    except r.exceptions.ConnectionError:
        print('connectionerror')
        time.sleep(2)
        return

    try:

        return req.json()
    except ValueError:
        time.sleep(2)
        return

