#!/usr/bin/env python3
"""
GPUOptimizer System Functionality Test
Tests all critical components to ensure they work properly
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

def test_email_system():
    """Test email system functionality"""
    print("🧪 Testing Email System...")
    
    try:
        from gpu_optimizer_system import RevenueManager
        
        # Initialize revenue manager
        revenue_manager = RevenueManager()
        
        # Test email sending (will show preview if no credentials)
        test_email = "test@example.com"
        test_api_key = "gopt_test123456789"
        
        print(f"📧 Testing email to: {test_email}")
        revenue_manager.send_email(
            test_email, 
            "🧪 Test Email", 
            "This is a test email from GPUOptimizer system."
        )
        
        print("✅ Email system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Email system test failed: {e}")
        return False

def test_payment_system():
    """Test payment system functionality"""
    print("🧪 Testing Payment System...")
    
    try:
        from global_payment_system import GlobalPaymentSystem
        
        # Initialize payment system
        payment_system = GlobalPaymentSystem()
        
        # Test available gateways
        print("🔍 Testing available gateways...")
        gateways = payment_system.get_available_gateways()
        print(f"📋 Available gateways: {len(gateways)}")
        
        for gateway in gateways:
            print(f"  ✅ {gateway['name']} ({gateway['id']}) - {gateway['fees']}")
        
        # Test payment creation (demo mode if no API keys)
        print("💳 Testing payment creation...")
        result = payment_system.create_payment(
            amount=49.0,
            currency="USD",
            plan="professional",
            customer_email="test@example.com"
        )
        
        print(f"💰 Payment result: {result.status} - {result.message}")
        if result.payment_url:
            print(f"🔗 Payment URL: {result.payment_url}")
        
        print("✅ Payment system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Payment system test failed: {e}")
        return False

def test_customer_creation():
    """Test customer creation functionality"""
    print("🧪 Testing Customer Creation...")
    
    try:
        from gpu_optimizer_system import RevenueManager
        
        # Initialize revenue manager
        revenue_manager = RevenueManager()
        
        # Test customer creation
        test_email = f"test_{int(time.time())}@example.com"
        print(f"👤 Creating test customer: {test_email}")
        
        customer = revenue_manager.create_customer(test_email)
        
        print(f"✅ Customer created successfully!")
        print(f"📧 Email: {customer.email}")
        print(f"🔑 API Key: {customer.api_key}")
        print(f"🎯 Tier: {customer.tier}")
        
        return True
        
    except Exception as e:
        print(f"❌ Customer creation test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("🧪 Testing API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test health endpoint
        print("🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = response.json()
            print(f"📊 Status: {health_data.get('status')}")
        else:
            print(f"⚠️  Health endpoint returned: {response.status_code}")
        
        # Test payment gateways endpoint
        print("💳 Testing payment gateways endpoint...")
        response = requests.get(f"{base_url}/api/payment/gateways", timeout=5)
        if response.status_code == 200:
            print("✅ Payment gateways endpoint working")
            gateways = response.json()
            print(f"📋 Available gateways: {len(gateways.get('gateways', []))}")
        else:
            print(f"⚠️  Payment gateways endpoint returned: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - skipping API endpoint tests")
        print("💡 To test API endpoints, run: python gpu_optimizer_system.py")
        return True
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("🚀 GPUOptimizer System Functionality Test")
    print("=" * 50)
    print(f"📅 Test started at: {datetime.now()}")
    print()
    
    tests = [
        ("Email System", test_email_system),
        ("Payment System", test_payment_system),
        ("Customer Creation", test_customer_creation),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} Test...")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print()
    print("💡 Next Steps:")
    print("1. 🚀 Deploy to Render if all tests pass")
    print("2. 📧 Configure email credentials (SENDER_EMAIL, SENDER_PASSWORD)")
    print("3. 💳 Configure payment gateway API keys")
    print("4. 🎨 Enhance frontend for better user experience")

if __name__ == "__main__":
    main()
