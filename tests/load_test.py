"""
Load testing for GPUOptimizer using Locust
Run with: locust -f tests/load_test.py --host=http://localhost:5000
"""

from locust import HttpUser, task, between
import json
import random
import string


class GPUOptimizerUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Setup user session"""
        self.api_key = None
        self.email = self.generate_random_email()
        self.signup()
    
    def generate_random_email(self):
        """Generate random email for testing"""
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@loadtest.com"
    
    def signup(self):
        """Sign up a new user"""
        response = self.client.post(
            "/api/signup",
            json={"email": self.email},
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.api_key = data.get('api_key')
            response.success()
        else:
            response.failure(f"Signup failed: {response.status_code}")
    
    @task(3)
    def track_gpu_usage(self):
        """Track GPU usage (most common operation)"""
        if not self.api_key:
            return
        
        gpu_data = self.generate_gpu_data()
        
        response = self.client.post(
            "/api/track-usage",
            json={
                "api_key": self.api_key,
                "gpu_data": gpu_data
            },
            catch_response=True
        )
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Track usage failed: {response.status_code}")
    
    @task(1)
    def view_dashboard(self):
        """View dashboard page"""
        response = self.client.get("/dashboard", catch_response=True)
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Dashboard failed: {response.status_code}")
    
    @task(1)
    def get_stats(self):
        """Get system stats"""
        response = self.client.get("/api/stats", catch_response=True)
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Stats failed: {response.status_code}")
    
    @task(1)
    def view_landing_page(self):
        """View landing page"""
        response = self.client.get("/", catch_response=True)
        
        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Landing page failed: {response.status_code}")
    
    def generate_gpu_data(self):
        """Generate realistic GPU data for testing"""
        num_gpus = random.randint(1, 4)
        gpu_data = []
        
        for i in range(num_gpus):
            gpu_data.append({
                'gpu_index': i,
                'gpu_name': random.choice(['Tesla V100', 'Tesla P100', 'RTX 3090', 'A100']),
                'gpu_util': random.uniform(10, 95),
                'mem_used': random.randint(2000, 15000),
                'mem_total': 16000,
                'temperature': random.uniform(60, 85),
                'cost_per_hour': random.uniform(2.5, 4.0)
            })
        
        return gpu_data


class AdminUser(HttpUser):
    """Admin user for testing admin operations"""
    
    wait_time = between(5, 10)  # Admins check less frequently
    weight = 1  # Lower weight = fewer admin users
    
    @task
    def check_stats(self):
        """Admin checking system stats"""
        self.client.get("/api/stats")
    
    @task
    def view_dashboard(self):
        """Admin viewing dashboard"""
        self.client.get("/dashboard")


class HeavyUser(HttpUser):
    """Heavy user simulating enterprise customers"""
    
    wait_time = between(0.5, 1)  # More frequent requests
    weight = 2  # More heavy users
    
    def on_start(self):
        """Setup heavy user"""
        self.api_key = None
        self.email = f"heavy_{random.randint(1000, 9999)}@enterprise.com"
        self.signup()
    
    def signup(self):
        """Sign up heavy user"""
        response = self.client.post("/api/signup", json={"email": self.email})
        if response.status_code == 200:
            self.api_key = response.json().get('api_key')
    
    @task(5)
    def track_large_gpu_cluster(self):
        """Track large GPU cluster"""
        if not self.api_key:
            return
        
        # Enterprise users have more GPUs
        gpu_data = []
        for i in range(random.randint(8, 16)):
            gpu_data.append({
                'gpu_index': i,
                'gpu_name': 'A100',
                'gpu_util': random.uniform(70, 95),  # Higher utilization
                'mem_used': random.randint(30000, 80000),
                'mem_total': 80000,
                'temperature': random.uniform(70, 85),
                'cost_per_hour': 8.0
            })
        
        self.client.post(
            "/api/track-usage",
            json={
                "api_key": self.api_key,
                "gpu_data": gpu_data
            }
        )


# Load test scenarios
class QuickLoadTest(HttpUser):
    """Quick load test for CI/CD"""
    
    wait_time = between(1, 2)
    
    @task
    def quick_test(self):
        """Quick test of main endpoints"""
        self.client.get("/")
        self.client.get("/api/stats")


# Custom load test shapes
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    Step load pattern:
    - Start with 10 users
    - Increase by 10 every 30 seconds
    - Max 100 users
    - Run for 5 minutes total
    """
    
    step_time = 30
    step_load = 10
    spawn_rate = 5
    time_limit = 300
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        user_count = min(self.step_load * (current_step + 1), 100)
        
        return (user_count, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load pattern:
    - Normal load: 20 users
    - Spike to 100 users for 1 minute
    - Back to normal
    """
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time < 60:
            return (20, 5)  # Normal load
        elif run_time < 120:
            return (100, 20)  # Spike
        elif run_time < 180:
            return (20, 5)  # Back to normal
        else:
            return None  # End test
