import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test credentials
TEST_CREDENTIALS = {
    "email": "patient@test.com",
    "password": "Test@123"
}

def test_login():
    """Test login"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        return None

def test_endpoint(token, method, endpoint, name):
    """Test a single endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result_data = response.json()
            # Handle wrapped responses
            if isinstance(result_data, dict):
                if "appointments" in result_data:
                    count = len(result_data["appointments"])
                elif "doctors" in result_data:
                    count = len(result_data["doctors"])
                elif "prescriptions" in result_data:
                    count = len(result_data["prescriptions"])
                else:
                    count = 'N/A'
            elif isinstance(result_data, list):
                count = len(result_data)
            else:
                count = 'N/A'
            print(f"✅ {name}: {response.status_code} | Records: {count}")
            return True
        else:
            print(f"❌ {name}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("  FRIENDLYHEALTHY API TEST - FINAL RESULTS")
    print("="*60)
    
    # Login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Test core endpoints
    passed = 0
    failed = 0
    
    tests = [
        ("GET", "/appointments", "GET /appointments"),
        ("GET", "/appointments/upcoming", "GET /appointments/upcoming"),
        ("GET", "/prescriptions", "GET /prescriptions"),
        ("GET", "/prescriptions/active", "GET /prescriptions/active"),
        ("GET", "/medical-history", "GET /medical-history"),
        ("GET", "/reports", "GET /reports"),
        ("GET", "/doctors", "GET /doctors"),
        ("GET", "/doctors/specializations", "GET /doctors/specializations"),
        ("GET", "/notifications", "GET /notifications"),
        ("GET", "/notifications/unread-count", "GET /notifications/unread-count"),
    ]
    
    print("\n" + "="*60)
    print("  TESTING CORE APIs")
    print("="*60 + "\n")
    
    for method, endpoint, name in tests:
        if test_endpoint(token, method, endpoint, name):
            passed += 1
        else:
            failed += 1
    
    # Summary
    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*60)
    print("  FINAL SUMMARY")
    print("="*60)
    print(f"  Total Tests: {total}")
    print(f"  ✅ Passed: {passed} ({percentage:.1f}%)")
    print(f"  ❌ Failed: {failed} ({100-percentage:.1f}%)")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
