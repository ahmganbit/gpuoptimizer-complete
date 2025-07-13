#!/usr/bin/env python3
"""
GPUOptimizer Intelligent Customer Onboarding System
AI-powered personalized onboarding and activation
"""

import os
import json
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import threading
from dataclasses import dataclass, asdict
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_onboarding.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class OnboardingStep:
    """Individual onboarding step"""
    id: str
    name: str
    description: str
    step_type: str  # 'setup', 'tutorial', 'integration', 'verification'
    estimated_time: int  # minutes
    is_required: bool
    prerequisites: List[str]
    completion_criteria: Dict[str, Any]
    help_resources: List[str]

@dataclass
class CustomerProfile:
    """Customer profile for personalization"""
    customer_id: str
    company_size: str  # 'startup', 'small', 'medium', 'enterprise'
    industry: str
    use_case: str  # 'ml_training', 'inference', 'research', 'development'
    technical_level: str  # 'beginner', 'intermediate', 'expert'
    infrastructure: str  # 'aws', 'gcp', 'azure', 'on_premise', 'hybrid'
    goals: List[str]
    pain_points: List[str]
    created_at: datetime

@dataclass
class OnboardingJourney:
    """Customer onboarding journey tracking"""
    customer_id: str
    journey_id: str
    profile: CustomerProfile
    steps: List[OnboardingStep]
    current_step: int
    completion_rate: float
    time_to_value: Optional[int]  # minutes to first value
    activation_score: float
    status: str  # 'active', 'completed', 'stalled', 'churned'
    started_at: datetime
    completed_at: Optional[datetime] = None

class IntelligentOnboarding:
    """AI-powered customer onboarding system"""
    
    def __init__(self, revenue_manager):
        self.revenue_manager = revenue_manager
        self.db_path = "intelligent_onboarding.db"
        self.init_database()
        
        # Onboarding templates by customer type
        self.onboarding_templates = {
            'startup_ml_training': self.create_startup_ml_template(),
            'enterprise_inference': self.create_enterprise_inference_template(),
            'research_development': self.create_research_template(),
            'small_business_general': self.create_small_business_template()
        }
        
        # Activation criteria
        self.activation_criteria = {
            'first_gpu_connected': 20,
            'first_optimization_applied': 30,
            'cost_savings_achieved': 40,
            'dashboard_configured': 10,
            'api_integration_completed': 25,
            'team_member_invited': 15,
            'alert_configured': 10,
            'report_generated': 15
        }
        
        # Email templates
        self.email_templates = {
            'welcome': self.get_welcome_email_template(),
            'step_reminder': self.get_step_reminder_template(),
            'progress_update': self.get_progress_update_template(),
            'completion_celebration': self.get_completion_template(),
            'stalled_intervention': self.get_stalled_intervention_template()
        }
        
        logging.info("Intelligent onboarding system initialized")
    
    def init_database(self):
        """Initialize onboarding database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customer profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_profiles (
            customer_id TEXT PRIMARY KEY,
            company_size TEXT,
            industry TEXT,
            use_case TEXT,
            technical_level TEXT,
            infrastructure TEXT,
            goals TEXT,
            pain_points TEXT,
            created_at TEXT
        )
        ''')
        
        # Onboarding journeys table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS onboarding_journeys (
            customer_id TEXT PRIMARY KEY,
            journey_id TEXT UNIQUE,
            profile_data TEXT,
            steps_data TEXT,
            current_step INTEGER DEFAULT 0,
            completion_rate REAL DEFAULT 0,
            time_to_value INTEGER,
            activation_score REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer_profiles (customer_id)
        )
        ''')
        
        # Step completions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS step_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            step_id TEXT,
            completed_at TEXT,
            time_taken INTEGER,
            success_rate REAL,
            feedback TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer_profiles (customer_id)
        )
        ''')
        
        # Onboarding metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS onboarding_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            metric_name TEXT,
            metric_value REAL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customer_profiles (customer_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Onboarding database initialized")
    
    # =============================================================================
    # CUSTOMER PROFILING & PERSONALIZATION
    # =============================================================================
    
    def create_customer_profile(self, customer_id: str, survey_data: Dict[str, Any]) -> CustomerProfile:
        """Create customer profile from onboarding survey"""
        try:
            profile = CustomerProfile(
                customer_id=customer_id,
                company_size=survey_data.get('company_size', 'small'),
                industry=survey_data.get('industry', 'technology'),
                use_case=survey_data.get('use_case', 'ml_training'),
                technical_level=survey_data.get('technical_level', 'intermediate'),
                infrastructure=survey_data.get('infrastructure', 'aws'),
                goals=survey_data.get('goals', ['reduce_costs']),
                pain_points=survey_data.get('pain_points', ['high_gpu_costs']),
                created_at=datetime.now()
            )
            
            self.save_customer_profile(profile)
            logging.info(f"Created customer profile for {customer_id}")
            
            return profile
            
        except Exception as e:
            logging.error(f"Profile creation error: {e}")
            raise
    
    def save_customer_profile(self, profile: CustomerProfile):
        """Save customer profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO customer_profiles 
        (customer_id, company_size, industry, use_case, technical_level, 
         infrastructure, goals, pain_points, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.customer_id, profile.company_size, profile.industry,
            profile.use_case, profile.technical_level, profile.infrastructure,
            json.dumps(profile.goals), json.dumps(profile.pain_points),
            profile.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get customer profile from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customer_profiles WHERE customer_id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return CustomerProfile(
                customer_id=row[0],
                company_size=row[1],
                industry=row[2],
                use_case=row[3],
                technical_level=row[4],
                infrastructure=row[5],
                goals=json.loads(row[6]),
                pain_points=json.loads(row[7]),
                created_at=datetime.fromisoformat(row[8])
            )
        return None
    
    def start_personalized_onboarding(self, customer_id: str, profile: CustomerProfile) -> OnboardingJourney:
        """Start personalized onboarding journey"""
        try:
            # Select appropriate template
            template_key = self.select_onboarding_template(profile)
            steps = self.onboarding_templates[template_key]
            
            # Customize steps based on profile
            customized_steps = self.customize_onboarding_steps(steps, profile)
            
            journey = OnboardingJourney(
                customer_id=customer_id,
                journey_id=str(uuid.uuid4()),
                profile=profile,
                steps=customized_steps,
                current_step=0,
                completion_rate=0.0,
                time_to_value=None,
                activation_score=0.0,
                status='active',
                started_at=datetime.now()
            )
            
            self.save_onboarding_journey(journey)
            self.send_welcome_email(customer_id, profile)
            self.schedule_onboarding_reminders(customer_id)
            
            logging.info(f"Started onboarding journey for {customer_id}")
            return journey
            
        except Exception as e:
            logging.error(f"Onboarding start error: {e}")
            raise
    
    def select_onboarding_template(self, profile: CustomerProfile) -> str:
        """Select appropriate onboarding template"""
        # Simple rule-based selection (could be ML-powered)
        if profile.company_size == 'startup' and profile.use_case == 'ml_training':
            return 'startup_ml_training'
        elif profile.company_size == 'enterprise' and profile.use_case == 'inference':
            return 'enterprise_inference'
        elif profile.use_case in ['research', 'development']:
            return 'research_development'
        else:
            return 'small_business_general'
    
    def customize_onboarding_steps(self, steps: List[OnboardingStep], profile: CustomerProfile) -> List[OnboardingStep]:
        """Customize onboarding steps based on customer profile"""
        customized = []
        
        for step in steps:
            # Skip advanced steps for beginners
            if profile.technical_level == 'beginner' and 'advanced' in step.name.lower():
                continue
            
            # Skip infrastructure-specific steps
            if step.name.lower().startswith('aws') and profile.infrastructure != 'aws':
                continue
            if step.name.lower().startswith('gcp') and profile.infrastructure != 'gcp':
                continue
            if step.name.lower().startswith('azure') and profile.infrastructure != 'azure':
                continue
            
            # Adjust time estimates based on technical level
            if profile.technical_level == 'beginner':
                step.estimated_time = int(step.estimated_time * 1.5)
            elif profile.technical_level == 'expert':
                step.estimated_time = int(step.estimated_time * 0.7)
            
            customized.append(step)
        
        return customized
    
    # =============================================================================
    # ONBOARDING TEMPLATES
    # =============================================================================
    
    def create_startup_ml_template(self) -> List[OnboardingStep]:
        """Create onboarding template for ML startups"""
        return [
            OnboardingStep(
                id='welcome_survey',
                name='Welcome Survey',
                description='Tell us about your ML infrastructure and goals',
                step_type='setup',
                estimated_time=5,
                is_required=True,
                prerequisites=[],
                completion_criteria={'survey_completed': True},
                help_resources=['survey_help_guide']
            ),
            OnboardingStep(
                id='connect_first_gpu',
                name='Connect Your First GPU',
                description='Install the GPUOptimizer agent on your training instance',
                step_type='setup',
                estimated_time=10,
                is_required=True,
                prerequisites=['welcome_survey'],
                completion_criteria={'gpu_connected': True},
                help_resources=['installation_guide', 'video_tutorial']
            ),
            OnboardingStep(
                id='configure_monitoring',
                name='Configure Monitoring',
                description='Set up real-time GPU utilization monitoring',
                step_type='setup',
                estimated_time=15,
                is_required=True,
                prerequisites=['connect_first_gpu'],
                completion_criteria={'monitoring_active': True},
                help_resources=['monitoring_setup_guide']
            ),
            OnboardingStep(
                id='first_optimization',
                name='Apply First Optimization',
                description='Let GPUOptimizer optimize your training workload',
                step_type='tutorial',
                estimated_time=20,
                is_required=True,
                prerequisites=['configure_monitoring'],
                completion_criteria={'optimization_applied': True},
                help_resources=['optimization_guide', 'best_practices']
            ),
            OnboardingStep(
                id='cost_dashboard',
                name='Explore Cost Dashboard',
                description='Review your GPU cost savings and trends',
                step_type='tutorial',
                estimated_time=10,
                is_required=False,
                prerequisites=['first_optimization'],
                completion_criteria={'dashboard_viewed': True},
                help_resources=['dashboard_tour']
            ),
            OnboardingStep(
                id='set_alerts',
                name='Set Up Cost Alerts',
                description='Configure alerts for unusual GPU spending',
                step_type='setup',
                estimated_time=8,
                is_required=False,
                prerequisites=['cost_dashboard'],
                completion_criteria={'alerts_configured': True},
                help_resources=['alerts_guide']
            ),
            OnboardingStep(
                id='api_integration',
                name='API Integration',
                description='Integrate GPUOptimizer with your ML pipeline',
                step_type='integration',
                estimated_time=30,
                is_required=False,
                prerequisites=['first_optimization'],
                completion_criteria={'api_integrated': True},
                help_resources=['api_documentation', 'code_examples']
            )
        ]
    
    def create_enterprise_inference_template(self) -> List[OnboardingStep]:
        """Create onboarding template for enterprise inference workloads"""
        return [
            OnboardingStep(
                id='enterprise_consultation',
                name='Enterprise Consultation',
                description='Schedule a call with our solutions architect',
                step_type='setup',
                estimated_time=30,
                is_required=True,
                prerequisites=[],
                completion_criteria={'consultation_scheduled': True},
                help_resources=['enterprise_guide']
            ),
            OnboardingStep(
                id='infrastructure_audit',
                name='Infrastructure Audit',
                description='Comprehensive audit of your GPU infrastructure',
                step_type='setup',
                estimated_time=60,
                is_required=True,
                prerequisites=['enterprise_consultation'],
                completion_criteria={'audit_completed': True},
                help_resources=['audit_checklist']
            ),
            OnboardingStep(
                id='pilot_deployment',
                name='Pilot Deployment',
                description='Deploy GPUOptimizer on a subset of your infrastructure',
                step_type='setup',
                estimated_time=120,
                is_required=True,
                prerequisites=['infrastructure_audit'],
                completion_criteria={'pilot_deployed': True},
                help_resources=['deployment_guide', 'enterprise_setup']
            ),
            OnboardingStep(
                id='performance_baseline',
                name='Performance Baseline',
                description='Establish baseline metrics for optimization',
                step_type='setup',
                estimated_time=45,
                is_required=True,
                prerequisites=['pilot_deployment'],
                completion_criteria={'baseline_established': True},
                help_resources=['baseline_guide']
            ),
            OnboardingStep(
                id='optimization_rollout',
                name='Optimization Rollout',
                description='Gradually roll out optimizations across infrastructure',
                step_type='tutorial',
                estimated_time=90,
                is_required=True,
                prerequisites=['performance_baseline'],
                completion_criteria={'rollout_completed': True},
                help_resources=['rollout_strategy']
            ),
            OnboardingStep(
                id='team_training',
                name='Team Training',
                description='Train your team on GPUOptimizer best practices',
                step_type='tutorial',
                estimated_time=120,
                is_required=False,
                prerequisites=['optimization_rollout'],
                completion_criteria={'training_completed': True},
                help_resources=['training_materials', 'certification_program']
            )
        ]
