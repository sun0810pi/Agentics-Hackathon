#!/usr/bin/env python3
"""
Test script cho Audit API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_process_batch():
    """Test batch processing"""
    print("🔍 Testing /process-batch endpoint...")
    
    payload = {
        "items": [
            {
                "invoice_amount": 1000000,
                "po_amount": 950000,
                "supplier": "Test Supplier 1",
                "email": "test1@example.com",
                "bank_account": "1234567890"
            },
            {
                "invoice_amount": 5000000,
                "po_amount": 5000000,
                "supplier": "Test Supplier 2",
                "email": "test2@example.com",
                "bank_account": "9876543210"
            },
            {
                "invoice_amount": 10000000,
                "po_amount": 8000000,
                "supplier": "High Risk Supplier",
                "email": "highrisk@example.com",
                "bank_account": "5555666677"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/process-batch", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_dashboard():
    """Test dashboard stats"""
    print("🔍 Testing /dashboard endpoint...")
    response = requests.get(f"{BASE_URL}/dashboard")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_transactions():
    """Test get transactions"""
    print("🔍 Testing /transactions endpoint...")
    response = requests.get(f"{BASE_URL}/transactions")
    print(f"Status: {response.status_code}")
    print(f"Total transactions: {len(response.json())}")
    
    if response.json():
        print(f"First transaction: {json.dumps(response.json()[0], indent=2)}")
    print()

def test_agents():
    """Test agent stats"""
    print("🔍 Testing /agents/stats endpoint...")
    response = requests.get(f"{BASE_URL}/agents/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 AUDIT CORE V4 API TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_process_batch()
        test_dashboard()
        test_transactions()
        test_agents()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API")
        print("Make sure the server is running: python backend/main.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
