from django.test import TestCase
from django.contrib.auth.models import User
import json
import requests

from unittest.mock import patch, MagicMock

class UserAuthenticationTests(TestCase):
    """
    Tests for user signup, login, and logout functionality.
    """

    def setUp(self):
        """Set up test data."""
        self.username = "testuser"
        self.password = "strong-password-123"

    def test_signup_and_login_flow(self):
        """
        Tests that a user can successfully sign up and then log in.
        """
        # 1. Test user signup
        signup_response = self.client.post(
            '/api/signup/',
            json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json'
        )
        self.assertEqual(signup_response.status_code, 201, "Signup should be successful (201 Created).")
        self.assertTrue(User.objects.filter(username=self.username).exists(), "User should exist in the database after signup.")

        # 2. Test user login with the newly created credentials
        login_response = self.client.post(
            '/api/login/',
            json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200, "Login should be successful (200 OK).")
        self.assertIn('_auth_user_id', self.client.session, "User ID should be in the session after login.")

    def test_signup_with_existing_username(self):
        """
        Tests that signing up with a username that already exists fails.
        """
        User.objects.create_user(username=self.username, password=self.password)
        response = self.client.post(
            '/api/signup/',
            json.dumps({'username': self.username, 'password': 'another-password'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400, "Signup with existing username should fail (400 Bad Request).")
        self.assertEqual(response.json()['message'], 'Username already exists.')

    def test_login_with_nonexistent_user(self):
        """
        Tests that attempting to log in with a user that does not exist fails.
        """
        response = self.client.post(
            '/api/login/',
            json.dumps({'username': 'nonexistentuser', 'password': 'fakepassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401, "Login with nonexistent user should fail (401 Unauthorized).")
        self.assertEqual(response.json()['message'], 'Invalid credentials.')

    def test_login_with_incorrect_password(self):
        """
        Tests that logging in with a correct username but incorrect password fails.
        """
        # Create the user first
        User.objects.create_user(username=self.username, password=self.password)

        # Attempt to log in with the wrong password
        response = self.client.post(
            '/api/login/',
            json.dumps({'username': self.username, 'password': 'wrong-password'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401, "Login with incorrect password should fail (401 Unauthorized).")
        self.assertEqual(response.json()['message'], 'Invalid credentials.')


class StockQuoteTests(TestCase):
    """
    Tests for the stock quote endpoint.
    """

    def setUp(self):
        """Set up a user and log them in."""
        self.username = "testuser"
        self.password = "strong-password-123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_quote_view_unauthenticated(self):
        """
        Tests that an unauthenticated user cannot access the quote endpoint.
        """
        self.client.logout()
        response = self.client.get('/api/quote/?symbol=AAPL')
        self.assertEqual(response.status_code, 401, "Unauthenticated request should be rejected (401 Unauthorized).")

    def test_quote_view_missing_symbol(self):
        """
        Tests that a request without a symbol is rejected.
        """
        response = self.client.get('/api/quote/')
        self.assertEqual(response.status_code, 400, "Request without a symbol should fail (400 Bad Request).")

    @patch('api.views.requests.get')
    def test_quote_view_success(self, mock_get):
        """
        Tests a successful API call to the quote endpoint.
        """
        # Configure the mock to simulate a successful response from Finnhub
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'o': 150.75, 'c': 152.00}
        mock_get.return_value = mock_response

        response = self.client.get('/api/quote/?symbol=AAPL')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['open_price'], 150.75)

    @patch('api.views.requests.get')
    def test_quote_view_symbol_not_found(self, mock_get):
        """
        Tests the case where Finnhub does not recognize the symbol.
        """
        # Configure the mock to simulate Finnhub's "not found" response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'o': 0, 'c': 0}
        mock_get.return_value = mock_response

        response = self.client.get('/api/quote/?symbol=FAKESYMBOL')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json()['error'])

    @patch('api.views.requests.get')
    def test_quote_view_finnhub_api_error(self, mock_get):
        """
        Tests how the view handles a failure from the Finnhub API.
        """
        # Configure the mock to raise an exception, simulating a network error
        mock_get.side_effect = requests.exceptions.RequestException("API is down")

        response = self.client.get('/api/quote/?symbol=AAPL')
        self.assertEqual(response.status_code, 502, "Should return 502 Bad Gateway on external API failure.")
        self.assertIn('Failed to retrieve data', response.json()['error'])