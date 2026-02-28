import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (from seeded data)
TEST_CREDENTIALS = {
    "patient": {
        "email": "patient@test.com",
        "password": "Test@123"
    },
    "doctor": {
        "email": "sarah.johnson@healthcare.com",
        "password": "Doctor@123"
    },
    "admin": {
        "email": "admin@healthcare.com",
        "password": "Admin@123"
    }
}

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.user_role = None
        self.results = {
            "passed": [],
            "failed": [],
            "skipped": []
        }
    
    def login(self, role="patient"):
        """Login and get access token"""
        print(f"\n{'='*60}")
        print(f"  [AUTH] LOGGING IN AS {role.upper()}")
        print(f"{'='*60}\n")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=TEST_CREDENTIALS[role]
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.user_role = role
                print(f"[PASS] Login successful")
                print(f"   User ID: {self.user_id}")
                print(f"   Token: {self.token[:30]}...")
                self.results["passed"].append(f"Login as {role}")
                return True
            else:
                print(f"[FAIL] Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.results["failed"].append(f"Login as {role}")
                return False
        except Exception as e:
            print(f"[ERROR] Login error: {str(e)}")
            self.results["failed"].append(f"Login as {role}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_endpoint(self, method, endpoint, name, data=None, expected_status=200):
        """Test a single endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=self.get_headers())
            elif method == "POST":
                response = requests.post(url, headers=self.get_headers(), json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.get_headers(), json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.get_headers())
            
            if response.status_code == expected_status:
                result_data = response.json() if response.content else {}
                count = len(result_data) if isinstance(result_data, list) else (
                    len(result_data.get('data', [])) if isinstance(result_data.get('data'), list) else 'N/A'
                )
                print(f"  ✅ {name}: {response.status_code} (Records: {count})")
                self.results["passed"].append(name)
                return True, result_data
            else:
                print(f"  ❌ {name}: {response.status_code} (Expected: {expected_status})")
                print(f"     Response: {response.text[:200]}")
                self.results["failed"].append(name)
                return False, None
        except Exception as e:
            print(f"  ❌ {name}: Error - {str(e)}")
            self.results["failed"].append(name)
            return False, None
    
    def test_all_endpoints(self):
        """Test all API endpoints"""
        
        # 1. APPOINTMENTS
        print(f"\n{'='*60}")
        print("  📅 TESTING APPOINTMENTS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/appointments", "GET /appointments")
        self.test_endpoint("GET", "/appointments/upcoming", "GET /appointments/upcoming")
        success, appointments = self.test_endpoint("GET", "/appointments", "GET /appointments (for detail test)")
        if success and appointments:
            apt_id = appointments[0]['id'] if isinstance(appointments, list) else (
                appointments.get('data', [{}])[0].get('id')
            )
            if apt_id:
                self.test_endpoint("GET", f"/appointments/{apt_id}", f"GET /appointments/{apt_id}")
        
        # 2. PRESCRIPTIONS
        print(f"\n{'='*60}")
        print("  💊 TESTING PRESCRIPTIONS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/prescriptions", "GET /prescriptions")
        self.test_endpoint("GET", "/prescriptions/active", "GET /prescriptions/active")
        success, prescriptions = self.test_endpoint("GET", "/prescriptions", "GET /prescriptions (for detail test)")
        if success and prescriptions:
            presc_id = prescriptions[0]['id'] if isinstance(prescriptions, list) else (
                prescriptions.get('data', [{}])[0].get('id')
            )
            if presc_id:
                self.test_endpoint("GET", f"/prescriptions/{presc_id}", f"GET /prescriptions/{presc_id}")
        
        # 3. MEDICAL RECORDS
        print(f"\n{'='*60}")
        print("  📋 TESTING MEDICAL RECORDS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/medical-history", "GET /medical-history")
        
        # 4. REPORTS
        print(f"\n{'='*60}")
        print("  📊 TESTING REPORTS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/reports", "GET /reports")
        success, reports = self.test_endpoint("GET", "/reports", "GET /reports (for detail test)")
        if success and reports:
            report_id = reports[0]['id'] if isinstance(reports, list) else (
                reports.get('data', [{}])[0].get('id')
            )
            if report_id:
                self.test_endpoint("GET", f"/reports/{report_id}", f"GET /reports/{report_id}")
        
        # 5. DOCTORS
        print(f"\n{'='*60}")
        print("  👨‍⚕️ TESTING DOCTORS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/doctors", "GET /doctors")
        self.test_endpoint("GET", "/doctors/specializations", "GET /doctors/specializations")
        success, doctors = self.test_endpoint("GET", "/doctors", "GET /doctors (for detail test)")
        if success and doctors:
            doctor_id = doctors[0]['id'] if isinstance(doctors, list) else (
                doctors.get('data', [{}])[0].get('id')
            )
            if doctor_id:
                self.test_endpoint("GET", f"/doctors/{doctor_id}", f"GET /doctors/{doctor_id}")
        
        # 6. DIGITAL SIGNATURES
        print(f"\n{'='*60}")
        print("  ✍️ TESTING DIGITAL SIGNATURES")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/signatures", "GET /signatures")
        
        # 7. NOTIFICATIONS
        print(f"\n{'='*60}")
        print("  🔔 TESTING NOTIFICATIONS")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/notifications", "GET /notifications")
        self.test_endpoint("GET", "/notifications/unread-count", "GET /notifications/unread-count")
        self.test_endpoint("GET", "/notification-preferences", "GET /notification-preferences")
        
        # 8. PATIENTS (if doctor/admin)
        if self.user_role in ["doctor", "admin"]:
            print(f"\n{'='*60}")
            print("  👥 TESTING PATIENTS")
            print(f"{'='*60}\n")
            
            self.test_endpoint("GET", "/patients", "GET /patients")
        
        # 9. TEMPLATES (Sprint 1.2)
        print(f"\n{'='*60}")
        print("  📝 TESTING TEMPLATES (Sprint 1.2)")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/templates", "GET /templates", expected_status=[200, 404])
        
        # 10. FAVORITES (Sprint 1.2)
        print(f"\n{'='*60}")
        print("  ⭐ TESTING FAVORITES (Sprint 1.2)")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/favorites", "GET /favorites", expected_status=[200, 404])
        
        # 11. TEST ORDERS (Sprint 1.4)
        print(f"\n{'='*60}")
        print("  🧪 TESTING TEST ORDERS (Sprint 1.4)")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/tests", "GET /tests", expected_status=[200, 404])
        
        # 12. REMINDERS (Sprint 2.1)
        print(f"\n{'='*60}")
        print("  ⏰ TESTING REMINDERS (Sprint 2.1)")
        print(f"{'='*60}\n")
        
        self.test_endpoint("GET", "/reminders", "GET /reminders", expected_status=[200, 404])
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["skipped"])
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        skipped = len(self.results["skipped"])
        
        print("\n" + "="*60)
        print("  📊 TEST SUMMARY")
        print("="*60 + "\n")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Passed: {passed} ({passed*100//total if total > 0 else 0}%)")
        print(f"  ❌ Failed: {failed} ({failed*100//total if total > 0 else 0}%)")
        print(f"  ⏭️  Skipped: {skipped}")
        print("\n" + "="*60 + "\n")
        
        if self.results["failed"]:
            print("\n❌ Failed Tests:")
            for test in self.results["failed"]:
                print(f"   - {test}")
        
        if self.results["skipped"]:
            print("\n⏭️  Skipped Tests:")
            for test in self.results["skipped"]:
                print(f"   - {test}")

def main():
    print("\n" + "="*60)
    print("  FRIENDLYHEALTHY API TEST SUITE")
    print("="*60)
    
    # Test as PATIENT
    tester = APITester()
    if tester.login("patient"):
        tester.test_all_endpoints()
    
    # Print final summary
    tester.print_summary()

if __name__ == "__main__":
    main()
