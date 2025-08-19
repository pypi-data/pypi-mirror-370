"""
Unit tests for the KRA client functionality.
"""

import unittest
from unittest.mock import patch, Mock
from gava_connect import KRAGavaConnect, TaxObligationType, KRAMethodsProvider


class TestTaxObligationType(unittest.TestCase):
    """Test cases for TaxObligationType enum."""
    
    def test_get_obligation_type_valid_code(self):
        """Test getting obligation type with valid code."""
        result = TaxObligationType.get_obligation_type("9")
        self.assertEqual(result, "Value Added Tax (VAT)")
    
    def test_get_obligation_type_invalid_code(self):
        """Test getting obligation type with invalid code."""
        result = TaxObligationType.get_obligation_type("999")
        self.assertEqual(result, "Unknown Tax Obligation Type")
    
    def test_get_obligation_code_valid_description(self):
        """Test getting obligation code with valid description."""
        result = TaxObligationType.get_obligation_code("Value Added Tax (VAT)")
        self.assertEqual(result, "9")
    
    def test_get_obligation_code_invalid_description(self):
        """Test getting obligation code with invalid description."""
        result = TaxObligationType.get_obligation_code("Invalid Description")
        self.assertEqual(result, "Unknown Tax Obligation Code")


class TestKRAMethodsProvider(unittest.TestCase):
    """Test cases for KRAMethodsProvider."""
    
    def test_init_sandbox_environment(self):
        """Test initialization with sandbox environment."""
        provider = KRAMethodsProvider("sandbox")
        self.assertEqual(provider.base_url, "https://sbx.kra.go.ke")
        self.assertEqual(provider.environment, "sandbox")
    
    def test_init_production_environment(self):
        """Test initialization with production environment."""
        provider = KRAMethodsProvider("production")
        self.assertEqual(provider.base_url, "https://api.kra.go.ke")
        self.assertEqual(provider.environment, "production")
    
    def test_init_invalid_environment(self):
        """Test initialization with invalid environment."""
        with self.assertRaises(ValueError):
            KRAMethodsProvider("invalid")
    
    def test_check_pin_url_pin(self):
        """Test PIN check URL generation for PIN-based check."""
        provider = KRAMethodsProvider("sandbox")
        url = provider.check_pin_url("pin")
        self.assertEqual(url, "https://sbx.kra.go.ke/checker/v1/pinbypin")
    
    def test_check_pin_url_id(self):
        """Test PIN check URL generation for ID-based check."""
        provider = KRAMethodsProvider("sandbox")
        url = provider.check_pin_url("id")
        self.assertEqual(url, "https://sbx.kra.go.ke/checker/v1/pin")
    
    def test_get_token_url(self):
        """Test token URL generation."""
        provider = KRAMethodsProvider("sandbox")
        url = provider.get_token_url()
        self.assertEqual(url, "https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials")


class TestKRAGavaConnect(unittest.TestCase):
    """Test cases for KRAGavaConnect."""
    
    @patch('gava_connect.kra_client.requests.get')
    def test_authentication_success(self, mock_get):
        """Test successful authentication."""
        # Mock successful authentication response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_get.return_value = mock_response
        
        client = KRAGavaConnect("test_key", "test_secret", "sandbox")
        self.assertEqual(client.access_token, "test_token")
        self.assertIn("Bearer test_token", client.headers["Authorization"])
    
    @patch('gava_connect.kra_client.requests.get')
    def test_authentication_failure(self, mock_get):
        """Test authentication failure."""
        # Mock failed authentication response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception):
            KRAGavaConnect("test_key", "test_secret", "sandbox")
    
    def test_init_missing_credentials(self):
        """Test initialization with missing credentials."""
        with self.assertRaises(ValueError):
            KRAGavaConnect("", "test_secret", "sandbox")
        
        with self.assertRaises(ValueError):
            KRAGavaConnect("test_key", "", "sandbox")
    
    @patch('gava_connect.kra_client.requests.post')
    @patch('gava_connect.kra_client.requests.get')
    def test_check_pin_kra_pin(self, mock_get, mock_post):
        """Test KRA PIN check."""
        # Mock authentication
        mock_auth_response = Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_get.return_value = mock_auth_response
        
        # Mock PIN check response
        mock_pin_response = Mock()
        mock_pin_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_pin_response
        
        client = KRAGavaConnect("test_key", "test_secret", "sandbox")
        result = client.check_pin_kra_pin("A123456789")
        
        self.assertEqual(result, {"status": "success"})
        mock_post.assert_called_once()
    
    @patch('gava_connect.kra_client.requests.post')
    @patch('gava_connect.kra_client.requests.get')
    def test_check_pin_by_id(self, mock_get, mock_post):
        """Test ID-based PIN check."""
        # Mock authentication
        mock_auth_response = Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_get.return_value = mock_auth_response
        
        # Mock ID check response
        mock_id_response = Mock()
        mock_id_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_id_response
        
        client = KRAGavaConnect("test_key", "test_secret", "sandbox")
        result = client.check_pin_by_id("12345678")
        
        self.assertEqual(result, {"status": "success"})
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
