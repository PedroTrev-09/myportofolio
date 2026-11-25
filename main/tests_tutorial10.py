from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase


class TokenIntegrationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser('token-owner', 'owner@example.com', 'local-test-password')
        cls.visitor = User.objects.create_user('token-visitor', password='local-test-password')

    def test_login_create_logout_and_revoked_token(self):
        login = self.client.post(reverse('api:api_token_auth'), {'username': 'token-owner', 'password': 'local-test-password'}, format='json')
        self.assertEqual(login.status_code, 200)
        token = login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        payload = {'title': 'Token Project', 'category': 'design', 'short_description': 'Short', 'full_description': 'Full', 'tags': 'Flutter', 'image_url': '/static/img/monte.png'}
        self.assertEqual(self.client.post(reverse('api:project-list'), payload, format='json').status_code, 201)
        logout = self.client.post(reverse('api:api-logout'))
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(logout.content, b'')
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.post(reverse('api:project-list'), payload, format='json').status_code, 401)

    def test_missing_invalid_and_non_owner_tokens(self):
        url = reverse('api:project-list')
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 401)
        self.assertEqual(self.client.post(reverse('api:api-logout')).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.visitor).key}')
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 403)
        self.assertEqual(self.client.post(reverse('api:api-logout')).status_code, 204)

    def test_bad_password_does_not_issue_token(self):
        response = self.client.post(reverse('api:api_token_auth'), {'username': 'token-owner', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.owner).exists())

    @override_settings(CORS_ALLOW_ALL_ORIGINS=True)
    def test_local_cors_preflight_allows_authorization(self):
        response = self.client.options(reverse('api:project-list'), HTTP_ORIGIN='http://localhost:8030', HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST', HTTP_ACCESS_CONTROL_REQUEST_HEADERS='authorization,content-type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['access-control-allow-origin'], '*')
        self.assertIn('authorization', response['access-control-allow-headers'])

    @override_settings(CORS_ALLOW_ALL_ORIGINS=False, CORS_ALLOWED_ORIGINS=['https://portfolio.example'])
    def test_production_cors_restricts_origins(self):
        for origin, allowed in [('https://portfolio.example', True), ('https://other.example', False)]:
            response = self.client.get(reverse('api:project-list'), HTTP_ORIGIN=origin)
            self.assertEqual('access-control-allow-origin' in response, allowed)

    def test_session_logout_without_token_is_safe(self):
        client = APIClient()
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse('api:api-logout')).status_code, 204)
