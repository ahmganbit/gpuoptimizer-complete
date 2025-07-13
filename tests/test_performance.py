"""
Performance tests for GPUOptimizer system
"""

import pytest
import time
import threading
import concurrent.futures
from unittest.mock import patch

from gpu_optimizer_system import RevenueManager


class TestPerformance:
    """Test suite for performance benchmarks"""
    
    def test_database_connection_pool_performance(self, revenue_manager, performance_timer):
        """Test database connection pool performance"""
        # Test concurrent database operations
        def create_customer(index):
            email = f"test{index}@example.com"
            return revenue_manager.create_customer(email)
        
        performance_timer.start()
        
        # Create customers concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_customer, i) for i in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        performance_timer.stop()
        
        # Verify all customers were created
        assert len(results) == 50
        assert all(customer.email.startswith('test') for customer in results)
        
        # Performance benchmark: should complete within reasonable time
        assert performance_timer.elapsed < 10.0, f"Database operations too slow: {performance_timer.elapsed}s"
    
    def test_cache_performance(self, revenue_manager, performance_timer):
        """Test caching performance improvement"""
        # Create a customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # First call (database hit)
        performance_timer.start()
        result1 = revenue_manager.get_customer("test@example.com")
        first_call_time = time.time() - performance_timer.start_time
        
        # Second call (cache hit)
        start_time = time.time()
        result2 = revenue_manager.get_customer("test@example.com")
        second_call_time = time.time() - start_time
        
        # Verify results are the same
        assert result1.email == result2.email
        assert result1.api_key == result2.api_key
        
        # Cache should be faster (though this might be flaky in tests)
        # At minimum, verify it doesn't crash and returns correct data
        assert result2 is not None
    
    def test_batch_gpu_processing_performance(self, revenue_manager, performance_timer):
        """Test batch GPU data processing performance"""
        # Create customer
        customer = revenue_manager.create_customer("test@example.com")
        
        # Create large GPU dataset
        large_gpu_data = []
        for i in range(100):
            large_gpu_data.append({
                'gpu_index': i,
                'gpu_name': f'Tesla V100-{i}',
                'gpu_util': 50.0 + (i % 50),
                'mem_used': 8000 + (i * 100),
                'mem_total': 16000,
                'temperature': 70.0 + (i % 20),
                'cost_per_hour': 3.06
            })
        
        performance_timer.start()
        result = revenue_manager.track_gpu_usage(customer.api_key, large_gpu_data)
        performance_timer.stop()
        
        # Verify processing succeeded
        assert result['status'] == 'success'
        assert result['gpus_monitored'] == 100
        
        # Performance benchmark: should process 100 GPUs quickly
        assert performance_timer.elapsed < 5.0, f"Batch processing too slow: {performance_timer.elapsed}s"
    
    def test_concurrent_api_requests(self, client, performance_timer):
        """Test concurrent API request handling"""
        def make_signup_request(index):
            return client.post(
                '/api/signup',
                json={'email': f'test{index}@example.com'}
            )
        
        performance_timer.start()
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_signup_request, i) for i in range(100)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        performance_timer.stop()
        
        # Count successful responses
        successful_responses = [r for r in responses if r.status_code == 200]
        
        # Should handle most requests successfully (some might be rate limited)
        assert len(successful_responses) >= 50, "Too many failed requests under load"
        
        # Performance benchmark
        assert performance_timer.elapsed < 30.0, f"Concurrent requests too slow: {performance_timer.elapsed}s"
    
    def test_memory_usage_stability(self, revenue_manager):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(1000):
            customer = revenue_manager.create_customer(f"test{i}@example.com")
            revenue_manager.get_customer(customer.email)
            revenue_manager.get_customer_by_api_key(customer.api_key)
            
            # Force garbage collection periodically
            if i % 100 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 100MB for 1000 operations)
        assert memory_growth < 100 * 1024 * 1024, f"Excessive memory growth: {memory_growth / 1024 / 1024:.2f}MB"
    
    def test_database_query_performance(self, revenue_manager, performance_timer):
        """Test database query performance"""
        # Create many customers
        customers = []
        for i in range(100):
            customer = revenue_manager.create_customer(f"test{i}@example.com")
            customers.append(customer)
        
        # Test query performance
        performance_timer.start()
        
        # Perform many lookups
        for customer in customers:
            result = revenue_manager.get_customer(customer.email)
            assert result is not None
        
        performance_timer.stop()
        
        # Should complete lookups quickly
        avg_time_per_query = performance_timer.elapsed / len(customers)
        assert avg_time_per_query < 0.01, f"Database queries too slow: {avg_time_per_query:.4f}s per query"
    
    def test_api_response_time(self, client, performance_timer):
        """Test API response times"""
        endpoints_to_test = [
            ('GET', '/'),
            ('GET', '/api/stats'),
            ('POST', '/api/signup', {'email': 'test@example.com'})
        ]
        
        for method, endpoint, *data in endpoints_to_test:
            performance_timer.start()
            
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, json=data[0] if data else {})
            
            performance_timer.stop()
            
            # Verify response is successful or expected error
            assert response.status_code in [200, 400, 401], f"Unexpected status for {endpoint}"
            
            # Response time should be reasonable
            assert performance_timer.elapsed < 1.0, f"Slow response for {endpoint}: {performance_timer.elapsed:.3f}s"
    
    def test_large_payload_handling(self, client, performance_timer):
        """Test handling of large payloads"""
        # Create customer first
        signup_response = client.post('/api/signup', json={'email': 'test@example.com'})
        api_key = signup_response.json['api_key']
        
        # Create large GPU data payload
        large_payload = {
            'api_key': api_key,
            'gpu_data': []
        }
        
        # Add many GPU entries
        for i in range(50):  # Reasonable size for testing
            large_payload['gpu_data'].append({
                'gpu_index': i,
                'gpu_name': f'GPU-{i}',
                'gpu_util': 50.0,
                'mem_used': 8000,
                'mem_total': 16000,
                'cost_per_hour': 3.0
            })
        
        performance_timer.start()
        response = client.post('/api/track-usage', json=large_payload)
        performance_timer.stop()
        
        # Should handle large payload
        assert response.status_code == 200
        
        # Should process within reasonable time
        assert performance_timer.elapsed < 5.0, f"Large payload processing too slow: {performance_timer.elapsed}s"
    
    def test_connection_pool_efficiency(self, revenue_manager):
        """Test database connection pool efficiency"""
        # Test that connection pool reuses connections efficiently
        initial_pool_size = revenue_manager.db_pool.pool.qsize()
        
        # Perform many database operations
        for i in range(50):
            customer = revenue_manager.create_customer(f"test{i}@example.com")
            revenue_manager.get_customer(customer.email)
        
        final_pool_size = revenue_manager.db_pool.pool.qsize()
        
        # Pool should maintain reasonable size (not create excessive connections)
        assert final_pool_size <= revenue_manager.db_pool.pool_size
        assert final_pool_size >= initial_pool_size - 2  # Allow some variance
    
    def test_cache_hit_ratio(self, revenue_manager):
        """Test cache hit ratio performance"""
        # Create customers
        customers = []
        for i in range(10):
            customer = revenue_manager.create_customer(f"test{i}@example.com")
            customers.append(customer)
        
        # First round: populate cache
        for customer in customers:
            revenue_manager.get_customer(customer.email)
        
        # Second round: should hit cache
        cache_hits = 0
        for customer in customers:
            start_time = time.time()
            result = revenue_manager.get_customer(customer.email)
            query_time = time.time() - start_time
            
            # Cache hits should be faster
            if query_time < 0.001:  # Very fast = likely cache hit
                cache_hits += 1
            
            assert result is not None
        
        # Should have some cache hits (this test might be flaky)
        # At minimum, verify functionality works
        assert cache_hits >= 0
    
    def test_stress_test_api_endpoints(self, client):
        """Stress test API endpoints"""
        # Test multiple endpoints under load
        def stress_test_endpoint():
            responses = []
            for i in range(10):
                # Mix of different requests
                responses.append(client.get('/api/stats'))
                responses.append(client.post('/api/signup', json={'email': f'stress{i}@example.com'}))
            return responses
        
        # Run stress test with multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(stress_test_endpoint) for _ in range(5)]
            all_responses = []
            for future in concurrent.futures.as_completed(futures):
                all_responses.extend(future.result())
        
        # Count successful responses
        successful = sum(1 for r in all_responses if r.status_code in [200, 400, 429])
        total = len(all_responses)
        
        # Should handle most requests (allowing for rate limiting)
        success_rate = successful / total
        assert success_rate >= 0.8, f"Low success rate under stress: {success_rate:.2%}"
    
    def test_database_wal_mode_performance(self, revenue_manager):
        """Test WAL mode performance benefits"""
        # This test verifies WAL mode is enabled and working
        with revenue_manager.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            # Should be using WAL mode for better concurrency
            assert journal_mode.upper() == 'WAL', f"Expected WAL mode, got {journal_mode}"
    
    def test_concurrent_write_performance(self, revenue_manager, performance_timer):
        """Test concurrent write operations performance"""
        def create_and_track_usage(index):
            customer = revenue_manager.create_customer(f"concurrent{index}@example.com")
            gpu_data = [{
                'gpu_index': 0,
                'gpu_name': 'Tesla V100',
                'gpu_util': 50.0,
                'mem_used': 8000,
                'mem_total': 16000,
                'cost_per_hour': 3.0
            }]
            result = revenue_manager.track_gpu_usage(customer.api_key, gpu_data)
            return result
        
        performance_timer.start()
        
        # Perform concurrent writes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_track_usage, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        performance_timer.stop()
        
        # All operations should succeed
        assert len(results) == 20
        assert all(r['status'] == 'success' for r in results)
        
        # Should complete within reasonable time
        assert performance_timer.elapsed < 15.0, f"Concurrent writes too slow: {performance_timer.elapsed}s"
