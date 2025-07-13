"""
Integration tests for API endpoints
"""

import pytest
import json
from unittest.mock import patch

from gpu_optimizer_system import app, revenue_manager


class TestAPIEndpoints:
    """Test suite for API endpoint functionality"""
    
    def test_signup_endpoint_success(self, client, valid_email_data):
        """Test successful customer signup"""
        response = client.post(
            '/api/signup',
            data=json.dumps(valid_email_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'api_key' in data
        assert data['api_key'].startswith('gopt_')
    
    def test_signup_endpoint_invalid_email(self, client, invalid_email_data):
        """Test signup with invalid email"""
        response = client.post(
            '/api/signup',
            data=json.dumps(invalid_email_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_signup_endpoint_missing_data(self, client):
        """Test signup with missing data"""
        response = client.post(
            '/api/signup',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_signup_endpoint_duplicate_email(self, client, valid_email_data):
        """Test signup with duplicate email"""
        # First signup
        client.post(
            '/api/signup',
            data=json.dumps(valid_email_data),
            content_type='application/json'
        )
        
        # Second signup with same email
        response = client.post(
            '/api/signup',
            data=json.dumps(valid_email_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['message']
    
    def test_track_usage_endpoint_success(self, client, track_usage_data):
        """Test successful GPU usage tracking"""
        # First create a customer
        signup_response = client.post(
            '/api/signup',
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        api_key = json.loads(signup_response.data)['api_key']
        
        # Update track usage data with real API key
        track_usage_data['api_key'] = api_key
        
        response = client.post(
            '/api/track-usage',
            data=json.dumps(track_usage_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'gpus_monitored' in data
        assert 'potential_hourly_savings' in data
    
    def test_track_usage_endpoint_invalid_api_key(self, client, track_usage_data):
        """Test GPU usage tracking with invalid API key"""
        track_usage_data['api_key'] = 'invalid_key'
        
        response = client.post(
            '/api/track-usage',
            data=json.dumps(track_usage_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid' in data['error']
    
    def test_track_usage_endpoint_missing_api_key(self, client, sample_gpu_data):
        """Test GPU usage tracking without API key"""
        response = client.post(
            '/api/track-usage',
            data=json.dumps({'gpu_data': sample_gpu_data}),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    @patch('requests.post')
    def test_upgrade_endpoint_success(self, mock_post, client, upgrade_data):
        """Test successful customer upgrade"""
        # Mock Flutterwave response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'data': {'link': 'https://checkout.flutterwave.com/test'}
        }
        
        # First create a customer
        client.post(
            '/api/signup',
            data=json.dumps({'email': upgrade_data['customer_email']}),
            content_type='application/json'
        )
        
        response = client.post(
            '/api/upgrade',
            data=json.dumps(upgrade_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'payment_url' in data
    
    def test_upgrade_endpoint_nonexistent_customer(self, client, upgrade_data):
        """Test upgrade for non-existent customer"""
        upgrade_data['customer_email'] = 'nonexistent@example.com'
        
        response = client.post(
            '/api/upgrade',
            data=json.dumps(upgrade_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['message']
    
    def test_upgrade_endpoint_invalid_tier(self, client):
        """Test upgrade with invalid tier"""
        # Create customer first
        client.post(
            '/api/signup',
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        invalid_upgrade_data = {
            'customer_email': 'test@example.com',
            'tier': 'invalid_tier',
            'payment_method': 'flutterwave'
        }
        
        response = client.post(
            '/api/upgrade',
            data=json.dumps(invalid_upgrade_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_landing_page(self, client):
        """Test landing page endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'GPUOptimizer' in response.data
    
    def test_dashboard_page(self, client):
        """Test dashboard page endpoint"""
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'customers_by_tier' in data
        assert 'monthly_recurring_revenue' in data
    
    def test_rate_limiting(self, client, valid_email_data):
        """Test rate limiting on signup endpoint"""
        # Make multiple requests quickly
        responses = []
        for i in range(10):
            email_data = {'email': f'test{i}@example.com'}
            response = client.post(
                '/api/signup',
                data=json.dumps(email_data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429 status code)
        # Note: This test might be flaky depending on rate limit configuration
        assert any(status == 429 for status in responses[-3:])
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/signup')
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get('/')
        
        # Check for security headers (added by Talisman)
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
    
    def test_webhook_flutterwave(self, client):
        """Test Flutterwave webhook endpoint"""
        webhook_data = {
            'event': 'charge.completed',
            'data': {
                'id': 'test_payment_id',
                'status': 'successful',
                'customer': {'email': 'test@example.com'},
                'amount': 49
            }
        }
        
        response = client.post(
            '/payment/flutterwave/callback',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        # Should handle webhook (might return 400 if customer doesn't exist)
        assert response.status_code in [200, 400]
    
    def test_webhook_nowpayments(self, client):
        """Test NowPayments webhook endpoint"""
        webhook_data = {
            'payment_id': 'test_payment_id',
            'payment_status': 'finished',
            'order_id': 'test@example.com_professional'
        }
        
        # Mock signature header
        response = client.post(
            '/payment/nowpayments/webhook',
            data=json.dumps(webhook_data),
            content_type='application/json',
            headers={'x-nowpayments-sig': 'test_signature'}
        )
        
        # Should handle webhook (might return 400 for invalid signature)
        assert response.status_code in [200, 400]
    
    def test_malicious_input_handling(self, client, malicious_input_data):
        """Test handling of malicious input"""
        for attack_type, malicious_input in malicious_input_data.items():
            # Test with malicious email
            response = client.post(
                '/api/signup',
                data=json.dumps({'email': malicious_input}),
                content_type='application/json'
            )
            
            # Should reject malicious input
            assert response.status_code == 400
            
            # Should not crash the application
            health_response = client.get('/api/stats')
            assert health_response.status_code == 200
    
    def test_large_payload_handling(self, client):
        """Test handling of oversized payloads"""
        # Create oversized GPU data
        large_gpu_data = []
        for i in range(1000):  # Very large dataset
            large_gpu_data.append({
                'gpu_index': i,
                'gpu_name': f'GPU_{i}',
                'gpu_util': 50.0,
                'mem_used': 8000,
                'mem_total': 16000,
                'cost_per_hour': 3.0
            })
        
        response = client.post(
            '/api/track-usage',
            data=json.dumps({
                'api_key': 'gopt_test123456789012345',
                'gpu_data': large_gpu_data
            }),
            content_type='application/json'
        )
        
        # Should handle large payloads gracefully
        assert response.status_code in [400, 401, 413]  # Bad request, unauthorized, or payload too large
    
    def test_content_type_validation(self, client):
        """Test content type validation"""
        # Send request without proper content type
        response = client.post(
            '/api/signup',
            data='{"email": "test@example.com"}',
            content_type='text/plain'
        )
        
        # Should reject improper content type
        assert response.status_code == 400
    
    def test_method_not_allowed(self, client):
        """Test method not allowed responses"""
        # Try GET on POST-only endpoint
        response = client.get('/api/signup')
        assert response.status_code == 405
        
        # Try PUT on POST-only endpoint
        response = client.put('/api/signup')
        assert response.status_code == 405
    
    def test_api_versioning(self, client):
        """Test API versioning (if implemented)"""
        # Test that API endpoints are properly versioned
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        # Future: Test different API versions
        # response = client.get('/api/v2/stats')
    
    def test_error_response_format(self, client):
        """Test consistent error response format"""
        response = client.post(
            '/api/signup',
            data=json.dumps({'email': 'invalid-email'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        # Check error response format
        assert 'status' in data
        assert data['status'] == 'error'
        assert 'message' in data or 'error' in data
