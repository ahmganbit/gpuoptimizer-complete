#!/usr/bin/env python3
"""
GPUOptimizer Test Runner
Comprehensive test execution script with multiple test categories and reporting
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


class TestRunner:
    """Test runner for GPUOptimizer system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        
    def run_command(self, command, description=""):
        """Run a command and return success status"""
        print(f"\n{'='*60}")
        print(f"Running: {description or command}")
        print(f"{'='*60}")
        
        start_time = time.time()
        result = subprocess.run(command, shell=True, cwd=self.project_root)
        end_time = time.time()
        
        duration = end_time - start_time
        status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
        print(f"\n{status} - Duration: {duration:.2f}s")
        
        return result.returncode == 0
    
    def install_dependencies(self):
        """Install test dependencies"""
        print("Installing test dependencies...")
        return self.run_command(
            "pip install -r requirements-dev.txt",
            "Installing development dependencies"
        )
    
    def run_unit_tests(self):
        """Run unit tests"""
        return self.run_command(
            "pytest tests/test_revenue_manager.py -v -m 'not slow'",
            "Unit Tests - RevenueManager"
        )
    
    def run_integration_tests(self):
        """Run integration tests"""
        return self.run_command(
            "pytest tests/test_api_endpoints.py -v",
            "Integration Tests - API Endpoints"
        )
    
    def run_security_tests(self):
        """Run security tests"""
        return self.run_command(
            "pytest tests/test_security.py -v",
            "Security Tests"
        )
    
    def run_performance_tests(self):
        """Run performance tests"""
        return self.run_command(
            "pytest tests/test_performance.py -v --benchmark-only",
            "Performance Tests"
        )
    
    def run_all_tests(self):
        """Run all tests with coverage"""
        return self.run_command(
            "pytest tests/ -v --cov=gpu_optimizer_system --cov-report=html --cov-report=term",
            "All Tests with Coverage"
        )
    
    def run_quick_tests(self):
        """Run quick tests (excluding slow ones)"""
        return self.run_command(
            "pytest tests/ -v -m 'not slow and not performance'",
            "Quick Test Suite"
        )
    
    def run_code_quality_checks(self):
        """Run code quality checks"""
        checks = [
            ("black --check .", "Code Formatting Check (Black)"),
            ("isort --check-only .", "Import Sorting Check (isort)"),
            ("flake8 .", "Linting Check (flake8)"),
            ("mypy gpu_optimizer_system.py", "Type Checking (mypy)"),
            ("bandit -r . -f json", "Security Linting (bandit)")
        ]
        
        all_passed = True
        for command, description in checks:
            if not self.run_command(command, description):
                all_passed = False
        
        return all_passed
    
    def run_security_scan(self):
        """Run security vulnerability scan"""
        return self.run_command(
            "safety check --json",
            "Dependency Security Scan (safety)"
        )
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        return self.run_command(
            "pytest tests/ --html=reports/test_report.html --self-contained-html --cov=gpu_optimizer_system --cov-report=html:reports/coverage",
            "Generating Test Report"
        )
    
    def run_load_tests(self):
        """Run load tests using locust"""
        print("\n" + "="*60)
        print("Load Testing Instructions")
        print("="*60)
        print("To run load tests:")
        print("1. Start the application: python gpu_optimizer_system.py")
        print("2. In another terminal, run: locust -f tests/load_test.py --host=http://localhost:5000")
        print("3. Open http://localhost:8089 to configure and start load test")
        return True
    
    def setup_test_environment(self):
        """Setup test environment"""
        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Set test environment variables
        test_env = {
            'TESTING': 'true',
            'DATABASE_URL': 'sqlite:///test.db',
            'SECRET_KEY': 'test-secret-key',
            'FLUTTERWAVE_SECRET_KEY': 'test-key',
            'NOWPAYMENTS_API_KEY': 'test-key'
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        print("✅ Test environment configured")
        return True
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        # Remove test databases
        test_files = ['test.db', 'test.db-wal', 'test.db-shm']
        for file in test_files:
            file_path = self.project_root / file
            if file_path.exists():
                file_path.unlink()
        
        print("✅ Test environment cleaned up")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="GPUOptimizer Test Runner")
    parser.add_argument(
        'test_type',
        choices=[
            'all', 'unit', 'integration', 'security', 'performance',
            'quick', 'quality', 'scan', 'report', 'load', 'install'
        ],
        help='Type of tests to run'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='Skip cleanup after tests'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Setup
    if not runner.setup_test_environment():
        print("❌ Failed to setup test environment")
        sys.exit(1)
    
    success = True
    
    try:
        # Run selected tests
        if args.test_type == 'install':
            success = runner.install_dependencies()
        elif args.test_type == 'unit':
            success = runner.run_unit_tests()
        elif args.test_type == 'integration':
            success = runner.run_integration_tests()
        elif args.test_type == 'security':
            success = runner.run_security_tests()
        elif args.test_type == 'performance':
            success = runner.run_performance_tests()
        elif args.test_type == 'quick':
            success = runner.run_quick_tests()
        elif args.test_type == 'quality':
            success = runner.run_code_quality_checks()
        elif args.test_type == 'scan':
            success = runner.run_security_scan()
        elif args.test_type == 'report':
            success = runner.generate_test_report()
        elif args.test_type == 'load':
            success = runner.run_load_tests()
        elif args.test_type == 'all':
            # Run comprehensive test suite
            steps = [
                runner.run_unit_tests,
                runner.run_integration_tests,
                runner.run_security_tests,
                runner.run_code_quality_checks,
                runner.generate_test_report
            ]
            
            for step in steps:
                if not step():
                    success = False
                    break
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if success:
            print("🎉 All tests completed successfully!")
            print("\nNext steps:")
            print("- Review coverage report in reports/coverage/index.html")
            print("- Check test report in reports/test_report.html")
            print("- Run 'python run_tests.py load' for load testing")
        else:
            print("❌ Some tests failed. Please review the output above.")
            print("\nTroubleshooting:")
            print("- Check test logs for specific failures")
            print("- Ensure all dependencies are installed")
            print("- Verify test environment configuration")
    
    finally:
        # Cleanup
        if not args.no_cleanup:
            runner.cleanup_test_environment()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
