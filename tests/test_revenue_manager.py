"""
Unit tests for RevenueManager class
"""

import pytest
import sqlite3
from datetime import datetime
from unittest.mock import patch, Mock

from gpu_optimizer_system import RevenueManager, Customer


class TestRevenueManager:
    """Test suite for RevenueManager functionality"""
    
    def test_init_database(self, revenue_manager, db_connection):
        """Test database initialization"""
        # Check that all required tables exist
        cursor = db_connection.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'customers', 'revenue_events', 'gpu_usage_logs', 
            'payment_transactions', 'security_events', 
            'api_usage_logs', 'blocked_ips'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
    
    def test_create_customer_success(self, revenue_manager):
        """Test successful customer creation"""
        email = "test@example.com"
        customer = revenue_manager.create_customer(email)
        
        assert customer.email == email
        assert customer.tier == "free"
        assert customer.api_key.startswith("gopt_")
        assert len(customer.api_key) == 28
        assert customer.gpu_count == 0
        assert customer.monthly_savings == 0.0
    
    def test_create_customer_duplicate_email(self, revenue_manager):
        """Test creating customer with duplicate email"""
        email = "test@example.com"
        
        # Create first customer
        revenue_manager.create_customer(email)
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="Customer already exists"):
            revenue_manager.create_customer(email)
    
    def test_create_customer_invalid_email(self, revenue_manager):
        """Test creating customer with invalid email"""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@example",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                revenue_manager.create_customer(email)
    
    def test_generate_api_key_uniqueness(self, revenue_manager):
        """Test API key generation uniqueness"""
        keys = set()
        for _ in range(100):
            key = revenue_manager.generate_api_key()
            assert key not in keys, "Duplicate API key generated"
            assert key.startswith("gopt_")
            assert len(key) == 28
            keys.add(key)
    
    def test_get_customer_by_email(self, revenue_manager):
        """Test retrieving customer by email"""
        email = "test@example.com"
        original_customer = revenue_manager.create_customer(email)
        
        retrieved_customer = revenue_manager.get_customer(email)
        
        assert retrieved_customer is not None
        assert retrieved_customer.email == original_customer.email
        assert retrieved_customer.api_key == original_customer.api_key
        assert retrieved_customer.tier == original_customer.tier
    
    def test_get_customer_by_api_key(self, revenue_manager):
        """Test retrieving customer by API key"""
        email = "test@example.com"
        original_customer = revenue_manager.create_customer(email)
        
        retrieved_customer = revenue_manager.get_customer_by_api_key(original_customer.api_key)
        
        assert retrieved_customer is not None
        assert retrieved_customer.email == original_customer.email
        assert retrieved_customer.api_key == original_customer.api_key
    
    def test_get_customer_nonexistent(self, revenue_manager):
        """Test retrieving non-existent customer"""
        assert revenue_manager.get_customer("nonexistent@example.com") is None
        assert revenue_manager.get_customer_by_api_key("gopt_invalid123456789012") is None
    
    def test_track_gpu_usage_success(self, revenue_manager, sample_gpu_data):
        """Test successful GPU usage tracking"""
        # Create customer first
        customer = revenue_manager.create_customer("test@example.com")
        
        result = revenue_manager.track_gpu_usage(customer.api_key, sample_gpu_data)
        
        assert result['status'] == 'success'
        assert result['gpus_monitored'] == len(sample_gpu_data)
        assert result['tier'] == 'free'
        assert 'potential_hourly_savings' in result
        assert 'monthly_projection' in result
    
    def test_track_gpu_usage_invalid_api_key(self, revenue_manager, sample_gpu_data):
        """Test GPU usage tracking with invalid API key"""
        result = revenue_manager.track_gpu_usage("invalid_key", sample_gpu_data)
        
        assert result['error'] == 'Invalid API key'
    
    def test_track_gpu_usage_free_tier_limit(self, revenue_manager, sample_gpu_data):
        """Test GPU usage tracking exceeding free tier limit"""
        # Create customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # Create GPU data exceeding free tier limit (2 GPUs)
        large_gpu_data = sample_gpu_data * 2  # 4 GPUs total
        
        result = revenue_manager.track_gpu_usage(customer.api_key, large_gpu_data)
        
        assert 'error' in result
        assert 'Free tier limited' in result['error']
    
    def test_validate_email_security(self, revenue_manager):
        """Test email validation security features"""
        malicious_emails = [
            "test<script>@example.com",
            "test';DROP TABLE customers;--@example.com",
            "test@example.com<script>alert('xss')</script>",
            "test@example..com",
            ".test@example.com",
            "test@example.com."
        ]
        
        for email in malicious_emails:
            assert not revenue_manager.validate_email(email), f"Malicious email {email} passed validation"
    
    def test_security_logging(self, revenue_manager):
        """Test security event logging"""
        # This test verifies that security logging doesn't crash
        revenue_manager.log_security_event(
            'test_event',
            'Test security event',
            ip='127.0.0.1',
            user='test@example.com'
        )
        
        # Verify log was created (basic check)
        assert hasattr(revenue_manager, 'security_logger')
    
    def test_ip_blocking(self, revenue_manager):
        """Test IP blocking functionality"""
        test_ip = "192.168.1.100"
        
        # Initially not blocked
        assert not revenue_manager.is_ip_blocked(test_ip)
        
        # Block IP
        revenue_manager.block_ip(test_ip, "Test blocking", duration_hours=1)
        
        # Should now be blocked
        assert revenue_manager.is_ip_blocked(test_ip)
    
    def test_rate_limiting(self, revenue_manager):
        """Test rate limiting functionality"""
        identifier = "test_user"
        limit = 5
        
        # Should allow requests under limit
        for i in range(limit):
            assert revenue_manager.check_rate_limit(identifier, limit)
        
        # Should deny request over limit
        assert not revenue_manager.check_rate_limit(identifier, limit)
    
    def test_row_to_customer_conversion(self, revenue_manager):
        """Test database row to Customer object conversion"""
        # Test with valid row
        valid_row = (
            1, "test@example.com", "gopt_test123456789012345", "free",
            "2025-07-05T10:00:00", None, 1, 100.0, None, None
        )
        
        customer = revenue_manager.row_to_customer(valid_row)
        assert customer is not None
        assert customer.email == "test@example.com"
        assert customer.tier == "free"
        
        # Test with invalid row
        invalid_row = None
        assert revenue_manager.row_to_customer(invalid_row) is None
        
        # Test with incomplete row
        incomplete_row = (1, "test@example.com")
        assert revenue_manager.row_to_customer(incomplete_row) is None
    
    def test_database_error_handling(self, revenue_manager):
        """Test database error handling"""
        # Simulate database error by closing connection pool
        revenue_manager.db_pool.close_all()
        
        # Operations should handle errors gracefully
        result = revenue_manager.get_customer("test@example.com")
        assert result is None  # Should return None on error, not crash
    
    def test_cache_functionality(self, revenue_manager):
        """Test caching functionality"""
        # Create customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # First call should hit database
        result1 = revenue_manager.get_customer("test@example.com")
        
        # Second call should hit cache (we can't easily test this without mocking,
        # but we can verify it doesn't crash and returns same result)
        result2 = revenue_manager.get_customer("test@example.com")
        
        assert result1.email == result2.email
        assert result1.api_key == result2.api_key
    
    @patch('requests.post')
    def test_flutterwave_payment_creation(self, mock_post, revenue_manager, mock_flutterwave):
        """Test Flutterwave payment creation"""
        # Create customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # Mock successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'data': {'link': 'https://checkout.flutterwave.com/test'}
        }
        
        result = revenue_manager.create_flutterwave_payment(
            customer.email, 49.0, "USD"
        )
        
        assert result['status'] == 'success'
        assert 'payment_url' in result
    
    @patch('requests.post')
    def test_nowpayments_payment_creation(self, mock_post, revenue_manager):
        """Test NowPayments payment creation"""
        # Create customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # Mock successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'payment_id': 'test_id',
            'payment_status': 'waiting',
            'pay_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'pay_amount': 0.001,
            'pay_currency': 'btc'
        }
        
        result = revenue_manager.create_nowpayments_payment(
            customer.email, 49.0, "USD"
        )
        
        assert result['status'] == 'success'
        assert 'payment_id' in result
