from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, get_user_model, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.test import LiveServerTestCase
from selenium.webdriver import DesiredCapabilities
from splinter import Browser


class BaseLiveServer(LiveServerTestCase):
    username = 'spam'
    password = 'eggs'

    @classmethod
    def setUpClass(cls):
        super(BaseLiveServer, cls).setUpClass()
        capabilities = DesiredCapabilities.PHANTOMJS.copy()
        capabilities['phantomjs.page.customHeaders.Accept-Language'] = 'en,en_US;q=0.8'
        cls.browser = Browser('phantomjs', desired_capabilities=capabilities)
        cls.driver = cls.browser.driver

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(BaseLiveServer, cls).tearDownClass()

    def get_or_create_user(self):
        User = get_user_model()

        try:
            user = User.objects.get(username__exact=self.username)
        except User.DoesNotExist:
            user = User.objects.create_user(self.username, '', self.password)

        return user

    def create_auth_session(self):
        user = self.get_or_create_user()
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        self.browser.visit(self.live_server_url)
        self.driver.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/'))

    def abspath(self, url):
        return '{}{}'.format(self.live_server_url, url)

    def visit(self, url):
        abspath = self.abspath(url)
        self.browser.visit(abspath)


class LoginTestCase(BaseLiveServer):

    def test_login_with_valid_user(self):
        self.get_or_create_user()
        self.visit('/')

        self.assertEqual('Login', self.browser.title)

        self.browser.fill('username', self.username)
        self.browser.fill('password', self.password)
        self.browser.find_by_name('login').click()

        welcome_text = self.browser.find_by_css('.navbar-text').first

        self.assertEqual('Welcome, %s!' % self.username.capitalize(), welcome_text.html)
