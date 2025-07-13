#!/usr/bin/env python3
"""
GPUOptimizer Autopilot Startup Script
One-click startup for the complete automated revenue system
"""

import os
import sys
import time
import logging
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autopilot_startup.log'),
        logging.StreamHandler()
    ]
)

class AutopilotStarter:
    """Automated startup system for GPUOptimizer"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_files = [
            'gpu_optimizer_system.py',
            'autonomous_acquisition.py',
            'marketing_automation.py',
            'seo_growth_engine.py',
            'affiliate_system.py',
            'autopilot_revenue.py',
            'intelligent_onboarding.py',
            'revenue_analytics.py',
            'growth_engine.py',
            'master_orchestrator.py'
        ]
        
        self.required_env_vars = [
            'SECRET_KEY',
            'ENCRYPTION_KEY',
            'SENDER_EMAIL',
            'SENDER_PASSWORD',
            'DOMAIN'
        ]
        
        self.optional_env_vars = [
            'OPENAI_API_KEY',
            'STRIPE_SECRET_KEY',
            'FLUTTERWAVE_SECRET_KEY',
            'NOWPAYMENTS_API_KEY',
            'GITHUB_TOKEN',
            'TWITTER_API_KEY',
            'LINKEDIN_CLIENT_ID',
            'SENDGRID_API_KEY',
            'GOOGLE_ADS_DEVELOPER_TOKEN'
        ]
    
    def start_autopilot_system(self):
        """Start the complete autopilot system"""
        try:
            print("🚀 Starting GPUOptimizer Autopilot System...")
            print("=" * 60)
            
            # Pre-flight checks
            self.run_preflight_checks()
            
            # Setup environment
            self.setup_environment()
            
            # Initialize databases
            self.initialize_databases()
            
            # Start web server
            self.start_web_server()
            
            # Start master orchestrator
            self.start_master_orchestrator()
            
            print("\n✅ GPUOptimizer Autopilot System Started Successfully!")
            print("=" * 60)
            self.display_system_info()
            
        except Exception as e:
            logging.error(f"Startup failed: {e}")
            print(f"❌ Startup failed: {e}")
            sys.exit(1)
    
    def run_preflight_checks(self):
        """Run pre-flight system checks"""
        print("🔍 Running pre-flight checks...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ required")
        print("✓ Python version check passed")
        
        # Check required files
        missing_files = []
        for file in self.required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            raise Exception(f"Missing required files: {missing_files}")
        print("✓ Required files check passed")
        
        # Check dependencies
        self.check_dependencies()
        print("✓ Dependencies check passed")
        
        # Check environment variables
        self.check_environment_variables()
        print("✓ Environment variables check passed")
    
    def check_dependencies(self):
        """Check if required Python packages are installed"""
        required_packages = [
            'flask',
            'requests',
            'sqlite3',
            'pandas',
            'numpy',
            'schedule',
            'cryptography',
            'stripe',
            'matplotlib',
            'seaborn',
            'plotly',
            'scikit-learn'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️  Installing missing packages: {missing_packages}")
            self.install_packages(missing_packages)
    
    def install_packages(self, packages):
        """Install missing Python packages"""
        try:
            for package in packages:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ Installed {package}")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install packages: {e}")
    
    def check_environment_variables(self):
        """Check environment variables"""
        # Check for .env file
        env_file = self.project_root / '.env'
        if not env_file.exists():
            print("⚠️  .env file not found, creating from template...")
            self.create_env_file()
        
        # Load environment variables
        self.load_env_file()
        
        # Check required variables
        missing_required = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        if missing_required:
            print(f"⚠️  Missing required environment variables: {missing_required}")
            print("Please update your .env file with the required values")
            
        # Check optional variables
        missing_optional = []
        for var in self.optional_env_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_optional:
            print(f"ℹ️  Optional environment variables not set: {missing_optional}")
            print("Some features may be limited without these API keys")
    
    def create_env_file(self):
        """Create .env file from template"""
        env_template = """# GPUOptimizer Environment Configuration
# Required Variables
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-email-password
DOMAIN=localhost:5000

# Database Configuration
DATABASE_URL=sqlite:///gpuoptimizer.db
REDIS_URL=redis://localhost:6379/0

# Payment Processing
STRIPE_SECRET_KEY=sk_test_your_stripe_key
FLUTTERWAVE_SECRET_KEY=your_flutterwave_key
NOWPAYMENTS_API_KEY=your_nowpayments_key

# AI/ML Services
OPENAI_API_KEY=your_openai_key

# Social Media APIs
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_twitter_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_token_secret

LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_secret

FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_secret

# Email Marketing
SENDGRID_API_KEY=your_sendgrid_key
MAILCHIMP_API_KEY=your_mailchimp_key

# SEO/Analytics
GOOGLE_ADS_DEVELOPER_TOKEN=your_google_ads_token
AHREFS_API_KEY=your_ahrefs_key
SEMRUSH_API_KEY=your_semrush_key

# GitHub Integration
GITHUB_TOKEN=your_github_token
"""
        
        with open(self.project_root / '.env', 'w') as f:
            f.write(env_template)
        
        print("✓ Created .env file template")
    
    def load_env_file(self):
        """Load environment variables from .env file"""
        env_file = self.project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    def setup_environment(self):
        """Setup runtime environment"""
        print("🔧 Setting up environment...")
        
        # Create necessary directories
        directories = ['logs', 'data', 'reports', 'backups']
        for directory in directories:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        # Set Python path
        sys.path.insert(0, str(self.project_root))
        
        print("✓ Environment setup complete")
    
    def initialize_databases(self):
        """Initialize all system databases"""
        print("🗄️  Initializing databases...")
        
        try:
            # Import and initialize each system to create databases
            from gpu_optimizer_system import GPUOptimizerSystem
            from autonomous_acquisition import AutonomousAcquisition
            from marketing_automation import MarketingAutomation
            from seo_growth_engine import SEOGrowthEngine
            from affiliate_system import AffiliateSystem
            from autopilot_revenue import AutopilotRevenue
            from intelligent_onboarding import IntelligentOnboarding
            from revenue_analytics import RevenueAnalytics
            from growth_engine import GrowthEngine
            
            # Initialize core system
            gpu_system = GPUOptimizerSystem()
            
            # Initialize other systems (this creates their databases)
            AutonomousAcquisition(gpu_system)
            MarketingAutomation()
            SEOGrowthEngine()
            AffiliateSystem()
            AutopilotRevenue(gpu_system)
            IntelligentOnboarding(gpu_system)
            RevenueAnalytics(gpu_system)
            GrowthEngine(gpu_system, AffiliateSystem())
            
            print("✓ All databases initialized")
            
        except Exception as e:
            raise Exception(f"Database initialization failed: {e}")
    
    def start_web_server(self):
        """Start the Flask web server"""
        print("🌐 Starting web server...")
        
        try:
            # Start Flask app in background
            import threading
            from gpu_optimizer_system import app
            
            def run_flask():
                app.run(host='0.0.0.0', port=5000, debug=False)
            
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            # Wait a moment for server to start
            time.sleep(2)
            
            print("✓ Web server started on http://localhost:5000")
            
        except Exception as e:
            raise Exception(f"Web server startup failed: {e}")
    
    def start_master_orchestrator(self):
        """Start the master orchestrator"""
        print("🎯 Starting master orchestrator...")
        
        try:
            from master_orchestrator import MasterOrchestrator
            
            # Start orchestrator in background thread
            def run_orchestrator():
                orchestrator = MasterOrchestrator()
                orchestrator.start_orchestration()
            
            orchestrator_thread = threading.Thread(target=run_orchestrator, daemon=True)
            orchestrator_thread.start()
            
            print("✓ Master orchestrator started")
            
        except Exception as e:
            raise Exception(f"Master orchestrator startup failed: {e}")
    
    def display_system_info(self):
        """Display system information and next steps"""
        print("\n📊 System Information:")
        print(f"• Web Interface: http://localhost:5000")
        print(f"• API Endpoint: http://localhost:5000/api")
        print(f"• Admin Dashboard: http://localhost:5000/admin")
        print(f"• Project Directory: {self.project_root}")
        print(f"• Logs Directory: {self.project_root}/logs")
        
        print("\n🎯 Active Systems:")
        print("• Autonomous Customer Acquisition")
        print("• Marketing Automation")
        print("• SEO & Growth Engine")
        print("• Affiliate Program")
        print("• Autopilot Revenue Optimization")
        print("• Intelligent Customer Onboarding")
        print("• Revenue Analytics & Forecasting")
        print("• Viral Growth Engine")
        
        print("\n📈 Next Steps:")
        print("1. Visit the web interface to configure your settings")
        print("2. Add your API keys in the .env file for full functionality")
        print("3. Monitor the logs for system performance")
        print("4. Check the admin dashboard for revenue metrics")
        
        print("\n🔄 The system is now running autonomously!")
        print("Press Ctrl+C to stop the system")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(60)
                print(f"⏰ System running... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system...")

def main():
    """Main entry point"""
    try:
        starter = AutopilotStarter()
        starter.start_autopilot_system()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
