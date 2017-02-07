import logging
import time
import urlparse

import requests
from bs4 import BeautifulSoup

PARSER = 'html.parser'
IMDB_BASE_URL = 'www.imdb.com'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

GRABBER_LOG = logging.getLogger(__name__)
GRABBER_LOG.addHandler(logging.StreamHandler())
GRABBER_LOG.setLevel(logging.INFO)


class Grabber(object):
    def __init__(self, url):
        self.url = transform_mobile_url(url)
        self.page_index = 1
        self.flat_thread = self.get_flat_url()
        self._end = None

        self.posts = []
        self.page_html = None

    @property
    def current_url(self):
        url = urlparse.urlparse(self.flat_thread)
        query = 'p={}'.format(self.page_index)

        raw_url = (url.scheme, url.netloc, url.path, url.params, query, url.fragment)
        return urlparse.urlunparse(raw_url)

    @property
    def title(self):
        return self.posts[0].title

    @property
    def end(self):
        return self._get_end()

    def _get_end(self):
        if not self._end:
            url = urlparse.urlparse(self.flat_thread)
            query = 'p=last'
            raw_url = (url.scheme, url.netloc, url.path, url.params, query, url.fragment)
            last_url = urlparse.urlunparse(raw_url)
            last_page = requests.get(last_url, headers=HEADERS)
            if not last_page.ok:
                raise RuntimeError("Error reaching URL {}: {}".format(last_url, last_page.reason))
            self._end = int(last_page.url.split('?p=')[-1])
        else:
            return self._end

    def get_flat_url(self):
        parsed = urlparse.urlparse(self.url)

        path = parsed.path.replace('/thread/', '/flat/')
        query = 'p={}'.format(self.page_index)

        raw_url = (parsed.scheme, parsed.netloc, path, parsed.params, query, parsed.fragment)
        return urlparse.urlunparse(raw_url)

    @staticmethod
    def soup(raw_html):
        return BeautifulSoup(raw_html, PARSER)

    def find_posts(self):
        posts_body = self.page_html.select('#lhs > div > div.thread.mode-flat')[0]
        self.posts.extend([ForumPost(post) for post in posts_body.find_all(class_='comment')])

    def is_last_page(self):
        return self.page_index == self.end

    def get_page(self):
        GRABBER_LOG.info("Getting page %s", self.current_url)

        response = requests.get(self.current_url, headers=HEADERS)
        if response.ok:
            return response.content
        else:
            raise RuntimeError("Page {} unavailable: {}.".format(self.current_url, response.reason))

    def run(self):
        done = False

        while not done:
            done = self.is_last_page()
            self.page_html = self.soup(self.get_page())
            self.find_posts()

            # sleep to avoid hammering IMDB
            time.sleep(0.1)
            self.page_index += 1

    @property
    def json_output(self):
        if self.posts:
            return [post.json for post in self.posts if not post.deleted]
        else:
            return None


def transform_mobile_url(url):
    parsed = urlparse.urlparse(url)
    netloc = parsed.netloc
    if netloc.startswith('m.imdb'):
        netloc = 'www.imdb.com'

    path = parsed.path
    if '/threads/' in path:
        # slight difference in how mobile treats path to the thread
        path = path.replace('/threads/', '/thread/')

    raw_url = (parsed.scheme, netloc, path, parsed.params, parsed.query, parsed.fragment)
    return urlparse.urlunparse(raw_url)


class ForumPost(object):
    def __init__(self, thread_soup):
        self.soup = thread_soup

    @property
    def date(self):
        return self.soup.find(class_='timestamp').text

    @property
    def edited(self):
        info = self.soup.find(class_='info')
        if info:
            info = info.text
            info = info.replace('\n', '')
            info = info.replace('Post Edited:', '')
            info = info.lstrip().rstrip()
        return info

    @property
    def raw(self):
        return unicode(self.soup)

    @property
    def raw_content(self):
        return self.soup.find(class_='body')

    @property
    def raw_author(self):
        return self.soup.find(class_='user')

    @property
    def deleted(self):
        return 'deleted' in self.soup['class']

    @property
    def content(self):
        return self.raw_content.text

    @property
    def title(self):
        return self.soup.find('h2').text

    @property
    def author(self):
        return self.raw_author.text

    @property
    def author_url(self):
        path = self.raw_author.find('a')['href']
        return urlparse.urlunparse(('http', IMDB_BASE_URL, path, None, None, None))

    @property
    def json(self):
        return self._make_json()

    def _make_json(self):
        json = {
            'raw': self.raw,
            'author': self.author,
            'author_url': self.author_url,
            'date': self.date,
            'edited': self.edited,
            'title': self.title,
            'content': self.content,
            'deleted': self.deleted
        }

        return json
