from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import Client

from djet.testcases import ViewTestCase
from djet.assertions import MessagesAssertionsMixin, StatusCodeAssertionsMixin
from djet.utils import refresh

from mock import MagicMock

User = get_user_model()


class BaseTestCase(MessagesAssertionsMixin,
                   StatusCodeAssertionsMixin,
                   ViewTestCase):

    username = 'spam'
    password = 'eggs'

    @classmethod
    def setUpClass(cls):
        cls.anonymous_user = AnonymousUser()
        cls.mock_user = MagicMock()
        cls.mock_user.is_authenticated = MagicMock(return_value=True)
        cls.mock_session = MagicMock()
        cls.mock_session.flush = MagicMock()

    def setUp(self, *args, **kwargs):
        super(BaseTestCase, self).setUp(*args, **kwargs)
        self.client = Client()

    def login(self):
        self.get_or_create_user()
        self.client.login(username=self.username, password=self.password)

    def get_or_create_user(self):
        try:
            User.objects.get(username__exact=self.username)

        except User.DoesNotExist:
            User.objects.create_user(self.username, '', self.password)

    def refresh(self, instance):
        return refresh(instance)
