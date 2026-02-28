import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "patient@test.com", "password": "Test@123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    
    # Try to get appointments
    response = requests.get(
        "http://localhost:8000/api/v1/appointments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
else:
    print(f"Login failed: {login_response.text}")
