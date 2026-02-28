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
    print("\n" + "="*60)
    print("  TESTING LOGIN")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_CREDENTIALS
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[PASS] Login successful")
        print(f"  User ID: {data.get('user_id')}")
        return data.get("access_token")
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
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
            count = len(result_data) if isinstance(result_data, list) else (
                len(result_data.get('data', [])) if isinstance(result_data.get('data'), list) else 'N/A'
            )
            print(f"[PASS] {name}: {response.status_code} | Records: {count}")
            return True
        else:
            print(f"[FAIL] {name}: {response.status_code}")
            if response.text:
                print(f"      Response: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("  FRIENDLYHEALTHY API TEST SUITE")
    print("="*60)
    
    # Login
    token = test_login()
    if not token:
        print("\n[FAIL] Cannot proceed without authentication")
        return
    
    # Test endpoints
    passed = 0
    failed = 0
    
    print("\n" + "="*60)
    print("  TESTING APPOINTMENTS")
    print("="*60)
    if test_endpoint(token, "GET", "/appointments", "GET /appointments"):
        passed += 1
    else:
        failed += 1
    
    if test_endpoint(token, "GET", "/appointments/upcoming", "GET /appointments/upcoming"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING PRESCRIPTIONS")
    print("="*60)
    if test_endpoint(token, "GET", "/prescriptions", "GET /prescriptions"):
        passed += 1
    else:
        failed += 1
    
    if test_endpoint(token, "GET", "/prescriptions/active", "GET /prescriptions/active"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING MEDICAL RECORDS")
    print("="*60)
    if test_endpoint(token, "GET", "/medical-history", "GET /medical-history"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING REPORTS")
    print("="*60)
    if test_endpoint(token, "GET", "/reports", "GET /reports"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING DOCTORS")
    print("="*60)
    if test_endpoint(token, "GET", "/doctors", "GET /doctors"):
        passed += 1
    else:
        failed += 1
    
    if test_endpoint(token, "GET", "/doctors/specializations", "GET /doctors/specializations"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING DIGITAL SIGNATURES")
    print("="*60)
    if test_endpoint(token, "GET", "/signatures", "GET /signatures"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING NOTIFICATIONS")
    print("="*60)
    if test_endpoint(token, "GET", "/notifications", "GET /notifications"):
        passed += 1
    else:
        failed += 1
    
    if test_endpoint(token, "GET", "/notifications/unread-count", "GET /notifications/unread-count"):
        passed += 1
    else:
        failed += 1
    
    if test_endpoint(token, "GET", "/notification-preferences", "GET /notification-preferences"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING TEMPLATES (Sprint 1.2)")
    print("="*60)
    if test_endpoint(token, "GET", "/templates", "GET /templates"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING FAVORITES (Sprint 1.2)")
    print("="*60)
    if test_endpoint(token, "GET", "/favorites", "GET /favorites"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING TEST ORDERS (Sprint 1.4)")
    print("="*60)
    if test_endpoint(token, "GET", "/tests", "GET /tests"):
        passed += 1
    else:
        failed += 1
    
    print("\n" + "="*60)
    print("  TESTING REMINDERS (Sprint 2.1)")
    print("="*60)
    if test_endpoint(token, "GET", "/reminders", "GET /reminders"):
        passed += 1
    else:
        failed += 1
    
    # Summary
    total = passed + failed
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"  Total Tests: {total}")
    print(f"  [PASS] Passed: {passed} ({passed*100//total if total > 0 else 0}%)")
    print(f"  [FAIL] Failed: {failed} ({failed*100//total if total > 0 else 0}%)")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
