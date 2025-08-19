import unittest
from unittest.mock import patch, MagicMock
from opticedge_cloud_utils.secrets import get_secret
from google.api_core.exceptions import GoogleAPICallError

class TestGetSecret(unittest.TestCase):

    @patch("opticedge_cloud_utils.secrets.secretmanager.SecretManagerServiceClient")
    def test_get_secret_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.payload.data = b"super-secret-value"
        mock_client.access_secret_version.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = get_secret("test-project", "my-secret")
        self.assertEqual(result, "super-secret-value")
        mock_client.access_secret_version.assert_called_once_with(
            request={"name": "projects/test-project/secrets/my-secret/versions/latest"}
        )

    @patch("opticedge_cloud_utils.secrets.secretmanager.SecretManagerServiceClient")
    def test_get_secret_failure(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.access_secret_version.side_effect = GoogleAPICallError("API error")
        mock_client_cls.return_value = mock_client

        with self.assertRaises(RuntimeError) as context:
            get_secret("test-project", "my-secret")

        self.assertIn("Failed to fetch secret 'my-secret'", str(context.exception))

if __name__ == "__main__":
    unittest.main()
