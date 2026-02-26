#!/usr/bin/env python3

import requests
import sys
import os
import json
from datetime import datetime
import time

class AirbnbAPITester:
    def __init__(self):
        # Try to determine the correct API URL
        # First check if there's a frontend/.env with REACT_APP_BACKEND_URL
        frontend_env_path = "/app/frontend/.env"
        if os.path.exists(frontend_env_path):
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.strip().split('=', 1)[1].strip()
                        break
                else:
                    self.base_url = "http://localhost:8001"  # fallback
        else:
            self.base_url = "http://localhost:8001"  # fallback
            
        self.tests_run = 0
        self.tests_passed = 0
        self.booking_id = None

    def log_result(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        print()

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                details = f"Status: {data.get('status', 'unknown')}"
            else:
                details = f"Status Code: {response.status_code}"
            self.log_result("Health Check", success, details)
            return success
        except Exception as e:
            self.log_result("Health Check", False, f"Error: {str(e)}")
            return False

    def test_create_booking(self):
        """Test creating a booking with multipart form data"""
        print("🔍 Testing Booking Creation...")
        
        # Create test data
        booking_data = {
            'guest_name': 'Test User',
            'guest_phone': '+919876543210',
            'check_in': '2024-12-15',
            'check_out': '2024-12-17',
            'num_guests': '3',
            'total_price': '6000',
            'property_name': 'Siddha SkyView Studio'
        }
        
        # Create a test file (mock Aadhaar)
        test_file_content = b"Test Aadhaar Document Content"
        files = {'aadhaar_file': ('test_aadhaar.jpg', test_file_content, 'image/jpeg')}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/bookings", 
                data=booking_data,
                files=files,
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get('success') and data.get('booking'):
                    self.booking_id = data['booking']['booking_id']
                    details = f"Booking ID: {self.booking_id}, Total: ₹{data['booking']['total_price']}"
                else:
                    success = False
                    details = "Invalid response structure"
            else:
                details = f"Status Code: {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        details += f", Error: {error_data.get('detail', 'Unknown error')}"
                    except:
                        details += f", Response: {response.content[:200]}"
            
            self.log_result("Create Booking", success, details)
            return success
            
        except Exception as e:
            self.log_result("Create Booking", False, f"Error: {str(e)}")
            return False

    def test_get_all_bookings(self):
        """Test fetching all bookings"""
        print("🔍 Testing Get All Bookings...")
        try:
            response = requests.get(f"{self.base_url}/api/bookings", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                bookings = data.get('bookings', [])
                details = f"Found {len(bookings)} bookings"
                if self.booking_id and bookings:
                    # Check if our created booking is in the list
                    found_booking = any(b.get('booking_id') == self.booking_id for b in bookings)
                    details += f", Created booking found: {found_booking}"
            else:
                details = f"Status Code: {response.status_code}"
            
            self.log_result("Get All Bookings", success, details)
            return success
            
        except Exception as e:
            self.log_result("Get All Bookings", False, f"Error: {str(e)}")
            return False

    def test_get_single_booking(self):
        """Test fetching a single booking by ID"""
        if not self.booking_id:
            self.log_result("Get Single Booking", False, "No booking ID available from previous test")
            return False
            
        print("🔍 Testing Get Single Booking...")
        try:
            response = requests.get(f"{self.base_url}/api/bookings/{self.booking_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Booking ID: {data.get('booking_id')}, Guest: {data.get('guest_name')}"
            else:
                details = f"Status Code: {response.status_code}"
            
            self.log_result("Get Single Booking", success, details)
            return success
            
        except Exception as e:
            self.log_result("Get Single Booking", False, f"Error: {str(e)}")
            return False

    def test_file_validation(self):
        """Test file upload validation"""
        print("🔍 Testing File Upload Validation...")
        
        # Test invalid file type
        booking_data = {
            'guest_name': 'Test User',
            'guest_phone': '+919876543210',
            'check_in': '2024-12-20',
            'check_out': '2024-12-22',
            'num_guests': '2',
            'total_price': '5000',
            'property_name': 'Siddha SkyView Studio'
        }
        
        # Test with invalid file extension
        invalid_file = {'aadhaar_file': ('test.txt', b"Invalid file content", 'text/plain')}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/bookings",
                data=booking_data,
                files=invalid_file,
                timeout=10
            )
            
            # Should fail with 400 status code
            success = response.status_code == 400
            if success:
                data = response.json()
                details = f"Correctly rejected invalid file: {data.get('detail', 'Unknown error')}"
            else:
                success = False
                details = f"Did not reject invalid file. Status: {response.status_code}"
            
            self.log_result("File Upload Validation", success, details)
            return success
            
        except Exception as e:
            self.log_result("File Upload Validation", False, f"Error: {str(e)}")
            return False

    def test_guest_count_validation(self):
        """Test guest count validation (1-4 guests)"""
        print("🔍 Testing Guest Count Validation...")
        
        booking_data = {
            'guest_name': 'Test User',
            'guest_phone': '+919876543210', 
            'check_in': '2024-12-25',
            'check_out': '2024-12-27',
            'num_guests': '5',  # Invalid: more than 4
            'total_price': '7500',
            'property_name': 'Siddha SkyView Studio'
        }
        
        valid_file = {'aadhaar_file': ('test.jpg', b"Test content", 'image/jpeg')}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/bookings",
                data=booking_data,
                files=valid_file,
                timeout=10
            )
            
            # Should fail with 400 status code
            success = response.status_code == 400
            if success:
                data = response.json()
                details = f"Correctly rejected invalid guest count: {data.get('detail', 'Unknown error')}"
            else:
                details = f"Did not reject invalid guest count. Status: {response.status_code}"
            
            self.log_result("Guest Count Validation", success, details)
            return success
            
        except Exception as e:
            self.log_result("Guest Count Validation", False, f"Error: {str(e)}")
            return False

    def test_aadhaar_file_endpoint(self):
        """Test the Aadhaar file download endpoint"""
        if not self.booking_id:
            self.log_result("Aadhaar File Download", False, "No booking with file available")
            return False
            
        print("🔍 Testing Aadhaar File Download...")
        
        # First get the booking to get the filename
        try:
            booking_response = requests.get(f"{self.base_url}/api/bookings/{self.booking_id}", timeout=10)
            if booking_response.status_code != 200:
                self.log_result("Aadhaar File Download", False, "Could not get booking details")
                return False
                
            booking_data = booking_response.json()
            filename = booking_data.get('aadhaar_filename')
            
            if not filename:
                self.log_result("Aadhaar File Download", False, "No Aadhaar filename in booking")
                return False
            
            # Test file download
            file_response = requests.get(f"{self.base_url}/api/aadhaar/{filename}", timeout=10)
            success = file_response.status_code == 200
            
            if success:
                details = f"File downloaded successfully, Size: {len(file_response.content)} bytes"
            else:
                details = f"Status Code: {file_response.status_code}"
            
            self.log_result("Aadhaar File Download", success, details)
            return success
            
        except Exception as e:
            self.log_result("Aadhaar File Download", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("🚀 Starting Airbnb Booking API Tests")
        print(f"🎯 Base URL: {self.base_url}")
        print("=" * 60)
        print()
        
        # Test order matters - some tests depend on others
        test_results = [
            self.test_health_endpoint(),
            self.test_create_booking(),
            self.test_get_all_bookings(), 
            self.test_get_single_booking(),
            self.test_aadhaar_file_endpoint(),
            self.test_file_validation(),
            self.test_guest_count_validation()
        ]
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"✨ Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print("=" * 60)
        
        return all(test_results)

def main():
    tester = AirbnbAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())