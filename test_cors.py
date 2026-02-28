import requests

print("Testing CORS headers...")

# Login to get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "patient@test.com", "password": "Test@123"}
)
token = login_response.json()["access_token"]

# Test with Origin header (simulating browser request)
headers = {
    "Authorization": f"Bearer {token}",
    "Origin": "http://localhost:3000"
}

response = requests.get(
    "http://localhost:8000/api/v1/appointments",
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"\nAll Response Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\n\nLooking for CORS headers:")
cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
if cors_headers:
    for key, value in cors_headers.items():
        print(f"  ✓ {key}: {value}")
else:
    print("  ✗ NO CORS HEADERS FOUND!")
