#!/usr/bin/env python3
"""
GPUOptimizer Render Deployment Helper
Automates the deployment process to Render
"""

import os
import subprocess
import sys
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_git_status():
    """Check if git is initialized and has changes"""
    if not os.path.exists('.git'):
        print("📁 Git repository not initialized")
        return False
    
    result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("📝 Uncommitted changes detected")
        return True
    else:
        print("✅ No uncommitted changes")
        return False

def create_render_config():
    """Create render.yaml configuration"""
    config = {
        'services': [{
            'type': 'web',
            'name': 'gpuoptimizer',
            'env': 'python',
            'plan': 'free',
            'buildCommand': 'pip install -r requirements.txt',
            'startCommand': 'python gpu_optimizer_system.py',
            'healthCheckPath': '/api/health',
            'envVars': [
                {'key': 'PYTHON_VERSION', 'value': '3.9.18'},
                {'key': 'FLASK_ENV', 'value': 'production'},
                {'key': 'PORT', 'value': '10000'}
            ]
        }]
    }
    
    try:
        with open('render.yaml', 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        print("✅ render.yaml created")
        return True
    except ImportError:
        # If PyYAML not available, create manually
        yaml_content = """services:
  - type: web
    name: gpuoptimizer
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python gpu_optimizer_system.py
    healthCheckPath: /api/health
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 10000
"""
        with open('render.yaml', 'w') as f:
            f.write(yaml_content)
        print("✅ render.yaml created")
        return True
    except Exception as e:
        print(f"❌ Failed to create render.yaml: {e}")
        return False

def main():
    """Main deployment process"""
    print("🚀 GPUOptimizer Render Deployment Helper")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('gpu_optimizer_system.py'):
        print("❌ gpu_optimizer_system.py not found. Please run this from the project root.")
        sys.exit(1)
    
    # Step 1: Create render configuration
    print("\n📋 Step 1: Creating Render configuration...")
    if not create_render_config():
        print("❌ Failed to create Render configuration")
        sys.exit(1)
    
    # Step 2: Initialize git if needed
    print("\n📋 Step 2: Setting up Git repository...")
    if not os.path.exists('.git'):
        if not run_command('git init', 'Initializing Git repository'):
            sys.exit(1)
    
    # Step 3: Add all files
    print("\n📋 Step 3: Adding files to Git...")
    if not run_command('git add .', 'Adding files to Git'):
        sys.exit(1)
    
    # Step 4: Commit changes
    print("\n📋 Step 4: Committing changes...")
    commit_message = f"Deploy GPUOptimizer to Render - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_message}"', 'Committing changes'):
        # Check if there are no changes to commit
        result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
        if not result.stdout.strip():
            print("ℹ️ No changes to commit")
        else:
            print("❌ Failed to commit changes")
            sys.exit(1)
    
    # Step 5: Check for GitHub remote
    print("\n📋 Step 5: Checking GitHub remote...")
    result = subprocess.run('git remote -v', shell=True, capture_output=True, text=True)
    if 'origin' not in result.stdout:
        print("⚠️ No GitHub remote found. Please set up GitHub repository:")
        print("1. Go to https://github.com/new")
        print("2. Create repository: gpuoptimizer-complete")
        print("3. Run: git remote add origin https://github.com/YOURUSERNAME/gpuoptimizer-complete.git")
        print("4. Run: git push -u origin main")
        print("5. Then continue with Render deployment")
    else:
        print("✅ GitHub remote found")
        
        # Try to push
        print("\n📋 Step 6: Pushing to GitHub...")
        if run_command('git push', 'Pushing to GitHub'):
            print("✅ Code pushed to GitHub successfully")
        else:
            print("⚠️ Push failed. You may need to set upstream:")
            print("Run: git push -u origin main")
    
    # Step 6: Deployment instructions
    print("\n" + "=" * 50)
    print("🎉 Preparation Complete!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Go to https://render.com")
    print("2. Sign up with your GitHub account")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your 'gpuoptimizer-complete' repository")
    print("5. Configure:")
    print("   - Name: gpuoptimizer")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python gpu_optimizer_system.py")
    print("6. Add environment variables:")
    print("   - SECRET_KEY=your-secret-key-32-chars")
    print("   - ENCRYPTION_KEY=your-encryption-key-32-chars")
    print("   - FLASK_ENV=production")
    print("7. Click 'Create Web Service'")
    print("\n🌐 Your app will be available at: https://gpuoptimizer.onrender.com")
    print("\n📚 For detailed instructions, see: RENDER_DEPLOYMENT.md")
    
    # Step 7: Environment variables template
    print("\n📋 Environment Variables Template:")
    print("-" * 30)
    env_template = """SECRET_KEY=your-secret-key-32-characters-minimum
ENCRYPTION_KEY=your-encryption-key-32-characters
FLASK_ENV=production

# Payment Gateways (add as you set them up)
NOWPAYMENTS_API_KEY=your_nowpayments_api_key
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_secret_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_public_key
PADDLE_VENDOR_ID=your_paddle_vendor_id
PADDLE_VENDOR_AUTH_CODE=your_paddle_auth_code

# Email (optional)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password"""
    
    print(env_template)
    print("-" * 30)
    
    print("\n🚀 Ready to deploy! Follow the steps above to get your GPUOptimizer live!")

if __name__ == '__main__':
    main()
