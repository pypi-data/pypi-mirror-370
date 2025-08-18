import pytest
from unittest.mock import Mock, patch
from api_marketplace_client import EncarClient, AuthError


class TestEncarClient:
    def setup_method(self):
        self.client = EncarClient(api_key="test_key")

    @patch('api_marketplace_client.client.requests.Session.request')
    def test_get_brands_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"brands": []}
        mock_request.return_value = mock_response

        result = self.client.get_brands()
        assert result == {"brands": []}

    @patch('api_marketplace_client.client.requests.Session.request')
    def test_auth_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with pytest.raises(AuthError):
            self.client.get_brands()
