#!/usr/bin/env python
"""
Test script for the St-James-st Parking API
Run this after starting the server to test all endpoints
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "email": "testuser@example.com",
    "password": "testpass123",
    "name": "Test User",
    "address": "123 Test St, Test City, TC 12345"
}

def print_response(title, response, status_code=None):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)
    return response.status_code == 200

def test_signup():
    """Test user signup"""
    response = requests.post(
        f"{BASE_URL}/api/auth/signup",
        json=TEST_USER
    )
    print_response("SIGNUP", response)
    return response.json() if response.status_code == 201 else None

def test_login():
    """Test user login"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    print_response("LOGIN", response)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_list_spots(token):
    """Test listing parking spots"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/spots",
        headers=headers
    )
    print_response("LIST SPOTS", response)
    return response.status_code == 200

def test_list_spots_with_bbox(token):
    """Test listing parking spots with bounding box"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/spots?bbox=-74.01,40.71,-74.00,40.72",
        headers=headers
    )
    print_response("LIST SPOTS (WITH BBOX)", response)
    return response.status_code == 200

def test_request_verification(token):
    """Test verification request"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/verification/request",
        json={"method": "invite"},
        headers=headers
    )
    print_response("REQUEST VERIFICATION", response)
    return response.status_code == 200

def test_redeem_invite(token):
    """Test redeeming invite code"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/verification/redeem-invite",
        json={"code": "TEST-INVITE-123"},
        headers=headers
    )
    print_response("REDEEM INVITE", response)
    return response.status_code == 200

def test_create_reservation(token, spot_id):
    """Test creating a reservation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    now = datetime.utcnow()
    start_time = now + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    response = requests.post(
        f"{BASE_URL}/api/reservations",
        json={
            "spot_id": spot_id,
            "vehicle_id": "TEST-123",
            "start_at": start_time.isoformat() + "Z",
            "end_at": end_time.isoformat() + "Z"
        },
        headers=headers
    )
    print_response("CREATE RESERVATION", response)
    return response.status_code == 201

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  St-James-st Parking API - Test Suite")
    print("="*60)
    
    # Test health
    if not test_health():
        print("ERROR: Health check failed!")
        return
    
    # Test signup
    user = test_signup()
    if not user:
        print("ERROR: Signup failed!")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("ERROR: Login failed!")
        return
    
    print(f"\n✓ Got access token: {token[:20]}...")
    
    # Test listing spots
    test_list_spots(token)
    test_list_spots_with_bbox(token)
    
    # Get first spot for reservation test
    response = requests.get(f"{BASE_URL}/api/spots")
    if response.status_code == 200:
        spots = response.json().get("features", [])
        if spots:
            spot_id = spots[0]["properties"]["id"]
            
            # Test verification flow
            test_request_verification(token)
            test_redeem_invite(token)
            
            # Test creating reservation
            test_create_reservation(token, spot_id)
    
    print("\n" + "="*60)
    print("  Test Suite Complete!")
    print("="*60)

if __name__ == "__main__":
    main()
