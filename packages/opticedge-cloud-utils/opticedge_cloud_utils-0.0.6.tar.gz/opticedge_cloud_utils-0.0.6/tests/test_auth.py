# tests/test_auth.py
import unittest
from unittest.mock import patch, MagicMock
from opticedge_cloud_utils.auth import verify_request

class TestVerifyRequest(unittest.TestCase):

    def setUp(self):
        # Mock request object with headers
        self.mock_request = MagicMock()
        self.allowed_service_account = "service-account@example.com"
        self.allowed_audience = "https://example.com/task"

    @patch("google.oauth2.id_token.verify_oauth2_token")
    @patch("google.auth.transport.requests.Request")
    def test_valid_request(self, mock_request_adapter, mock_verify_token):
        # Mock decoded token to match allowed service account
        mock_verify_token.return_value = {"email": self.allowed_service_account}

        self.mock_request.headers = {"Authorization": "Bearer fake-token"}

        result = verify_request(
            self.mock_request,
            allowed_service_account=self.allowed_service_account,
            allowed_audience=self.allowed_audience
        )
        self.assertTrue(result)
        mock_verify_token.assert_called_once()

    @patch("google.oauth2.id_token.verify_oauth2_token")
    @patch("google.auth.transport.requests.Request")
    def test_invalid_service_account(self, mock_request_adapter, mock_verify_token):
        # Token email does not match
        mock_verify_token.return_value = {"email": "other@example.com"}

        self.mock_request.headers = {"Authorization": "Bearer fake-token"}

        result = verify_request(
            self.mock_request,
            allowed_service_account=self.allowed_service_account,
            allowed_audience=self.allowed_audience
        )
        self.assertFalse(result)

    def test_missing_authorization_header(self):
        self.mock_request.headers = {}
        result = verify_request(
            self.mock_request,
            allowed_service_account=self.allowed_service_account,
            allowed_audience=self.allowed_audience
        )
        self.assertFalse(result)

    @patch("google.oauth2.id_token.verify_oauth2_token")
    @patch("google.auth.transport.requests.Request")
    def test_invalid_token_raises_exception(self, mock_request_adapter, mock_verify_token):
        # Simulate token verification failure
        mock_verify_token.side_effect = Exception("Invalid token")

        self.mock_request.headers = {"Authorization": "Bearer fake-token"}

        result = verify_request(
            self.mock_request,
            allowed_service_account=self.allowed_service_account,
            allowed_audience=self.allowed_audience
        )
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
