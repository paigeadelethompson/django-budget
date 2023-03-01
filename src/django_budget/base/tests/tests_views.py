from __future__ import unicode_literals

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login, logout_then_login
from django.core.urlresolvers import reverse

from base.utils import BaseTestCase


class LoginViewTestCase(BaseTestCase):
    view_function = login

    def test_view_response(self):
        request = self.factory.get()
        response = self.view(request)
        response.render()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed('registration/login.html')
        self.assertIsInstance(
            response.context_data['form'], AuthenticationForm)

    def test_redirects_after_login(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        User.objects.create_user('foo', 'foo@bar', 'bar')
        form_data = {'username': 'foo', 'password': 'bar'}
        request = self.factory.post(data=form_data, user=self.mock_user)
        request._dont_enforce_csrf_checks = True
        request.session = self.mock_session
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('dashboard'), response._headers['location'][1])


class LogoutViewTestCase(BaseTestCase):
    view_function = logout_then_login

    def test_redirect_after_logout(self):
        request = self.factory.get(user=self.mock_user)
        request.session = self.mock_session
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('login'), response._headers['location'][1])


class SetupViewTestCase(BaseTestCase):
    from base.views import BudgetSetupView

    view_class = BudgetSetupView

    def test_view_response(self):
        response = self.get()

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'setup.html')

    def test_html_content(self):
        response = self.get()

        self.assertContains(response, 'Setup', count=3)
        self.assertContains(response, reverse('category:category_list'))
        self.assertContains(response, reverse('budget:budget_list'), count=2)

    def test_redirect_if_anonymous(self):
        url = reverse('setup')
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = self.view(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual('%s?next=%s' %
                         (reverse('login'), url), response._headers['location'][1])

    def get(self):
        url = reverse('setup')
        request = self.factory.get(path=url, user=self.mock_user)
        response = self.view(request)
        return response.render()


class MenusTestCase(BaseTestCase):

    def test_base_html_menus_if_anonymous(self):
        url = reverse('login')
        request = self.factory.get(path=url, user=self.anonymous_user)
        response = login(request)

        self.assertNotContains(response, reverse('setup'))
        self.assertNotContains(response, reverse('dashboard'))
        self.assertNotContains(response, reverse('summary:summary_list'))
        self.assertContains(response, reverse('login'))
        self.assertNotContains(response, reverse('logout'))

    def test_base_html_menus_if_not_anonymous(self):
        url = reverse('login')
        request = self.factory.get(path=url, user=self.mock_user)
        response = login(request)

        self.assertContains(response, reverse('setup'))
        self.assertContains(response, reverse('dashboard'))
        self.assertContains(response, reverse('summary:summary_list'))
        self.assertNotContains(response, reverse('login'))
        self.assertContains(response, reverse('logout'))


class IndexViewTest(BaseTestCase):
    from base.views import IndexRedirectView

    view_class = IndexRedirectView

    def test_index_view_should_redirect_to_dashboard(self):
        request = self.factory.get(user=self.mock_user)
        response = self.view(request)

        self.assertEqual(301, response.status_code)
        self.assertEqual(
            reverse('dashboard'), response._headers['location'][1])
