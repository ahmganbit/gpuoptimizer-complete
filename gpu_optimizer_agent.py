# =============================================================================
# GPU OPTIMIZER CLIENT AGENT
# Monitors GPU usage and reports to GPUOptimizer service
# =============================================================================

import os
import json
import time
import requests
import subprocess
import psutil
from datetime import datetime
from typing import List, Dict, Optional
import logging

class GPUMonitor:
    """
    Client-side GPU monitoring agent that:
    - Monitors GPU utilization and memory usage
    - Calculates potential cost savings
    - Reports data to GPUOptimizer service
    """
    
    def __init__(self, api_key: str, server_url: str = "http://localhost:5000"):
        self.api_key = api_key
        self.server_url = server_url.rstrip('/')
        self.monitoring_interval = 300  # 5 minutes
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gpu_optimizer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_gpu_info(self) -> List[Dict]:
        """Get GPU information using nvidia-smi"""
        try:
            # Run nvidia-smi command
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, check=True)
            
            gpu_data = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    
                    if len(parts) >= 6:
                        gpu_info = {
                            'gpu_index': int(parts[0]),
                            'gpu_name': parts[1],
                            'gpu_util': float(parts[2]),
                            'mem_used': float(parts[3]),
                            'mem_total': float(parts[4]),
                            'temperature': float(parts[5]),
                            'mem_util': (float(parts[3]) / float(parts[4])) * 100,
                            'cost_per_hour': self.estimate_cost_per_hour(parts[1]),
                            'timestamp': datetime.now().isoformat()
                        }
                        gpu_data.append(gpu_info)
            
            return gpu_data
            
        except subprocess.CalledProcessError:
            self.logger.error("nvidia-smi command failed. Make sure NVIDIA drivers are installed.")
            return []
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {e}")
            return []
    
    def estimate_cost_per_hour(self, gpu_name: str) -> float:
        """Estimate cost per hour based on GPU type"""
        # Rough estimates based on AWS pricing
        cost_mapping = {
            'Tesla V100': 3.06,  # p3.2xlarge
            'Tesla K80': 0.90,   # p2.xlarge
            'Tesla T4': 0.526,   # g4dn.xlarge
            'Tesla A100': 4.10,  # p4d.xlarge
            'RTX 3090': 1.50,    # Estimated for local/cloud
            'RTX 4090': 2.00,    # Estimated for local/cloud
            'GTX 1080': 0.50,    # Estimated for local/cloud
        }
        
        # Try to match GPU name
        for gpu_type, cost in cost_mapping.items():
            if gpu_type.lower() in gpu_name.lower():
                return cost
        
        # Default estimate for unknown GPUs
        return 2.0
    
    def send_usage_data(self, gpu_data: List[Dict]) -> Dict:
        """Send GPU usage data to GPUOptimizer service"""
        try:
            payload = {
                'api_key': self.api_key,
                'gpu_data': gpu_data
            }
            
            response = requests.post(
                f"{self.server_url}/api/track-usage",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Server error: {response.status_code} - {response.text}")
                return {'error': f'Server error: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error sending data: {e}")
            return {'error': f'Network error: {e}'}
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        self.logger.info("Starting GPU monitoring cycle...")
        
        # Get GPU data
        gpu_data = self.get_gpu_info()
        
        if not gpu_data:
            self.logger.warning("No GPU data available")
            return
        
        # Log current status
        for gpu in gpu_data:
            self.logger.info(
                f"GPU {gpu['gpu_index']} ({gpu['gpu_name']}): "
                f"{gpu['gpu_util']}% util, {gpu['mem_util']:.1f}% memory, "
                f"${gpu['cost_per_hour']:.2f}/hour"
            )
        
        # Send data to server
        result = self.send_usage_data(gpu_data)
        
        if 'error' in result:
            self.logger.error(f"Failed to send data: {result['error']}")
        else:
            self.logger.info(
                f"Data sent successfully. Monthly projection: "
                f"${result.get('monthly_projection', 0):.2f} savings"
            )
    
    def start_monitoring(self):
        """Start continuous GPU monitoring"""
        self.logger.info(f"Starting GPU monitoring with API key: {self.api_key[:12]}...")
        self.logger.info(f"Reporting to: {self.server_url}")
        self.logger.info(f"Monitoring interval: {self.monitoring_interval} seconds")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.monitoring_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")

def main():
    """Main entry point for GPU monitoring agent"""
    # Get API key from environment or command line
    api_key = os.getenv('GPU_OPTIMIZER_API_KEY')
    server_url = os.getenv('GPU_OPTIMIZER_SERVER_URL', 'http://localhost:5000')
    
    if not api_key:
        print("Error: GPU_OPTIMIZER_API_KEY environment variable not set")
        print("Usage: export GPU_OPTIMIZER_API_KEY=your_api_key")
        print("       python gpu_optimizer_agent.py")
        return
    
    # Create and start monitor
    monitor = GPUMonitor(api_key, server_url)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()

