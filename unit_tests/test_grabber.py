import os
import unittest

from grabber import Grabber, ForumPost

BR_THREAD = 'http://www.imdb.com/title/tt0083658/board/thread/117969472'
BR_THREAD_FLAT = 'http://www.imdb.com/title/tt0083658/board/flat/117969472?p=1'
BR_THREAD_MOBILE = 'http://m.imdb.com/title/tt0083658/board/threads/117969472/'

TEST_DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data')

with open(os.path.join(TEST_DATA_PATH, 'flat_forum_page.htm')) as test_html_file:
    TEST_HTML = test_html_file.read()

with open(os.path.join(TEST_DATA_PATH, 'deleted_post.html')) as deleted_post_file:
    DELETED_POST = deleted_post_file.read()

with open(os.path.join(TEST_DATA_PATH, 'valid_post.html')) as valid_post_file:
    VALID_POST = valid_post_file.read()

with open(os.path.join(TEST_DATA_PATH, 'last_page.html')) as last_page_file:
    LAST_PAGE = last_page_file.read()


class Test_Grabber(unittest.TestCase):
    def test_init(self):
        grabber = Grabber(BR_THREAD)
        self.assertEqual(BR_THREAD, grabber.url)
        self.assertEqual(BR_THREAD_FLAT, grabber.flat_thread)

    def test_mobile_url(self):
        grabber = Grabber(BR_THREAD_MOBILE)
        self.assertEqual(BR_THREAD + '/', grabber.url)

    def test_pagination(self):
        grabber = Grabber(BR_THREAD)
        for x in range(1, 11):
            grabber.page_index = x
            self.assertTrue(grabber.current_url.endswith('?p={}'.format(x)))

    def test_title(self):
        grabber = Grabber(BR_THREAD)
        grabber.page_html = grabber.soup(TEST_HTML)
        grabber.find_posts()

        self.assertEqual("Directors And Other Artists On Blade Runner", grabber.title)


class Test_Parsing(unittest.TestCase):
    def setUp(self):
        self.grabber = Grabber(BR_THREAD)
        self.grabber.page_html = self.grabber.soup(TEST_HTML)

    def test_post_finding(self):
        self.grabber.find_posts()
        first_post = self.grabber.posts[0]
        self.assertEqual('CremersAlex', first_post.author)
        self.assertEqual('Directors And Other Artists On Blade Runner', first_post.title)


class Test_ForumPost(unittest.TestCase):
    def setUp(self):
        self.post = ForumPost(Grabber.soup(VALID_POST).find(class_='comment'))

    def test_deleted_post(self):
        post = ForumPost(Grabber.soup(DELETED_POST).find(class_='comment'))
        self.assertTrue(post.deleted)

    def test_json(self):
        post_json = self.post.json

        for member in ['raw', 'author', 'author_url', 'date', 'edited', 'title', 'content',
                       'deleted']:
            self.assertIn(member, post_json)

        self.assertEqual('CremersAlex', post_json['author'])
        self.assertEqual('Directors And Other Artists On Blade Runner', post_json['title'])

    def test_title(self):
        self.assertEqual('Directors And Other Artists On Blade Runner', self.post.title)

    def test_author(self):
        self.assertEqual('CremersAlex', self.post.author)

    def test_author_url(self):
        expected_url = 'http://www.imdb.com/user/ur14503536/'
        self.assertEqual(expected_url, self.post.author_url)

    def test_date(self):
        expected_date = 'Wed Sep 17 2008 02:06:57'
        self.assertEqual(expected_date, self.post.date)

    def test_edited(self):
        expected_edited = 'Fri May 30 2014 01:27:21'
        self.assertEqual(expected_edited, self.post.edited)
