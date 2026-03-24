"""
Test suite for Xanadu Stays Guest ID Vault API
Tests backend health, vault config, vault status, vault auth, and bookings endpoints
"""
import pytest
import requests
import os

# Use localhost for testing as per agent instructions
BASE_URL = "http://localhost:8001"


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_returns_200(self):
        """GET /api/health should return 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"Health check passed: {data}")


class TestVaultConfigEndpoint:
    """Vault config endpoint tests - returns Supabase public config"""
    
    def test_vault_config_returns_200(self):
        """GET /api/vault/config should return 200"""
        response = requests.get(f"{BASE_URL}/api/vault/config")
        assert response.status_code == 200
        data = response.json()
        assert "supabase_url" in data
        assert "supabase_anon_key" in data
        print(f"Vault config response: {data}")
    
    def test_vault_config_returns_empty_strings_when_not_configured(self):
        """Config should return empty strings when Supabase is not configured"""
        response = requests.get(f"{BASE_URL}/api/vault/config")
        assert response.status_code == 200
        data = response.json()
        # Since Supabase is not configured, these should be empty strings
        assert data["supabase_url"] == ""
        assert data["supabase_anon_key"] == ""
        print("Vault config correctly returns empty strings for unconfigured Supabase")


class TestVaultStatusEndpoint:
    """Vault status endpoint tests - returns configuration status"""
    
    def test_vault_status_returns_200(self):
        """GET /api/vault/status should return 200"""
        response = requests.get(f"{BASE_URL}/api/vault/status")
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        assert "supabase_configured" in data
        assert "r2_configured" in data
        print(f"Vault status response: {data}")
    
    def test_vault_status_shows_unconfigured(self):
        """Status should show configured:false when credentials are not set"""
        response = requests.get(f"{BASE_URL}/api/vault/status")
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] == False
        assert data["supabase_configured"] == False
        assert data["r2_configured"] == False
        assert data["retention_years"] == 7
        assert data["storage_bucket"] == "guest-id-documents"
        print("Vault status correctly shows unconfigured state")


class TestVaultAuthEndpoint:
    """Vault authentication tests - protected endpoints require auth"""
    
    def test_vault_guests_without_auth_returns_401(self):
        """GET /api/vault/guests without auth header should return 401"""
        response = requests.get(f"{BASE_URL}/api/vault/guests")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "Unauthorized" in data["error"]
        print(f"Correctly returned 401 without auth: {data}")
    
    def test_vault_guests_with_fake_auth_returns_401(self):
        """GET /api/vault/guests with fake auth header should return 401"""
        headers = {"Authorization": "Bearer fake_token_12345"}
        response = requests.get(f"{BASE_URL}/api/vault/guests", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "Unauthorized" in data["error"]
        print(f"Correctly returned 401 with fake auth: {data}")
    
    def test_vault_guests_with_invalid_auth_format_returns_401(self):
        """GET /api/vault/guests with invalid auth format should return 401"""
        headers = {"Authorization": "InvalidFormat token"}
        response = requests.get(f"{BASE_URL}/api/vault/guests", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        print(f"Correctly returned 401 with invalid auth format: {data}")


class TestBookingsEndpoint:
    """Bookings endpoint tests - legacy FastAPI endpoints"""
    
    def test_get_bookings_returns_200(self):
        """GET /api/bookings should return 200 with list of bookings"""
        response = requests.get(f"{BASE_URL}/api/bookings")
        assert response.status_code == 200
        data = response.json()
        assert "bookings" in data
        assert isinstance(data["bookings"], list)
        print(f"Bookings endpoint returned {len(data['bookings'])} bookings")
    
    def test_bookings_have_required_fields(self):
        """Bookings should have required fields"""
        response = requests.get(f"{BASE_URL}/api/bookings")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["bookings"]) > 0:
            booking = data["bookings"][0]
            required_fields = ["booking_id", "guest_name", "guest_phone", 
                            "check_in", "check_out", "num_guests", 
                            "total_price", "property_name", "status"]
            for field in required_fields:
                assert field in booking, f"Missing field: {field}"
            print(f"Booking has all required fields: {list(booking.keys())}")
        else:
            print("No bookings to validate fields")


class TestVaultProxyEndpoints:
    """Test that vault proxy correctly forwards requests to dev server"""
    
    def test_vault_properties_without_auth_returns_401(self):
        """GET /api/vault/properties without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/vault/properties")
        assert response.status_code == 401
        print("Vault properties endpoint correctly requires auth")
    
    def test_vault_retention_review_without_auth_returns_401(self):
        """GET /api/vault/retention-review without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/vault/retention-review")
        assert response.status_code == 401
        print("Vault retention-review endpoint correctly requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
