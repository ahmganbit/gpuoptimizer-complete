#!/usr/bin/env python3
"""
GPUOptimizer SEO & Growth Hacking Engine
Automated SEO optimization and growth strategies
"""

import os
import json
import time
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import threading
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import hashlib
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seo_growth.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class SEOKeyword:
    """SEO keyword data structure"""
    keyword: str
    search_volume: int
    difficulty: int
    cpc: float
    competition: str
    current_rank: Optional[int] = None
    target_rank: int = 10
    content_gap: bool = False

@dataclass
class BacklinkOpportunity:
    """Backlink opportunity data structure"""
    domain: str
    url: str
    domain_authority: int
    page_authority: int
    relevance_score: int
    contact_email: Optional[str] = None
    outreach_status: str = 'pending'

class SEOGrowthEngine:
    """Advanced SEO and growth hacking automation"""
    
    def __init__(self):
        self.db_path = "seo_growth.db"
        self.init_database()
        
        # API configurations
        self.ahrefs_api_key = os.getenv('AHREFS_API_KEY')
        self.semrush_api_key = os.getenv('SEMRUSH_API_KEY')
        self.google_search_console_key = os.getenv('GOOGLE_SEARCH_CONSOLE_KEY')
        self.moz_api_key = os.getenv('MOZ_API_KEY')
        
        # Target domain
        self.domain = os.getenv('DOMAIN', 'gpuoptimizer.ai')
        
        # Primary keywords for GPU optimization niche
        self.primary_keywords = [
            'GPU cost optimization',
            'reduce GPU costs',
            'machine learning infrastructure costs',
            'AI training cost reduction',
            'CUDA optimization',
            'GPU monitoring tools',
            'cloud GPU savings',
            'ML infrastructure optimization',
            'deep learning cost optimization',
            'GPU utilization monitoring'
        ]
        
        # Long-tail keyword patterns
        self.long_tail_patterns = [
            'how to reduce {} costs',
            'best {} tools',
            '{} optimization guide',
            '{} cost calculator',
            '{} monitoring software',
            '{} best practices',
            'cheap {} alternatives',
            '{} ROI optimization'
        ]
        
        # Competitor domains
        self.competitors = [
            'run.ai',
            'cnvrg.io',
            'determined.ai',
            'weights-biases.com',
            'neptune.ai'
        ]
        
        logging.info("SEO Growth Engine initialized")
    
    def init_database(self):
        """Initialize SEO database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Keywords table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL,
            search_volume INTEGER,
            difficulty INTEGER,
            cpc REAL,
            competition TEXT,
            current_rank INTEGER,
            target_rank INTEGER,
            content_gap BOOLEAN,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Backlink opportunities table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS backlink_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            url TEXT NOT NULL,
            domain_authority INTEGER,
            page_authority INTEGER,
            relevance_score INTEGER,
            contact_email TEXT,
            outreach_status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            contacted_at TEXT,
            response_at TEXT
        )
        ''')
        
        # Content gaps table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            competitor_url TEXT,
            competitor_rank INTEGER,
            our_rank INTEGER,
            content_type TEXT,
            priority_score INTEGER,
            status TEXT DEFAULT 'identified',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # SEO metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS seo_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            organic_traffic INTEGER,
            keyword_rankings INTEGER,
            backlinks INTEGER,
            domain_authority INTEGER,
            page_speed_score INTEGER,
            core_web_vitals_score INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("SEO database initialized")
    
    # =============================================================================
    # KEYWORD RESEARCH & ANALYSIS
    # =============================================================================
    
    def research_keywords(self) -> List[SEOKeyword]:
        """Research and analyze keywords for GPU optimization niche"""
        keywords = []
        
        # Generate long-tail variations
        for primary in self.primary_keywords:
            for pattern in self.long_tail_patterns:
                long_tail = pattern.format(primary.lower())
                keywords.append(long_tail)
        
        # Add primary keywords
        keywords.extend(self.primary_keywords)
        
        # Analyze each keyword
        analyzed_keywords = []
        for keyword in keywords:
            seo_keyword = self.analyze_keyword(keyword)
            if seo_keyword:
                analyzed_keywords.append(seo_keyword)
                self.save_keyword(seo_keyword)
        
        logging.info(f"Researched {len(analyzed_keywords)} keywords")
        return analyzed_keywords
    
    def analyze_keyword(self, keyword: str) -> Optional[SEOKeyword]:
        """Analyze individual keyword metrics"""
        try:
            # Try to get data from multiple sources
            search_volume = self.get_search_volume(keyword)
            difficulty = self.get_keyword_difficulty(keyword)
            cpc = self.get_keyword_cpc(keyword)
            competition = self.get_competition_level(keyword)
            current_rank = self.get_current_rank(keyword)
            
            return SEOKeyword(
                keyword=keyword,
                search_volume=search_volume,
                difficulty=difficulty,
                cpc=cpc,
                competition=competition,
                current_rank=current_rank,
                target_rank=10,
                content_gap=current_rank is None or current_rank > 20
            )
            
        except Exception as e:
            logging.error(f"Keyword analysis error for '{keyword}': {e}")
            return None
    
    def get_search_volume(self, keyword: str) -> int:
        """Get search volume for keyword"""
        try:
            # Try SEMrush API first
            if self.semrush_api_key:
                url = f"https://api.semrush.com/"
                params = {
                    'type': 'phrase_this',
                    'key': self.semrush_api_key,
                    'phrase': keyword,
                    'database': 'us'
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.text.split('\n')[1].split(';')
                    return int(data[1]) if len(data) > 1 else 0
            
            # Fallback to estimated volume based on keyword characteristics
            return self.estimate_search_volume(keyword)
            
        except Exception as e:
            logging.error(f"Search volume error for '{keyword}': {e}")
            return self.estimate_search_volume(keyword)
    
    def estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword characteristics"""
        base_volume = 1000
        
        # Adjust based on keyword length
        words = len(keyword.split())
        if words == 1:
            base_volume *= 5
        elif words == 2:
            base_volume *= 3
        elif words >= 4:
            base_volume *= 0.5
        
        # Adjust based on keyword type
        if 'gpu' in keyword.lower():
            base_volume *= 2
        if 'cost' in keyword.lower():
            base_volume *= 1.5
        if 'optimization' in keyword.lower():
            base_volume *= 1.2
        if 'how to' in keyword.lower():
            base_volume *= 0.8
        
        return int(base_volume * random.uniform(0.5, 1.5))
    
    def get_keyword_difficulty(self, keyword: str) -> int:
        """Get keyword difficulty score"""
        try:
            # Estimate difficulty based on competition and keyword characteristics
            difficulty = 50  # Base difficulty
            
            # Adjust based on keyword length
            words = len(keyword.split())
            if words >= 4:
                difficulty -= 10  # Long-tail keywords are easier
            elif words == 1:
                difficulty += 20  # Single words are harder
            
            # Adjust based on commercial intent
            commercial_terms = ['cost', 'price', 'cheap', 'best', 'tool', 'software']
            if any(term in keyword.lower() for term in commercial_terms):
                difficulty += 15
            
            # Adjust based on technical terms
            technical_terms = ['gpu', 'cuda', 'optimization', 'monitoring']
            if any(term in keyword.lower() for term in technical_terms):
                difficulty += 10  # Technical terms are more competitive
            
            return min(max(difficulty, 1), 100)
            
        except Exception as e:
            logging.error(f"Keyword difficulty error for '{keyword}': {e}")
            return 50
    
    def get_keyword_cpc(self, keyword: str) -> float:
        """Get estimated cost per click"""
        try:
            # Estimate CPC based on keyword characteristics
            base_cpc = 2.0
            
            # B2B keywords typically have higher CPC
            if any(term in keyword.lower() for term in ['enterprise', 'business', 'professional']):
                base_cpc *= 2
            
            # Technical keywords have moderate CPC
            if any(term in keyword.lower() for term in ['gpu', 'optimization', 'monitoring']):
                base_cpc *= 1.5
            
            # Cost-related keywords have higher CPC
            if any(term in keyword.lower() for term in ['cost', 'price', 'savings']):
                base_cpc *= 1.8
            
            return round(base_cpc * random.uniform(0.7, 1.3), 2)
            
        except Exception as e:
            logging.error(f"CPC estimation error for '{keyword}': {e}")
            return 2.0
    
    def get_competition_level(self, keyword: str) -> str:
        """Get competition level for keyword"""
        try:
            # Estimate competition based on keyword characteristics
            score = 0
            
            # Check for commercial intent
            if any(term in keyword.lower() for term in ['best', 'top', 'tool', 'software']):
                score += 2
            
            # Check for high-value terms
            if any(term in keyword.lower() for term in ['enterprise', 'professional', 'cost']):
                score += 2
            
            # Check for technical complexity
            if any(term in keyword.lower() for term in ['gpu', 'cuda', 'optimization']):
                score += 1
            
            if score >= 4:
                return 'high'
            elif score >= 2:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logging.error(f"Competition analysis error for '{keyword}': {e}")
            return 'medium'
    
    def get_current_rank(self, keyword: str) -> Optional[int]:
        """Get current ranking for keyword"""
        try:
            # This would typically use Google Search Console API
            # For now, return None (not ranking) for most keywords
            return None
            
        except Exception as e:
            logging.error(f"Rank checking error for '{keyword}': {e}")
            return None
    
    # =============================================================================
    # COMPETITOR ANALYSIS
    # =============================================================================
    
    def analyze_competitors(self) -> Dict[str, Any]:
        """Analyze competitor SEO strategies"""
        competitor_analysis = {}
        
        for competitor in self.competitors:
            analysis = self.analyze_competitor_domain(competitor)
            competitor_analysis[competitor] = analysis
        
        logging.info(f"Analyzed {len(competitor_analysis)} competitors")
        return competitor_analysis
    
    def analyze_competitor_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze individual competitor domain"""
        try:
            analysis = {
                'domain': domain,
                'estimated_traffic': self.estimate_competitor_traffic(domain),
                'top_keywords': self.get_competitor_keywords(domain),
                'backlink_profile': self.analyze_competitor_backlinks(domain),
                'content_gaps': self.find_content_gaps(domain),
                'technical_seo': self.analyze_technical_seo(domain)
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Competitor analysis error for {domain}: {e}")
            return {'domain': domain, 'error': str(e)}
    
    def estimate_competitor_traffic(self, domain: str) -> int:
        """Estimate competitor organic traffic"""
        try:
            # This would typically use SEMrush or Ahrefs API
            # For now, return estimated values based on domain
            traffic_estimates = {
                'run.ai': 50000,
                'cnvrg.io': 25000,
                'determined.ai': 30000,
                'weights-biases.com': 100000,
                'neptune.ai': 40000
            }
            
            return traffic_estimates.get(domain, 20000)
            
        except Exception as e:
            logging.error(f"Traffic estimation error for {domain}: {e}")
            return 0
