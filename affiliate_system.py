#!/usr/bin/env python3
"""
GPUOptimizer Affiliate & Referral System
Automated affiliate marketing and referral program management
"""

import os
import json
import time
import logging
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import stripe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('affiliate_system.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Affiliate:
    """Affiliate partner data structure"""
    id: str
    email: str
    name: str
    company: Optional[str]
    referral_code: str
    commission_rate: float  # Percentage
    total_referrals: int
    total_earnings: float
    status: str  # 'active', 'pending', 'suspended'
    tier: str  # 'bronze', 'silver', 'gold', 'platinum'
    payment_method: str
    payment_details: Dict[str, Any]
    created_at: datetime
    last_payout: Optional[datetime] = None

@dataclass
class Referral:
    """Referral tracking data structure"""
    id: str
    affiliate_id: str
    customer_email: str
    referral_code: str
    conversion_date: Optional[datetime]
    commission_amount: float
    status: str  # 'pending', 'converted', 'paid'
    customer_tier: str
    customer_value: float
    created_at: datetime

@dataclass
class Commission:
    """Commission payout data structure"""
    id: str
    affiliate_id: str
    amount: float
    period_start: datetime
    period_end: datetime
    referrals_count: int
    status: str  # 'pending', 'processing', 'paid', 'failed'
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime] = None

class AffiliateSystem:
    """Advanced affiliate and referral program management"""
    
    def __init__(self):
        self.db_path = "affiliate_system.db"
        self.init_database()
        
        # Commission tiers
        self.commission_tiers = {
            'bronze': {'rate': 0.20, 'min_referrals': 0},    # 20%
            'silver': {'rate': 0.25, 'min_referrals': 10},   # 25%
            'gold': {'rate': 0.30, 'min_referrals': 25},     # 30%
            'platinum': {'rate': 0.35, 'min_referrals': 50}  # 35%
        }
        
        # Customer tier values (monthly)
        self.customer_values = {
            'free': 0,
            'professional': 49,
            'enterprise': 199,
            'custom': 499
        }
        
        # Payment configuration
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.paypal_config = {
            'client_id': os.getenv('PAYPAL_CLIENT_ID'),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET'),
            'mode': os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD')
        }
        
        logging.info("Affiliate system initialized")
    
    def init_database(self):
        """Initialize affiliate database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Affiliates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliates (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            company TEXT,
            referral_code TEXT UNIQUE NOT NULL,
            commission_rate REAL NOT NULL,
            total_referrals INTEGER DEFAULT 0,
            total_earnings REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            tier TEXT DEFAULT 'bronze',
            payment_method TEXT,
            payment_details TEXT,
            created_at TEXT NOT NULL,
            last_payout TEXT
        )
        ''')
        
        # Referrals table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id TEXT PRIMARY KEY,
            affiliate_id TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            referral_code TEXT NOT NULL,
            conversion_date TEXT,
            commission_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            customer_tier TEXT,
            customer_value REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (affiliate_id) REFERENCES affiliates (id)
        )
        ''')
        
        # Commissions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id TEXT PRIMARY KEY,
            affiliate_id TEXT NOT NULL,
            amount REAL NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            referrals_count INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            transaction_id TEXT,
            created_at TEXT NOT NULL,
            paid_at TEXT,
            FOREIGN KEY (affiliate_id) REFERENCES affiliates (id)
        )
        ''')
        
        # Affiliate clicks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            affiliate_id TEXT NOT NULL,
            referral_code TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            landing_page TEXT,
            converted BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (affiliate_id) REFERENCES affiliates (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Affiliate database initialized")
    
    # =============================================================================
    # AFFILIATE MANAGEMENT
    # =============================================================================
    
    def register_affiliate(self, email: str, name: str, company: str = None, 
                          payment_method: str = 'stripe') -> Affiliate:
        """Register new affiliate partner"""
        try:
            # Generate unique referral code
            referral_code = self.generate_referral_code(name)
            
            # Ensure uniqueness
            while self.referral_code_exists(referral_code):
                referral_code = self.generate_referral_code(name)
            
            affiliate = Affiliate(
                id=str(uuid.uuid4()),
                email=email,
                name=name,
                company=company,
                referral_code=referral_code,
                commission_rate=self.commission_tiers['bronze']['rate'],
                total_referrals=0,
                total_earnings=0.0,
                status='pending',
                tier='bronze',
                payment_method=payment_method,
                payment_details={},
                created_at=datetime.now()
            )
            
            self.save_affiliate(affiliate)
            self.send_welcome_email(affiliate)
            
            logging.info(f"Registered new affiliate: {email}")
            return affiliate
            
        except Exception as e:
            logging.error(f"Affiliate registration error: {e}")
            raise
    
    def generate_referral_code(self, name: str) -> str:
        """Generate unique referral code"""
        # Clean name and take first 3 characters
        clean_name = ''.join(c for c in name if c.isalnum())[:3].upper()
        
        # Add random suffix
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"GPU{clean_name}{suffix}"
    
    def referral_code_exists(self, code: str) -> bool:
        """Check if referral code already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM affiliates WHERE referral_code = ?', (code,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_affiliate(self, affiliate: Affiliate):
        """Save affiliate to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO affiliates 
        (id, email, name, company, referral_code, commission_rate, total_referrals, 
         total_earnings, status, tier, payment_method, payment_details, created_at, last_payout)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            affiliate.id, affiliate.email, affiliate.name, affiliate.company,
            affiliate.referral_code, affiliate.commission_rate, affiliate.total_referrals,
            affiliate.total_earnings, affiliate.status, affiliate.tier,
            affiliate.payment_method, json.dumps(affiliate.payment_details),
            affiliate.created_at.isoformat(),
            affiliate.last_payout.isoformat() if affiliate.last_payout else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_affiliate_by_code(self, referral_code: str) -> Optional[Affiliate]:
        """Get affiliate by referral code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM affiliates WHERE referral_code = ?', (referral_code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self.row_to_affiliate(row)
        return None
    
    def row_to_affiliate(self, row) -> Affiliate:
        """Convert database row to Affiliate object"""
        return Affiliate(
            id=row[0],
            email=row[1],
            name=row[2],
            company=row[3],
            referral_code=row[4],
            commission_rate=row[5],
            total_referrals=row[6],
            total_earnings=row[7],
            status=row[8],
            tier=row[9],
            payment_method=row[10],
            payment_details=json.loads(row[11]) if row[11] else {},
            created_at=datetime.fromisoformat(row[12]),
            last_payout=datetime.fromisoformat(row[13]) if row[13] else None
        )
    
    # =============================================================================
    # REFERRAL TRACKING
    # =============================================================================
    
    def track_referral_click(self, referral_code: str, ip_address: str, 
                           user_agent: str, referrer: str = None, 
                           landing_page: str = None) -> bool:
        """Track affiliate referral click"""
        try:
            affiliate = self.get_affiliate_by_code(referral_code)
            if not affiliate:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO affiliate_clicks 
            (affiliate_id, referral_code, ip_address, user_agent, referrer, landing_page)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (affiliate.id, referral_code, ip_address, user_agent, referrer, landing_page))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Tracked click for affiliate {referral_code}")
            return True
            
        except Exception as e:
            logging.error(f"Click tracking error: {e}")
            return False
    
    def process_conversion(self, customer_email: str, customer_tier: str, 
                          referral_code: str = None) -> Optional[Referral]:
        """Process customer conversion from referral"""
        try:
            if not referral_code:
                # Try to find referral code from recent clicks
                referral_code = self.find_referral_code_for_customer(customer_email)
            
            if not referral_code:
                return None
            
            affiliate = self.get_affiliate_by_code(referral_code)
            if not affiliate:
                return None
            
            # Calculate commission
            customer_value = self.customer_values.get(customer_tier, 0)
            commission_amount = customer_value * affiliate.commission_rate
            
            referral = Referral(
                id=str(uuid.uuid4()),
                affiliate_id=affiliate.id,
                customer_email=customer_email,
                referral_code=referral_code,
                conversion_date=datetime.now(),
                commission_amount=commission_amount,
                status='converted',
                customer_tier=customer_tier,
                customer_value=customer_value,
                created_at=datetime.now()
            )
            
            self.save_referral(referral)
            self.update_affiliate_stats(affiliate.id, commission_amount)
            self.check_tier_upgrade(affiliate.id)
            
            logging.info(f"Processed conversion: {customer_email} -> {referral_code}")
            return referral
            
        except Exception as e:
            logging.error(f"Conversion processing error: {e}")
            return None
    
    def find_referral_code_for_customer(self, customer_email: str) -> Optional[str]:
        """Find referral code for customer based on recent activity"""
        # This would typically use cookies or session tracking
        # For now, return None
        return None
    
    def save_referral(self, referral: Referral):
        """Save referral to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO referrals 
        (id, affiliate_id, customer_email, referral_code, conversion_date, 
         commission_amount, status, customer_tier, customer_value, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            referral.id, referral.affiliate_id, referral.customer_email,
            referral.referral_code, 
            referral.conversion_date.isoformat() if referral.conversion_date else None,
            referral.commission_amount, referral.status, referral.customer_tier,
            referral.customer_value, referral.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_affiliate_stats(self, affiliate_id: str, commission_amount: float):
        """Update affiliate statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE affiliates 
        SET total_referrals = total_referrals + 1,
            total_earnings = total_earnings + ?
        WHERE id = ?
        ''', (commission_amount, affiliate_id))
        
        conn.commit()
        conn.close()
    
    def check_tier_upgrade(self, affiliate_id: str):
        """Check and upgrade affiliate tier if eligible"""
        affiliate = self.get_affiliate_by_id(affiliate_id)
        if not affiliate:
            return
        
        current_tier = affiliate.tier
        new_tier = current_tier
        
        # Check tier upgrades
        for tier, requirements in self.commission_tiers.items():
            if (affiliate.total_referrals >= requirements['min_referrals'] and
                requirements['rate'] > self.commission_tiers[current_tier]['rate']):
                new_tier = tier
        
        if new_tier != current_tier:
            self.upgrade_affiliate_tier(affiliate_id, new_tier)
            self.send_tier_upgrade_email(affiliate, new_tier)
    
    def upgrade_affiliate_tier(self, affiliate_id: str, new_tier: str):
        """Upgrade affiliate to new tier"""
        new_rate = self.commission_tiers[new_tier]['rate']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE affiliates 
        SET tier = ?, commission_rate = ?
        WHERE id = ?
        ''', (new_tier, new_rate, affiliate_id))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Upgraded affiliate {affiliate_id} to {new_tier} tier")
    
    def get_affiliate_by_id(self, affiliate_id: str) -> Optional[Affiliate]:
        """Get affiliate by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM affiliates WHERE id = ?', (affiliate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self.row_to_affiliate(row)
        return None
