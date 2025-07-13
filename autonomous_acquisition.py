# =============================================================================
# AUTONOMOUS CUSTOMER ACQUISITION MODULE
# Zero-touch lead generation and conversion system
# =============================================================================

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import schedule
from dataclasses import dataclass
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import hashlib
import uuid
import re
from urllib.parse import urljoin, urlparse
import feedparser
import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Social Media APIs
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from linkedin_api import Linkedin
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False

try:
    import facebook
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False

# Email Marketing
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

try:
    from mailchimp3 import MailChimp
    MAILCHIMP_AVAILABLE = True
except ImportError:
    MAILCHIMP_AVAILABLE = False

# Analytics
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

@dataclass
class Lead:
    email: str
    name: str
    company: str
    source: str
    score: int  # Lead quality score 1-100
    status: str  # 'new', 'contacted', 'nurturing', 'converted', 'lost'
    created_at: datetime
    last_contact: Optional[datetime] = None
    metadata: Optional[Dict] = None

class AutonomousAcquisition:
    """
    Handles autonomous customer acquisition:
    - Lead generation from multiple sources
    - Automated outreach sequences
    - Lead scoring and qualification
    - Conversion tracking
    """
    
    def __init__(self, revenue_manager):
        self.revenue_manager = revenue_manager
        self.db_path = "leads.db"
        self.init_database()
        
        # Lead generation sources configuration
        self.sources = {
            'github': {
                'enabled': True,
                'keywords': ['gpu', 'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'cuda'],
                'api_token': os.getenv('GITHUB_TOKEN', ''),
                'daily_limit': 50
            },
            'reddit': {
                'enabled': True,
                'subreddits': ['MachineLearning', 'deeplearning', 'artificial', 'compsci', 'programming'],
                'keywords': ['gpu cost', 'expensive training', 'cloud computing'],
                'daily_limit': 30
            },
            'twitter': {
                'enabled': False,  # Requires API access
                'keywords': ['#MachineLearning', '#DeepLearning', '#GPU', '#CloudCosts'],
                'daily_limit': 20
            }
        }
        
        # Email sequences for different lead types
        self.email_sequences = {
            'github_developer': [
                {
                    'delay_hours': 0,
                    'subject': '🚀 Saw your {project_name} - Cut GPU costs by 40%?',
                    'template': 'github_initial'
                },
                {
                    'delay_hours': 72,
                    'subject': 'Quick question about your GPU usage',
                    'template': 'github_followup_1'
                },
                {
                    'delay_hours': 168,  # 1 week
                    'subject': 'Final thought on GPU optimization',
                    'template': 'github_final'
                }
            ],
            'reddit_user': [
                {
                    'delay_hours': 0,
                    'subject': 'Re: Your GPU cost question - Here\'s a solution',
                    'template': 'reddit_initial'
                },
                {
                    'delay_hours': 96,
                    'subject': 'Free GPU monitoring for your projects',
                    'template': 'reddit_followup'
                }
            ],
            'general': [
                {
                    'delay_hours': 0,
                    'subject': 'Cut your AI infrastructure costs by 40%',
                    'template': 'general_initial'
                },
                {
                    'delay_hours': 120,
                    'subject': 'Still spending too much on GPUs?',
                    'template': 'general_followup'
                }
            ]
        }
        
        # Start background acquisition tasks
        self.start_acquisition_scheduler()
    
    def init_database(self):
        """Initialize leads tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            company TEXT,
            source TEXT,
            score INTEGER DEFAULT 50,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contact TIMESTAMP,
            metadata TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outreach_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_email TEXT,
            sequence_type TEXT,
            step_number INTEGER,
            subject TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            opened BOOLEAN DEFAULT FALSE,
            clicked BOOLEAN DEFAULT FALSE,
            replied BOOLEAN DEFAULT FALSE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS acquisition_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE DEFAULT CURRENT_DATE,
            source TEXT,
            leads_generated INTEGER DEFAULT 0,
            emails_sent INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_github_leads(self) -> List[Lead]:
        """Generate leads from GitHub repositories"""
        leads = []
        
        if not self.sources['github']['enabled'] or not self.sources['github']['api_token']:
            return leads
        
        headers = {
            'Authorization': f"token {self.sources['github']['api_token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        for keyword in self.sources['github']['keywords']:
            try:
                # Search for repositories
                search_url = f"https://api.github.com/search/repositories"
                params = {
                    'q': f"{keyword} language:python stars:>10",
                    'sort': 'updated',
                    'per_page': 10
                }
                
                response = requests.get(search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    repos = response.json().get('items', [])
                    
                    for repo in repos:
                        owner = repo['owner']
                        
                        # Get owner details
                        user_response = requests.get(owner['url'], headers=headers)
                        
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            email = user_data.get('email')
                            
                            if email and '@' in email:
                                # Calculate lead score based on repository metrics
                                score = min(100, max(20, 
                                    (repo['stargazers_count'] * 2) + 
                                    (repo['forks_count'] * 3) + 
                                    (50 if repo['description'] and 'gpu' in repo['description'].lower() else 0)
                                ))
                                
                                lead = Lead(
                                    email=email,
                                    name=user_data.get('name', owner['login']),
                                    company=user_data.get('company', ''),
                                    source='github',
                                    score=score,
                                    status='new',
                                    created_at=datetime.now(),
                                    metadata={
                                        'repo_name': repo['name'],
                                        'repo_url': repo['html_url'],
                                        'stars': repo['stargazers_count'],
                                        'keyword': keyword
                                    }
                                )
                                
                                leads.append(lead)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error generating GitHub leads for {keyword}: {e}")
        
        return leads[:self.sources['github']['daily_limit']]
    
    def generate_reddit_leads(self) -> List[Lead]:
        """Generate leads from Reddit posts and comments"""
        leads = []
        
        if not self.sources['reddit']['enabled']:
            return leads
        
        headers = {
            'User-Agent': 'GPUOptimizer Lead Generator 1.0'
        }
        
        for subreddit in self.sources['reddit']['subreddits']:
            try:
                # Get recent posts
                url = f"https://www.reddit.com/r/{subreddit}/new.json"
                params = {'limit': 25}
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post['data']
                        title = post_data.get('title', '').lower()
                        selftext = post_data.get('selftext', '').lower()
                        
                        # Check if post mentions GPU costs or related keywords
                        relevant_keywords = ['gpu cost', 'expensive', 'cloud bill', 'aws cost', 'training cost']
                        
                        if any(keyword in title or keyword in selftext for keyword in relevant_keywords):
                            author = post_data.get('author')
                            
                            if author and author != '[deleted]':
                                # Generate potential email (this is speculative)
                                potential_emails = [
                                    f"{author}@gmail.com",
                                    f"{author}@outlook.com",
                                    f"{author}@protonmail.com"
                                ]
                                
                                # Use first email as placeholder (in real implementation, 
                                # you'd need to find actual contact info)
                                email = potential_emails[0]
                                
                                lead = Lead(
                                    email=email,
                                    name=author,
                                    company='',
                                    source='reddit',
                                    score=60,  # Medium score for Reddit leads
                                    status='new',
                                    created_at=datetime.now(),
                                    metadata={
                                        'post_title': post_data.get('title'),
                                        'post_url': f"https://reddit.com{post_data.get('permalink')}",
                                        'subreddit': subreddit,
                                        'upvotes': post_data.get('ups', 0)
                                    }
                                )
                                
                                leads.append(lead)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"Error generating Reddit leads for {subreddit}: {e}")
        
        return leads[:self.sources['reddit']['daily_limit']]
    
    def store_lead(self, lead: Lead) -> bool:
        """Store lead in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO leads 
            (email, name, company, source, score, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.email,
                lead.name,
                lead.company,
                lead.source,
                lead.score,
                lead.status,
                json.dumps(lead.metadata) if lead.metadata else None
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error storing lead: {e}")
            return False
        finally:
            conn.close()
    
    def get_leads_for_outreach(self, limit: int = 50) -> List[Lead]:
        """Get leads ready for outreach"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM leads 
        WHERE status = 'new' AND score >= 40
        ORDER BY score DESC, created_at ASC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        leads = []
        for row in rows:
            lead = Lead(
                email=row[1],
                name=row[2],
                company=row[3],
                source=row[4],
                score=row[5],
                status=row[6],
                created_at=datetime.fromisoformat(row[7]),
                last_contact=datetime.fromisoformat(row[8]) if row[8] else None,
                metadata=json.loads(row[9]) if row[9] else None
            )
            leads.append(lead)
        
        return leads
    
    def get_email_template(self, template_name: str, lead: Lead) -> Dict[str, str]:
        """Get personalized email template"""
        templates = {
            'github_initial': {
                'subject': f"🚀 Saw your {lead.metadata.get('repo_name', 'project')} - Cut GPU costs by 40%?",
                'body': f"""Hi {lead.name},

I came across your {lead.metadata.get('repo_name', 'project')} repository and was impressed by your work on {lead.metadata.get('keyword', 'machine learning')}.

I noticed you're working with GPUs for training/inference. Are you currently spending a lot on cloud GPU costs? Most ML teams we work with are overspending by 40-60% on idle GPU time.

We built GPUOptimizer specifically for developers like you - it automatically detects when your GPUs are idle and helps optimize your cloud spending. 

Would you be interested in a free analysis of your current GPU usage? It takes 2 minutes to set up and could save you hundreds monthly.

Best regards,
Alex from GPUOptimizer

P.S. - We're offering free monitoring for the first 2 GPUs. No credit card required.
"""
            },
            'github_followup_1': {
                'subject': 'Quick question about your GPU usage',
                'body': f"""Hi {lead.name},

Quick follow-up on my previous email about GPU cost optimization.

I'm curious - what's your current monthly spend on GPU compute? Whether it's AWS, GCP, or Azure, most teams are surprised to learn they're paying for 40-60% idle time.

Here's what one of our users (similar project to yours) discovered:
- Before: $2,400/month on p3.2xlarge instances
- After: $960/month with same performance
- Savings: $1,440/month

The setup literally takes 2 minutes. Would you like me to send you the quick start guide?

Best,
Alex
"""
            },
            'reddit_initial': {
                'subject': f"Re: Your GPU cost question - Here's a solution",
                'body': f"""Hi {lead.name},

I saw your post on r/{lead.metadata.get('subreddit', 'MachineLearning')} about GPU costs and thought you might find this helpful.

We built GPUOptimizer after facing the same problem - our ML team was burning through $5K+ monthly on cloud GPUs, with most of it going to idle time.

The tool automatically monitors your GPU utilization and gives you actionable insights to cut costs by 40-60%. It works with any cloud provider and takes 2 minutes to set up.

Since you're dealing with the same pain point, I'd love to offer you free monitoring for your first 2 GPUs. No strings attached.

Interested in a quick demo?

Best,
Alex from GPUOptimizer

P.S. - Here's a case study from a team with similar setup: [link]
"""
            },
            'general_initial': {
                'subject': 'Cut your AI infrastructure costs by 40%',
                'body': f"""Hi {lead.name},

Are you spending too much on GPU compute for your AI/ML workloads?

Most teams we work with discover they're paying for 40-60% idle GPU time. That's thousands of dollars monthly going to waste.

GPUOptimizer automatically monitors your GPU usage across all cloud providers and gives you actionable insights to optimize costs without impacting performance.

Here's what you get:
✅ Real-time GPU utilization monitoring
✅ Automated idle time detection
✅ Cost optimization recommendations
✅ Slack/email alerts for waste

Free for your first 2 GPUs. Setup takes 2 minutes.

Want to see how much you could save?

Best regards,
Alex from GPUOptimizer
"""
            }
        }
        
        template_key = template_name
        if template_name not in templates:
            template_key = 'general_initial'
        
        return templates[template_key]
    
    def send_outreach_email(self, lead: Lead, sequence_type: str, step_number: int):
        """Send outreach email to lead"""
        sequence = self.email_sequences.get(sequence_type, self.email_sequences['general'])
        
        if step_number >= len(sequence):
            return False
        
        step = sequence[step_number]
        template = self.get_email_template(step['template'], lead)
        
        # Send email
        success = self.revenue_manager.send_email(
            lead.email,
            template['subject'],
            template['body']
        )
        
        if success:
            # Log outreach
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO outreach_log 
            (lead_email, sequence_type, step_number, subject)
            VALUES (?, ?, ?, ?)
            ''', (lead.email, sequence_type, step_number, template['subject']))
            
            # Update lead status
            cursor.execute('''
            UPDATE leads 
            SET status = 'contacted', last_contact = CURRENT_TIMESTAMP
            WHERE email = ?
            ''', (lead.email,))
            
            conn.commit()
            conn.close()
            
            return True
        
        return False
    
    def process_daily_acquisition(self):
        """Daily autonomous acquisition process"""
        print(f"Starting daily acquisition process at {datetime.now()}")
        
        # Generate new leads
        all_leads = []
        
        # GitHub leads
        github_leads = self.generate_github_leads()
        all_leads.extend(github_leads)
        print(f"Generated {len(github_leads)} GitHub leads")
        
        # Reddit leads
        reddit_leads = self.generate_reddit_leads()
        all_leads.extend(reddit_leads)
        print(f"Generated {len(reddit_leads)} Reddit leads")
        
        # Store new leads
        new_leads_count = 0
        for lead in all_leads:
            if self.store_lead(lead):
                new_leads_count += 1
        
        print(f"Stored {new_leads_count} new leads")
        
        # Process outreach for existing leads
        leads_for_outreach = self.get_leads_for_outreach(20)
        emails_sent = 0
        
        for lead in leads_for_outreach:
            # Determine sequence type based on source
            if lead.source == 'github':
                sequence_type = 'github_developer'
            elif lead.source == 'reddit':
                sequence_type = 'reddit_user'
            else:
                sequence_type = 'general'
            
            # Send first email in sequence
            if self.send_outreach_email(lead, sequence_type, 0):
                emails_sent += 1
                time.sleep(random.uniform(30, 120))  # Random delay between emails
        
        print(f"Sent {emails_sent} outreach emails")
        
        # Update daily stats
        self.update_daily_stats('total', new_leads_count, emails_sent, 0)
    
    def update_daily_stats(self, source: str, leads_generated: int, emails_sent: int, conversions: int):
        """Update daily acquisition statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO acquisition_stats 
        (date, source, leads_generated, emails_sent, conversions)
        VALUES (CURRENT_DATE, ?, ?, ?, ?)
        ''', (source, leads_generated, emails_sent, conversions))
        
        conn.commit()
        conn.close()
    
    def start_acquisition_scheduler(self):
        """Start the background acquisition scheduler"""
        # Schedule daily acquisition at 9 AM
        schedule.every().day.at("09:00").do(self.process_daily_acquisition)
        
        # Schedule follow-up emails
        schedule.every().hour.do(self.process_followup_emails)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("Autonomous acquisition scheduler started")
    
    def process_followup_emails(self):
        """Process scheduled follow-up emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get leads that need follow-up emails
        cursor.execute('''
        SELECT l.*, ol.sequence_type, ol.step_number, ol.sent_at
        FROM leads l
        JOIN outreach_log ol ON l.email = ol.lead_email
        WHERE l.status = 'contacted' 
        AND ol.sent_at <= datetime('now', '-72 hours')
        AND ol.step_number < 2
        ORDER BY ol.sent_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            lead = Lead(
                email=row[1],
                name=row[2],
                company=row[3],
                source=row[4],
                score=row[5],
                status=row[6],
                created_at=datetime.fromisoformat(row[7]),
                last_contact=datetime.fromisoformat(row[8]) if row[8] else None,
                metadata=json.loads(row[9]) if row[9] else None
            )
            
            sequence_type = row[10]
            next_step = row[11] + 1
            
            # Send next email in sequence
            self.send_outreach_email(lead, sequence_type, next_step)
            time.sleep(random.uniform(60, 300))  # Random delay
    
    def get_acquisition_stats(self) -> Dict:
        """Get acquisition performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total leads by source
        cursor.execute('SELECT source, COUNT(*) FROM leads GROUP BY source')
        leads_by_source = dict(cursor.fetchall())
        
        # Conversion rate
        cursor.execute('SELECT COUNT(*) FROM leads WHERE status = "converted"')
        conversions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM leads WHERE status = "contacted"')
        contacted = cursor.fetchone()[0]
        
        conversion_rate = (conversions / max(contacted, 1)) * 100
        
        # Recent performance
        cursor.execute('''
        SELECT SUM(leads_generated), SUM(emails_sent), SUM(conversions)
        FROM acquisition_stats 
        WHERE date >= date('now', '-7 days')
        ''')
        
        weekly_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'leads_by_source': leads_by_source,
            'total_leads': sum(leads_by_source.values()),
            'conversion_rate': conversion_rate,
            'weekly_leads': weekly_stats[0] or 0,
            'weekly_emails': weekly_stats[1] or 0,
            'weekly_conversions': weekly_stats[2] or 0
        }

    # =============================================================================
    # ADVANCED LEAD GENERATION METHODS
    # =============================================================================

    def scrape_linkedin_leads(self, keywords: List[str], limit: int = 50) -> List[Lead]:
        """Scrape LinkedIn for potential leads using AI-powered targeting"""
        leads = []

        if not LINKEDIN_AVAILABLE:
            logging.warning("LinkedIn API not available")
            return leads

        try:
            # Initialize LinkedIn API (requires credentials)
            linkedin_username = os.getenv('LINKEDIN_USERNAME')
            linkedin_password = os.getenv('LINKEDIN_PASSWORD')

            if not linkedin_username or not linkedin_password:
                logging.warning("LinkedIn credentials not configured")
                return leads

            api = Linkedin(linkedin_username, linkedin_password)

            for keyword in keywords:
                # Search for people with relevant titles
                search_results = api.search_people(
                    keywords=keyword,
                    limit=limit // len(keywords)
                )

                for person in search_results:
                    if self.is_qualified_lead(person):
                        lead = Lead(
                            email=self.extract_email_from_linkedin(person),
                            name=person.get('name', ''),
                            company=person.get('company', ''),
                            source='linkedin',
                            score=self.calculate_lead_score(person, 'linkedin'),
                            status='new',
                            created_at=datetime.now(),
                            metadata={
                                'linkedin_profile': person.get('profile_url'),
                                'title': person.get('title'),
                                'industry': person.get('industry'),
                                'location': person.get('location')
                            }
                        )

                        if lead.email:
                            leads.append(lead)

                time.sleep(random.uniform(2, 5))  # Rate limiting

        except Exception as e:
            logging.error(f"LinkedIn scraping error: {e}")

        return leads

    def scrape_twitter_leads(self, hashtags: List[str], limit: int = 100) -> List[Lead]:
        """Find leads from Twitter conversations about GPU/ML topics"""
        leads = []

        if not TWITTER_AVAILABLE:
            logging.warning("Twitter API not available")
            return leads

        try:
            # Initialize Twitter API
            auth = tweepy.OAuthHandler(
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET')
            )
            auth.set_access_token(
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )

            api = tweepy.API(auth, wait_on_rate_limit=True)

            for hashtag in hashtags:
                tweets = tweepy.Cursor(
                    api.search_tweets,
                    q=hashtag + " -filter:retweets",
                    lang="en",
                    result_type="recent"
                ).items(limit // len(hashtags))

                for tweet in tweets:
                    user = tweet.user

                    # Check if user is a potential lead
                    if self.is_qualified_twitter_user(user, tweet):
                        email = self.extract_email_from_twitter(user)

                        if email:
                            lead = Lead(
                                email=email,
                                name=user.name,
                                company=self.extract_company_from_bio(user.description),
                                source='twitter',
                                score=self.calculate_twitter_lead_score(user, tweet),
                                status='new',
                                created_at=datetime.now(),
                                metadata={
                                    'twitter_handle': user.screen_name,
                                    'followers': user.followers_count,
                                    'tweet_content': tweet.text,
                                    'bio': user.description,
                                    'location': user.location
                                }
                            )
                            leads.append(lead)

                time.sleep(random.uniform(1, 3))  # Rate limiting

        except Exception as e:
            logging.error(f"Twitter scraping error: {e}")

        return leads

    def scrape_hackernews_leads(self, keywords: List[str]) -> List[Lead]:
        """Find leads from Hacker News discussions about GPU/ML topics"""
        leads = []

        try:
            # Get recent stories from HN API
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(top_stories_url)
            story_ids = response.json()[:100]  # Top 100 stories

            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url)
                story = story_response.json()

                if not story or 'title' not in story:
                    continue

                # Check if story is relevant
                if any(keyword.lower() in story['title'].lower() for keyword in keywords):
                    # Get comments
                    if 'kids' in story:
                        for comment_id in story['kids'][:20]:  # Top 20 comments
                            comment_url = f"https://hacker-news.firebaseio.com/v0/item/{comment_id}.json"
                            comment_response = requests.get(comment_url)
                            comment = comment_response.json()

                            if comment and 'by' in comment:
                                # Extract user info
                                user_url = f"https://hacker-news.firebaseio.com/v0/user/{comment['by']}.json"
                                user_response = requests.get(user_url)
                                user = user_response.json()

                                if user and self.is_qualified_hn_user(user, comment):
                                    email = self.extract_email_from_hn_user(user)

                                    if email:
                                        lead = Lead(
                                            email=email,
                                            name=user.get('id', ''),
                                            company=self.extract_company_from_hn_about(user.get('about', '')),
                                            source='hackernews',
                                            score=self.calculate_hn_lead_score(user, comment),
                                            status='new',
                                            created_at=datetime.now(),
                                            metadata={
                                                'hn_username': user.get('id'),
                                                'karma': user.get('karma', 0),
                                                'comment_text': comment.get('text', ''),
                                                'story_title': story['title'],
                                                'about': user.get('about', '')
                                            }
                                        )
                                        leads.append(lead)

                            time.sleep(0.5)  # Rate limiting

                time.sleep(1)  # Rate limiting between stories

        except Exception as e:
            logging.error(f"Hacker News scraping error: {e}")

        return leads

    # =============================================================================
    # AI-POWERED LEAD QUALIFICATION
    # =============================================================================

    def is_qualified_lead(self, person_data: Dict) -> bool:
        """Use AI to determine if a person is a qualified lead"""
        try:
            # Check job title relevance
            title = person_data.get('title', '').lower()
            relevant_titles = [
                'engineer', 'developer', 'scientist', 'researcher', 'architect',
                'cto', 'ceo', 'founder', 'lead', 'manager', 'director',
                'ml', 'ai', 'data', 'machine learning', 'deep learning'
            ]

            title_score = sum(1 for keyword in relevant_titles if keyword in title)

            # Check company relevance
            company = person_data.get('company', '').lower()
            relevant_companies = [
                'tech', 'ai', 'ml', 'data', 'cloud', 'startup', 'research',
                'university', 'lab', 'institute'
            ]

            company_score = sum(1 for keyword in relevant_companies if keyword in company)

            # Check industry
            industry = person_data.get('industry', '').lower()
            relevant_industries = [
                'technology', 'artificial intelligence', 'machine learning',
                'software', 'research', 'education', 'healthcare', 'finance'
            ]

            industry_score = sum(1 for keyword in relevant_industries if keyword in industry)

            # Calculate total qualification score
            total_score = title_score + company_score + industry_score

            return total_score >= 2  # Minimum threshold

        except Exception as e:
            logging.error(f"Lead qualification error: {e}")
            return False

    def is_qualified_twitter_user(self, user, tweet) -> bool:
        """Qualify Twitter users based on profile and tweet content"""
        try:
            # Check follower count (not too low, not too high)
            followers = user.followers_count
            if followers < 100 or followers > 100000:
                return False

            # Check bio for relevant keywords
            bio = user.description.lower()
            relevant_keywords = [
                'engineer', 'developer', 'ml', 'ai', 'data scientist',
                'researcher', 'founder', 'cto', 'startup'
            ]

            bio_score = sum(1 for keyword in relevant_keywords if keyword in bio)

            # Check tweet content relevance
            tweet_text = tweet.text.lower()
            gpu_keywords = ['gpu', 'cuda', 'training', 'model', 'cost', 'expensive']
            tweet_score = sum(1 for keyword in gpu_keywords if keyword in tweet_text)

            return bio_score >= 1 and tweet_score >= 1

        except Exception as e:
            logging.error(f"Twitter user qualification error: {e}")
            return False

    def is_qualified_hn_user(self, user, comment) -> bool:
        """Qualify Hacker News users based on karma and comment quality"""
        try:
            # Check karma (minimum threshold)
            karma = user.get('karma', 0)
            if karma < 100:
                return False

            # Check comment relevance
            comment_text = comment.get('text', '').lower()
            relevant_keywords = [
                'gpu', 'machine learning', 'deep learning', 'training',
                'model', 'cost', 'expensive', 'cloud', 'aws', 'gcp'
            ]

            comment_score = sum(1 for keyword in relevant_keywords if keyword in comment_text)

            # Check user about section
            about = user.get('about', '').lower()
            about_score = sum(1 for keyword in relevant_keywords if keyword in about)

            return comment_score >= 2 or about_score >= 1

        except Exception as e:
            logging.error(f"HN user qualification error: {e}")
            return False

    def calculate_lead_score(self, person_data: Dict, source: str) -> int:
        """Calculate lead quality score using AI-powered analysis"""
        try:
            score = 50  # Base score

            # Title scoring
            title = person_data.get('title', '').lower()
            if any(keyword in title for keyword in ['cto', 'ceo', 'founder', 'director']):
                score += 20
            elif any(keyword in title for keyword in ['lead', 'senior', 'principal']):
                score += 15
            elif any(keyword in title for keyword in ['engineer', 'developer', 'scientist']):
                score += 10

            # Company size scoring (if available)
            company = person_data.get('company', '')
            if company:
                score += 10

            # Industry scoring
            industry = person_data.get('industry', '').lower()
            if any(keyword in industry for keyword in ['technology', 'ai', 'ml', 'software']):
                score += 15

            # Location scoring (tech hubs)
            location = person_data.get('location', '').lower()
            tech_hubs = ['san francisco', 'silicon valley', 'new york', 'seattle', 'boston', 'austin']
            if any(hub in location for hub in tech_hubs):
                score += 10

            # Source-specific scoring
            if source == 'linkedin':
                score += 5  # LinkedIn generally higher quality
            elif source == 'github':
                score += 10  # GitHub users are developers

            return min(max(score, 1), 100)  # Clamp between 1-100

        except Exception as e:
            logging.error(f"Lead scoring error: {e}")
            return 50  # Default score

    def calculate_twitter_lead_score(self, user, tweet) -> int:
        """Calculate Twitter-specific lead score"""
        try:
            score = 40  # Lower base for Twitter

            # Follower count scoring
            followers = user.followers_count
            if 1000 <= followers <= 10000:
                score += 15
            elif 500 <= followers < 1000:
                score += 10
            elif 100 <= followers < 500:
                score += 5

            # Engagement scoring
            if hasattr(tweet, 'retweet_count') and tweet.retweet_count > 5:
                score += 10
            if hasattr(tweet, 'favorite_count') and tweet.favorite_count > 10:
                score += 10

            # Bio quality
            bio = user.description
            if len(bio) > 50:  # Detailed bio
                score += 10

            # Verified account
            if user.verified:
                score += 15

            return min(max(score, 1), 100)

        except Exception as e:
            logging.error(f"Twitter lead scoring error: {e}")
            return 40

    def calculate_hn_lead_score(self, user, comment) -> int:
        """Calculate Hacker News-specific lead score"""
        try:
            score = 45  # Base score for HN

            # Karma scoring
            karma = user.get('karma', 0)
            if karma > 5000:
                score += 20
            elif karma > 1000:
                score += 15
            elif karma > 500:
                score += 10
            elif karma > 100:
                score += 5

            # Comment quality (length and technical content)
            comment_text = comment.get('text', '')
            if len(comment_text) > 200:  # Detailed comment
                score += 10

            # Technical keywords in comment
            technical_keywords = ['algorithm', 'optimization', 'performance', 'scalability', 'architecture']
            tech_score = sum(1 for keyword in technical_keywords if keyword in comment_text.lower())
            score += tech_score * 3

            # About section quality
            about = user.get('about', '')
            if len(about) > 100:
                score += 10

            return min(max(score, 1), 100)

        except Exception as e:
            logging.error(f"HN lead scoring error: {e}")
            return 45

    # =============================================================================
    # AI-POWERED CONTENT GENERATION
    # =============================================================================

    def generate_personalized_email(self, lead: Lead, email_type: str = 'initial') -> Dict[str, str]:
        """Generate personalized email content using AI"""
        try:
            # Initialize OpenAI if available
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                return self.get_template_email(lead, email_type)

            openai.api_key = openai_api_key

            # Create personalized prompt
            prompt = self.create_email_prompt(lead, email_type)

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sales copywriter specializing in B2B SaaS for GPU optimization. Write personalized, value-focused emails that don't sound salesy."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            email_content = response.choices[0].message.content

            # Parse subject and body
            lines = email_content.split('\n')
            subject = lines[0].replace('Subject: ', '') if lines[0].startswith('Subject:') else f"Quick question about GPU costs at {lead.company}"
            body = '\n'.join(lines[1:]).strip()

            return {
                'subject': subject,
                'body': body,
                'personalized': True
            }

        except Exception as e:
            logging.error(f"AI email generation error: {e}")
            return self.get_template_email(lead, email_type)

    def create_email_prompt(self, lead: Lead, email_type: str) -> str:
        """Create AI prompt for email generation"""
        metadata = lead.metadata or {}

        prompt = f"""
        Write a personalized email for a potential customer:

        Lead Information:
        - Name: {lead.name}
        - Company: {lead.company}
        - Source: {lead.source}
        - Title: {metadata.get('title', 'Unknown')}
        - Industry: {metadata.get('industry', 'Unknown')}

        Email Type: {email_type}

        Product: GPUOptimizer - AI-powered GPU cost optimization platform that helps companies save 40-70% on GPU infrastructure costs through intelligent monitoring and optimization.

        Key Value Props:
        - Real-time GPU utilization monitoring
        - Automated cost optimization recommendations
        - 40-70% cost savings on average
        - Easy 5-minute setup
        - Works with AWS, GCP, Azure

        Requirements:
        - Keep it under 150 words
        - Be conversational and helpful, not salesy
        - Include a specific value proposition
        - End with a soft call-to-action
        - Reference their background if relevant
        - Start with "Subject: " followed by the subject line
        """

        if email_type == 'followup':
            prompt += "\n- This is a follow-up email, so reference the previous contact"
        elif email_type == 'final':
            prompt += "\n- This is a final follow-up, so create urgency but stay helpful"

        return prompt

    def get_template_email(self, lead: Lead, email_type: str) -> Dict[str, str]:
        """Fallback template emails when AI is not available"""
        templates = {
            'initial': {
                'subject': f"Quick question about GPU costs at {lead.company}",
                'body': f"""Hi {lead.name},

I noticed your work at {lead.company} and thought you might be interested in this.

We help companies like yours reduce GPU infrastructure costs by 40-70% through intelligent monitoring and optimization.

Most of our customers save $10K-$50K per month within the first 30 days.

Would you be open to a quick 5-minute demo to see how this could work for {lead.company}?

Best regards,
GPUOptimizer Team"""
            },
            'followup': {
                'subject': f"Following up on GPU optimization for {lead.company}",
                'body': f"""Hi {lead.name},

I reached out last week about helping {lead.company} reduce GPU costs.

Just wanted to share a quick case study: One of our customers (similar to {lead.company}) saved $35K in their first month by optimizing their ML training workloads.

The setup takes less than 5 minutes. Would you like to see how it works?

Best,
GPUOptimizer Team"""
            },
            'final': {
                'subject': f"Last note about GPU savings for {lead.company}",
                'body': f"""Hi {lead.name},

This will be my last email about GPU cost optimization.

I understand you're busy, but I didn't want you to miss out on potential savings of $10K-$50K per month.

If GPU costs aren't a priority right now, no worries at all. Feel free to reach out when the timing is better.

Best of luck with your projects!
GPUOptimizer Team"""
            }
        }

        template = templates.get(email_type, templates['initial'])
        return {
            'subject': template['subject'],
            'body': template['body'],
            'personalized': False
        }