"""
Pytest configuration and fixtures for GPUOptimizer tests
"""

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from gpu_optimizer_system import RevenueManager, Customer, app
from autonomous_acquisition import AutonomousAcquisition as CustomerAcquisitionBot


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def revenue_manager(temp_db):
    """Create a RevenueManager instance with temporary database"""
    manager = RevenueManager()
    manager.db_path = temp_db
    manager.init_database()
    return manager


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing"""
    from datetime import datetime
    return Customer(
        email="test@example.com",
        tier="free",
        api_key="gopt_test123456789012345",
        created_at=datetime.now(),
        gpu_count=1,
        monthly_savings=100.0
    )


@pytest.fixture
def sample_gpu_data():
    """Sample GPU data for testing"""
    return [
        {
            'gpu_index': 0,
            'gpu_name': 'Tesla V100',
            'gpu_util': 85.5,
            'mem_used': 12000,
            'mem_total': 16000,
            'temperature': 75.0,
            'cost_per_hour': 3.06
        },
        {
            'gpu_index': 1,
            'gpu_name': 'Tesla V100',
            'gpu_util': 10.0,  # Low utilization for savings calculation
            'mem_used': 2000,
            'mem_total': 16000,
            'temperature': 65.0,
            'cost_per_hour': 3.06
        }
    ]


@pytest.fixture
def flask_app():
    """Create Flask app for testing"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(flask_app):
    """Create Flask test client"""
    return flask_app.test_client()


@pytest.fixture
def mock_flutterwave():
    """Mock Flutterwave API responses"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'link': 'https://checkout.flutterwave.com/test',
                'id': 'test_payment_id'
            }
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_nowpayments():
    """Mock NowPayments API responses"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'payment_id': 'test_crypto_payment_id',
            'payment_status': 'waiting',
            'pay_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'pay_amount': 0.001,
            'pay_currency': 'btc'
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_email():
    """Mock email sending"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        yield mock_server


@pytest.fixture
def acquisition_bot(temp_db):
    """Create CustomerAcquisitionBot for testing"""
    bot = CustomerAcquisitionBot()
    bot.db_path = temp_db
    bot.init_database()
    return bot


# Test data fixtures
@pytest.fixture
def valid_email_data():
    """Valid email data for testing"""
    return {"email": "test@example.com"}


@pytest.fixture
def invalid_email_data():
    """Invalid email data for testing"""
    return {"email": "invalid-email"}


@pytest.fixture
def upgrade_data():
    """Valid upgrade data for testing"""
    return {
        "customer_email": "test@example.com",
        "tier": "professional",
        "payment_method": "flutterwave"
    }


@pytest.fixture
def track_usage_data(sample_gpu_data):
    """Valid track usage data for testing"""
    return {
        "api_key": "gopt_test123456789012345",
        "gpu_data": sample_gpu_data
    }


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'FLUTTERWAVE_SECRET_KEY': 'test_flutterwave_key',
        'FLUTTERWAVE_PUBLIC_KEY': 'test_flutterwave_public',
        'NOWPAYMENTS_API_KEY': 'test_nowpayments_key',
        'NOWPAYMENTS_IPN_SECRET': 'test_ipn_secret',
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'test_password',
        'SECRET_KEY': 'test_secret_key',
        'ENCRYPTION_KEY': 'test_encryption_key'
    }
    
    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield
    
    # Cleanup environment variables
    for key in test_env.keys():
        os.environ.pop(key, None)


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database testing utilities
@pytest.fixture
def db_connection(temp_db):
    """Direct database connection for testing"""
    conn = sqlite3.connect(temp_db)
    yield conn
    conn.close()


# Security testing fixtures
@pytest.fixture
def malicious_input_data():
    """Malicious input data for security testing"""
    return {
        'sql_injection': "'; DROP TABLE customers; --",
        'xss_script': '<script>alert("xss")</script>',
        'path_traversal': '../../../etc/passwd',
        'command_injection': '; rm -rf /',
        'oversized_input': 'A' * 10000
    }
