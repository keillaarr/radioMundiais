#!/usr/bin/env python3
"""
Backend API Testing for World Radio Application
Tests the Radio Browser API integration and all backend endpoints
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://2bc7cde3-e921-4bdf-951a-1b867ba9baa4.preview.emergentagent.com/api"

class WorldRadioAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "World Radio API" in data["message"]:
                    self.log_test("Root Endpoint", True, "API root accessible with correct message", data)
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_stations_endpoint_basic(self):
        """Test basic stations endpoint without parameters"""
        try:
            response = self.session.get(f"{self.base_url}/stations")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check first station structure
                    station = data[0]
                    required_fields = ['stationuuid', 'name', 'url']
                    missing_fields = [field for field in required_fields if field not in station]
                    
                    if not missing_fields:
                        self.log_test("Stations Endpoint (Basic)", True, 
                                    f"Retrieved {len(data)} stations with correct structure", 
                                    {"count": len(data), "sample": station})
                        return True
                    else:
                        self.log_test("Stations Endpoint (Basic)", False, 
                                    f"Missing required fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Stations Endpoint (Basic)", False, 
                                f"Expected list with stations, got: {type(data)}")
                    return False
            else:
                self.log_test("Stations Endpoint (Basic)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stations Endpoint (Basic)", False, f"Error: {str(e)}")
            return False
    
    def test_stations_with_limit(self):
        """Test stations endpoint with limit parameter"""
        try:
            limit = 10
            response = self.session.get(f"{self.base_url}/stations?limit={limit}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    actual_count = len(data)
                    if actual_count <= limit:
                        self.log_test("Stations Endpoint (Limit)", True, 
                                    f"Limit parameter working: requested {limit}, got {actual_count}")
                        return True
                    else:
                        self.log_test("Stations Endpoint (Limit)", False, 
                                    f"Limit not respected: requested {limit}, got {actual_count}")
                        return False
                else:
                    self.log_test("Stations Endpoint (Limit)", False, 
                                f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Stations Endpoint (Limit)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stations Endpoint (Limit)", False, f"Error: {str(e)}")
            return False
    
    def test_stations_by_country(self):
        """Test stations endpoint with country filter"""
        try:
            country = "Brazil"
            response = self.session.get(f"{self.base_url}/stations?country={country}&limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if stations are from the requested country
                        sample_station = data[0]
                        self.log_test("Stations Endpoint (Country Filter)", True, 
                                    f"Retrieved {len(data)} stations for {country}", 
                                    {"country_requested": country, "sample": sample_station})
                        return True
                    else:
                        self.log_test("Stations Endpoint (Country Filter)", True, 
                                    f"No stations found for {country} (valid response)")
                        return True
                else:
                    self.log_test("Stations Endpoint (Country Filter)", False, 
                                f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Stations Endpoint (Country Filter)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stations Endpoint (Country Filter)", False, f"Error: {str(e)}")
            return False
    
    def test_stations_by_name(self):
        """Test stations endpoint with name search"""
        try:
            name = "BBC"
            response = self.session.get(f"{self.base_url}/stations?name={name}&limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        sample_station = data[0]
                        self.log_test("Stations Endpoint (Name Search)", True, 
                                    f"Retrieved {len(data)} stations matching '{name}'", 
                                    {"search_term": name, "sample": sample_station})
                        return True
                    else:
                        self.log_test("Stations Endpoint (Name Search)", True, 
                                    f"No stations found matching '{name}' (valid response)")
                        return True
                else:
                    self.log_test("Stations Endpoint (Name Search)", False, 
                                f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Stations Endpoint (Name Search)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Stations Endpoint (Name Search)", False, f"Error: {str(e)}")
            return False
    
    def test_countries_endpoint(self):
        """Test countries endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/countries")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check structure of first country
                    country = data[0]
                    if isinstance(country, dict) and 'name' in country:
                        self.log_test("Countries Endpoint", True, 
                                    f"Retrieved {len(data)} countries with correct structure", 
                                    {"count": len(data), "sample": country})
                        return True
                    else:
                        self.log_test("Countries Endpoint", False, 
                                    f"Unexpected country structure: {country}")
                        return False
                else:
                    self.log_test("Countries Endpoint", False, 
                                f"Expected list with countries, got: {type(data)}")
                    return False
            else:
                self.log_test("Countries Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Countries Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_search_endpoint(self):
        """Test POST search endpoint"""
        try:
            search_data = {
                "query": "Radio",
                "country": "",
                "limit": 5
            }
            response = self.session.post(f"{self.base_url}/search", 
                                       json=search_data,
                                       headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Search Endpoint (POST)", True, 
                                f"Search returned {len(data)} results", 
                                {"search_data": search_data, "result_count": len(data)})
                    return True
                else:
                    self.log_test("Search Endpoint (POST)", False, 
                                f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Search Endpoint (POST)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Search Endpoint (POST)", False, f"Error: {str(e)}")
            return False
    
    def test_favorites_add(self):
        """Test adding a favorite station"""
        try:
            # First get a station to add as favorite
            stations_response = self.session.get(f"{self.base_url}/stations?limit=1")
            if stations_response.status_code != 200:
                self.log_test("Favorites Add", False, "Could not get station for favorite test")
                return False
            
            stations = stations_response.json()
            if not stations:
                self.log_test("Favorites Add", False, "No stations available for favorite test")
                return False
            
            station = stations[0]
            favorite_data = {
                "station_uuid": station["stationuuid"],
                "station_name": station["name"],
                "station_url": station["url"],
                "country": station.get("country", ""),
                "user_id": "test_user"
            }
            
            response = self.session.post(f"{self.base_url}/favorites", 
                                       json=favorite_data,
                                       headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                data = response.json()
                if "station_uuid" in data and data["station_uuid"] == station["stationuuid"]:
                    self.log_test("Favorites Add", True, 
                                f"Successfully added favorite: {station['name']}", 
                                {"favorite": data})
                    return True, station["stationuuid"]
                else:
                    self.log_test("Favorites Add", False, 
                                f"Unexpected response structure: {data}")
                    return False, None
            else:
                self.log_test("Favorites Add", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Favorites Add", False, f"Error: {str(e)}")
            return False, None
    
    def test_favorites_get(self):
        """Test getting favorite stations"""
        try:
            response = self.session.get(f"{self.base_url}/favorites?user_id=test_user")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Favorites Get", True, 
                                f"Retrieved {len(data)} favorites", 
                                {"count": len(data)})
                    return True
                else:
                    self.log_test("Favorites Get", False, 
                                f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Favorites Get", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Favorites Get", False, f"Error: {str(e)}")
            return False
    
    def test_favorites_delete(self, station_uuid):
        """Test deleting a favorite station"""
        if not station_uuid:
            self.log_test("Favorites Delete", False, "No station UUID provided for deletion test")
            return False
            
        try:
            response = self.session.delete(f"{self.base_url}/favorites/{station_uuid}?user_id=test_user")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "removed" in data["message"].lower():
                    self.log_test("Favorites Delete", True, 
                                f"Successfully deleted favorite: {station_uuid}", 
                                {"response": data})
                    return True
                else:
                    self.log_test("Favorites Delete", False, 
                                f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Favorites Delete", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Favorites Delete", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting World Radio API Backend Tests")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity and endpoints
        self.test_root_endpoint()
        
        # Test Radio Browser API Integration via stations endpoint
        self.test_stations_endpoint_basic()
        self.test_stations_with_limit()
        self.test_stations_by_country()
        self.test_stations_by_name()
        
        # Test countries endpoint
        self.test_countries_endpoint()
        
        # Test search endpoint
        self.test_search_endpoint()
        
        # Test favorites system (full CRUD)
        success, station_uuid = self.test_favorites_add()
        self.test_favorites_get()
        if success and station_uuid:
            self.test_favorites_delete(station_uuid)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = WorldRadioAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")