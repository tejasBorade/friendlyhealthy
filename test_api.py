import requests
import json

# Login
login_data = {
    "email": "patient@test.com",
    "password": "Test@123"
}

try:
    print("Testing login...")
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json=login_data
    )
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text}\n")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        
        if token:
            print(f"Token: {token[:50]}...\n")
            
            # Test appointments endpoint
            print("Testing appointments...")
            headers = {"Authorization": f"Bearer {token}"}
            appts_response = requests.get(
                "http://localhost:8000/api/v1/appointments",
                headers=headers
            )
            print(f"Appointments status: {appts_response.status_code}")
            print(f"Appointments response: {appts_response.text}\n")
            print(f"Response headers: {dict(appts_response.headers)}")
        else:
            print("No token in response")
    else:
        print(f"Login failed with status {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
