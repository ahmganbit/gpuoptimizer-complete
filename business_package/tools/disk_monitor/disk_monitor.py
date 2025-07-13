#!/usr/bin/env python3
"""
Professional Disk Space Monitor
Enterprise-grade disk space monitoring with email alerts and HTML reports

Author: Professional Automation Tools
Version: 2.0.0
License: Commercial
"""

import os
import sys
import json
import time
import smtplib
import logging
import platform
import threading
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import psutil
import schedule
from typing import Dict, List, Optional, Tuple
import argparse
import hashlib
import sqlite3
from dataclasses import dataclass, asdict
import webbrowser
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disk_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DriveInfo:
    """Data class for drive information"""
    device: str
    mountpoint: str
    total: int
    used: int
    free: int
    percent: float
    threshold: float
    status: str
    last_check: datetime

@dataclass
class AlertConfig:
    """Email alert configuration"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    to_emails: List[str]
    subject_prefix: str

class DiskMonitorDatabase:
    """SQLite database for storing monitoring history"""
    
    def __init__(self, db_path: str = "disk_monitor.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drive_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device TEXT NOT NULL,
                    mountpoint TEXT NOT NULL,
                    total_gb REAL,
                    used_gb REAL,
                    free_gb REAL,
                    percent_used REAL,
                    threshold REAL,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def log_check(self, drive_info: DriveInfo):
        """Log drive check results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO drive_checks 
                (device, mountpoint, total_gb, used_gb, free_gb, percent_used, threshold, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                drive_info.device,
                drive_info.mountpoint,
                drive_info.total / (1024**3),
                drive_info.used / (1024**3),
                drive_info.free / (1024**3),
                drive_info.percent,
                drive_info.threshold,
                drive_info.status
            ))
            conn.commit()
    
    def log_alert(self, device: str, alert_type: str, message: str):
        """Log alert events"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (device, alert_type, message)
                VALUES (?, ?, ?)
            """, (device, alert_type, message))
            conn.commit()

class EmailNotifier:
    """Professional email notification system"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.last_alert_time = {}  # Prevent spam
    
    def send_alert(self, subject: str, body: str, drive_info: DriveInfo) -> bool:
        """Send email alert with rate limiting"""
        current_time = datetime.now()
        device_key = drive_info.device
        
        # Rate limiting: max 1 alert per hour per device
        if device_key in self.last_alert_time:
            time_diff = current_time - self.last_alert_time[device_key]
            if time_diff.total_seconds() < 3600:  # 1 hour
                logger.info(f"Rate limiting alert for {device_key}")
                return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email
            msg['To'] = ', '.join(self.config.to_emails)
            msg['Subject'] = f"{self.config.subject_prefix} {subject}"
            
            # Create professional HTML email
            html_body = self._create_html_email(body, drive_info)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
            
            self.last_alert_time[device_key] = current_time
            logger.info(f"Alert sent successfully for {device_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _create_html_email(self, body: str, drive_info: DriveInfo) -> str:
        """Create professional HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; }}
                .drive-info {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .status-critical {{ color: #dc3545; font-weight: bold; }}
                .status-warning {{ color: #ffc107; font-weight: bold; }}
                .status-ok {{ color: #28a745; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="alert">
                <h2>🚨 Disk Space Alert</h2>
                <p>{body}</p>
            </div>
            
            <div class="drive-info">
                <h3>Drive Information</h3>
                <p><strong>Device:</strong> {drive_info.device}</p>
                <p><strong>Mount Point:</strong> {drive_info.mountpoint}</p>
                <p><strong>Total Space:</strong> {drive_info.total / (1024**3):.2f} GB</p>
                <p><strong>Used Space:</strong> {drive_info.used / (1024**3):.2f} GB</p>
                <p><strong>Free Space:</strong> {drive_info.free / (1024**3):.2f} GB</p>
                <p><strong>Usage:</strong> <span class="status-{drive_info.status.lower()}">{drive_info.percent:.1f}%</span></p>
                <p><strong>Threshold:</strong> {drive_info.threshold}%</p>
            </div>
            
            <p><em>This alert was generated by Professional Disk Space Monitor v2.0.0</em></p>
        </body>
        </html>
        """

class HTMLReportGenerator:
    """Generate professional HTML reports"""
    
    def __init__(self, db: DiskMonitorDatabase):
        self.db = db
    
    def generate_report(self, output_path: str = "disk_report.html"):
        """Generate comprehensive HTML report"""
        with sqlite3.connect(self.db.db_path) as conn:
            # Get latest drive status
            latest_data = conn.execute("""
                SELECT device, mountpoint, total_gb, used_gb, free_gb, percent_used, threshold, status, timestamp
                FROM drive_checks 
                WHERE timestamp = (SELECT MAX(timestamp) FROM drive_checks WHERE device = drive_checks.device)
                ORDER BY percent_used DESC
            """).fetchall()
            
            # Get alert history
            alerts = conn.execute("""
                SELECT device, alert_type, message, timestamp
                FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT 50
            """).fetchall()
        
        html_content = self._create_html_template(latest_data, alerts)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path
    
    def _create_html_template(self, drive_data, alerts):
        """Create professional HTML template"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate summary statistics
        total_drives = len(drive_data)
        critical_drives = sum(1 for row in drive_data if row[7] == 'CRITICAL')
        warning_drives = sum(1 for row in drive_data if row[7] == 'WARNING')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Disk Space Monitor Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .drive-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                .drive-table th, .drive-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                .drive-table th {{ background-color: #f8f9fa; font-weight: bold; }}
                .status-critical {{ color: #dc3545; font-weight: bold; }}
                .status-warning {{ color: #ffc107; font-weight: bold; }}
                .status-ok {{ color: #28a745; font-weight: bold; }}
                .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }}
                .progress-fill {{ height: 100%; transition: width 0.3s ease; }}
                .progress-critical {{ background-color: #dc3545; }}
                .progress-warning {{ background-color: #ffc107; }}
                .progress-ok {{ background-color: #28a745; }}
                .alerts-section {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; }}
                .alert-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💾 Disk Space Monitor Report</h1>
                    <p>Generated on {current_time}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>{total_drives}</h3>
                        <p>Total Drives</p>
                    </div>
                    <div class="summary-card">
                        <h3>{critical_drives}</h3>
                        <p>Critical</p>
                    </div>
                    <div class="summary-card">
                        <h3>{warning_drives}</h3>
                        <p>Warning</p>
                    </div>
                    <div class="summary-card">
                        <h3>{total_drives - critical_drives - warning_drives}</h3>
                        <p>Healthy</p>
                    </div>
                </div>
                
                <h2>Drive Status</h2>
                <table class="drive-table">
                    <thead>
                        <tr>
                            <th>Device</th>
                            <th>Mount Point</th>
                            <th>Total (GB)</th>
                            <th>Used (GB)</th>
                            <th>Free (GB)</th>
                            <th>Usage</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_drive_rows(drive_data)}
                    </tbody>
                </table>
                
                <div class="alerts-section">
                    <h2>Recent Alerts</h2>
                    {self._generate_alert_items(alerts)}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_drive_rows(self, drive_data):
        """Generate table rows for drive data"""
        rows = ""
        for row in drive_data:
            device, mountpoint, total_gb, used_gb, free_gb, percent_used, threshold, status, timestamp = row
            progress_class = f"progress-{status.lower()}"
            status_class = f"status-{status.lower()}"
            
            rows += f"""
            <tr>
                <td>{device}</td>
                <td>{mountpoint}</td>
                <td>{total_gb:.2f}</td>
                <td>{used_gb:.2f}</td>
                <td>{free_gb:.2f}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill {progress_class}" style="width: {percent_used}%"></div>
                    </div>
                    <span class="{status_class}">{percent_used:.1f}%</span>
                </td>
                <td><span class="{status_class}">{status}</span></td>
            </tr>
            """
        return rows
    
    def _generate_alert_items(self, alerts):
        """Generate alert items"""
        if not alerts:
            return "<p>No recent alerts</p>"
        
        items = ""
        for alert in alerts:
            device, alert_type, message, timestamp = alert
            items += f"""
            <div class="alert-item">
                <strong>{alert_type}</strong> - {device}<br>
                <small>{timestamp}</small><br>
                {message}
            </div>
            """
        return items

class ProfessionalDiskMonitor:
    """Main disk monitoring class"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.db = DiskMonitorDatabase()
        self.notifier = EmailNotifier(AlertConfig(**self.config['email']))
        self.report_generator = HTMLReportGenerator(self.db)
        self.running = False
        self.monitoring_thread = None
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def get_drive_info(self, mountpoint: str, threshold: float) -> DriveInfo:
        """Get detailed drive information"""
        try:
            usage = psutil.disk_usage(mountpoint)
            
            # Determine status based on threshold
            if usage.percent >= threshold:
                status = "CRITICAL"
            elif usage.percent >= threshold * 0.8:  # 80% of threshold
                status = "WARNING"
            else:
                status = "OK"
            
            return DriveInfo(
                device=psutil.disk_partitions()[0].device if psutil.disk_partitions() else "Unknown",
                mountpoint=mountpoint,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
                threshold=threshold,
                status=status,
                last_check=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting drive info for {mountpoint}: {e}")
            return None
    
    def check_drives(self):
        """Check all configured drives"""
        logger.info("Starting drive space check...")
        
        for drive_config in self.config['drives']:
            mountpoint = drive_config['mountpoint']
            threshold = drive_config['threshold']
            
            drive_info = self.get_drive_info(mountpoint, threshold)
            if drive_info:
                # Log to database
                self.db.log_check(drive_info)
                
                # Check if alert is needed
                if drive_info.status in ['WARNING', 'CRITICAL']:
                    self._send_alert(drive_info)
                
                logger.info(f"Drive {mountpoint}: {drive_info.percent:.1f}% used ({drive_info.status})")
    
    def _send_alert(self, drive_info: DriveInfo):
        """Send alert for drive issues"""
        if drive_info.status == 'CRITICAL':
            subject = f"CRITICAL: Disk space alert for {drive_info.mountpoint}"
            body = f"Critical disk space alert! Drive {drive_info.mountpoint} is {drive_info.percent:.1f}% full (threshold: {drive_info.threshold}%)."
        else:
            subject = f"WARNING: Disk space alert for {drive_info.mountpoint}"
            body = f"Warning: Drive {drive_info.mountpoint} is {drive_info.percent:.1f}% full (threshold: {drive_info.threshold}%)."
        
        if self.notifier.send_alert(subject, body, drive_info):
            self.db.log_alert(drive_info.device, drive_info.status, body)
    
    def generate_report(self, open_browser: bool = True):
        """Generate and optionally open HTML report"""
        report_path = self.report_generator.generate_report()
        
        if open_browser:
            try:
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
                logger.info("Report opened in browser")
            except Exception as e:
                logger.error(f"Could not open report in browser: {e}")
        
        return report_path
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.running:
            logger.warning("Monitoring is already running")
            return
        
        self.running = True
        interval_minutes = self.config.get('check_interval_minutes', 15)
        
        logger.info(f"Starting continuous monitoring (check every {interval_minutes} minutes)")
        
        # Schedule the monitoring job
        schedule.every(interval_minutes).minutes.do(self.check_drives)
        
        # Run initial check
        self.check_drives()
        
        # Start monitoring loop
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        logger.info("Monitoring stopped")
    
    def run_once(self):
        """Run a single check"""
        self.check_drives()
        self.generate_report()

def create_default_config():
    """Create default configuration file"""
    default_config = {
        "check_interval_minutes": 15,
        "drives": [
            {
                "mountpoint": "/",
                "threshold": 90.0
            },
            {
                "mountpoint": "/home",
                "threshold": 85.0
            }
        ],
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "from_email": "your-email@gmail.com",
            "to_emails": ["admin@company.com"],
            "subject_prefix": "[Disk Monitor]"
        }
    }
    
    with open("config.json", 'w') as f:
        json.dump(default_config, f, indent=4)
    
    print("Default configuration file 'config.json' created.")
    print("Please edit the configuration file with your settings before running.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Professional Disk Space Monitor")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--once", action="store_true", help="Run single check and exit")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument("--init", action="store_true", help="Create default configuration")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon/service")
    
    args = parser.parse_args()
    
    if args.init:
        create_default_config()
        return
    
    if not os.path.exists(args.config):
        print(f"Configuration file {args.config} not found. Use --init to create default config.")
        return
    
    monitor = ProfessionalDiskMonitor(args.config)
    
    if args.report:
        monitor.generate_report()
    elif args.once:
        monitor.run_once()
    elif args.daemon:
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    else:
        # Interactive mode
        print("Professional Disk Space Monitor v2.0.0")
        print("1. Run single check")
        print("2. Generate report")
        print("3. Start continuous monitoring")
        print("4. Exit")
        
        choice = input("Select option (1-4): ")
        
        if choice == "1":
            monitor.run_once()
        elif choice == "2":
            monitor.generate_report()
        elif choice == "3":
            try:
                monitor.start_monitoring()
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        else:
            print("Exiting...")

if __name__ == "__main__":
    main() 