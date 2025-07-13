#!/usr/bin/env python3
"""
GPUOptimizer Revenue Analytics & Reporting System
Advanced revenue analytics, forecasting, and automated reporting
"""

import os
import json
import time
import logging
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import threading
from dataclasses import dataclass, asdict
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('revenue_analytics.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class RevenueMetric:
    """Revenue metric data structure"""
    metric_name: str
    value: float
    period: str  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    date: datetime
    category: str  # 'revenue', 'customers', 'conversion', 'retention'
    subcategory: Optional[str] = None

@dataclass
class RevenueForecast:
    """Revenue forecast data structure"""
    period: str
    forecast_date: datetime
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    model_accuracy: float
    factors: Dict[str, float]

@dataclass
class RevenueReport:
    """Revenue report data structure"""
    id: str
    report_type: str  # 'daily', 'weekly', 'monthly', 'quarterly', 'custom'
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    charts: List[str]  # File paths to generated charts
    created_at: datetime

class RevenueAnalytics:
    """Advanced revenue analytics and forecasting system"""
    
    def __init__(self, revenue_manager):
        self.revenue_manager = revenue_manager
        self.db_path = "revenue_analytics.db"
        self.init_database()
        
        # Analytics configuration
        self.forecast_models = {
            'linear': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        # Key metrics to track
        self.key_metrics = [
            'total_revenue',
            'monthly_recurring_revenue',
            'annual_recurring_revenue',
            'customer_count',
            'average_revenue_per_user',
            'customer_acquisition_cost',
            'lifetime_value',
            'churn_rate',
            'conversion_rate',
            'growth_rate',
            'gross_margin',
            'net_revenue_retention'
        ]
        
        # Report templates
        self.report_templates = {
            'executive_summary': self.generate_executive_summary,
            'detailed_analysis': self.generate_detailed_analysis,
            'growth_metrics': self.generate_growth_metrics,
            'customer_analytics': self.generate_customer_analytics,
            'forecasting_report': self.generate_forecasting_report
        }
        
        # Visualization settings
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        logging.info("Revenue analytics system initialized")
    
    def init_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Revenue metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenue_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            period TEXT NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Revenue forecasts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenue_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            predicted_value REAL NOT NULL,
            confidence_interval_lower REAL,
            confidence_interval_upper REAL,
            model_accuracy REAL,
            factors TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Revenue reports table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenue_reports (
            id TEXT PRIMARY KEY,
            report_type TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            metrics TEXT NOT NULL,
            insights TEXT,
            recommendations TEXT,
            charts TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Cohort analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cohort_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cohort_month TEXT NOT NULL,
            period_number INTEGER NOT NULL,
            customers INTEGER NOT NULL,
            revenue REAL NOT NULL,
            retention_rate REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Revenue analytics database initialized")
    
    # =============================================================================
    # METRICS COLLECTION & CALCULATION
    # =============================================================================
    
    def collect_daily_metrics(self):
        """Collect and store daily revenue metrics"""
        try:
            logging.info("Collecting daily revenue metrics...")
            
            # Get current data from revenue manager
            stats = self.revenue_manager.get_revenue_stats()
            
            # Calculate metrics
            metrics = self.calculate_all_metrics(stats)
            
            # Store metrics
            for metric_name, value in metrics.items():
                metric = RevenueMetric(
                    metric_name=metric_name,
                    value=value,
                    period='daily',
                    date=datetime.now(),
                    category=self.get_metric_category(metric_name)
                )
                self.save_metric(metric)
            
            logging.info(f"Collected {len(metrics)} daily metrics")
            
        except Exception as e:
            logging.error(f"Daily metrics collection error: {e}")
    
    def calculate_all_metrics(self, stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all revenue metrics"""
        metrics = {}
        
        try:
            # Basic revenue metrics
            metrics['total_revenue'] = stats.get('total_revenue', 0)
            metrics['monthly_recurring_revenue'] = stats.get('monthly_revenue', 0)
            metrics['annual_recurring_revenue'] = metrics['monthly_recurring_revenue'] * 12
            
            # Customer metrics
            metrics['customer_count'] = stats.get('total_customers', 0)
            metrics['active_customers'] = stats.get('active_customers', 0)
            
            # Calculate ARPU
            if metrics['customer_count'] > 0:
                metrics['average_revenue_per_user'] = metrics['total_revenue'] / metrics['customer_count']
            else:
                metrics['average_revenue_per_user'] = 0
            
            # Calculate growth metrics
            metrics['growth_rate'] = self.calculate_growth_rate()
            metrics['churn_rate'] = self.calculate_churn_rate()
            metrics['conversion_rate'] = self.calculate_conversion_rate()
            
            # Calculate LTV and CAC
            metrics['lifetime_value'] = self.calculate_lifetime_value()
            metrics['customer_acquisition_cost'] = self.calculate_customer_acquisition_cost()
            
            # Calculate retention metrics
            metrics['net_revenue_retention'] = self.calculate_net_revenue_retention()
            
            # Calculate margins
            metrics['gross_margin'] = self.calculate_gross_margin(stats)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Metrics calculation error: {e}")
            return {}
    
    def calculate_growth_rate(self) -> float:
        """Calculate month-over-month growth rate"""
        try:
            # Get revenue for current and previous month
            current_month = datetime.now().replace(day=1)
            previous_month = (current_month - timedelta(days=1)).replace(day=1)
            
            current_revenue = self.get_revenue_for_period(current_month, current_month + timedelta(days=31))
            previous_revenue = self.get_revenue_for_period(previous_month, current_month)
            
            if previous_revenue > 0:
                return ((current_revenue - previous_revenue) / previous_revenue) * 100
            return 0
            
        except Exception as e:
            logging.error(f"Growth rate calculation error: {e}")
            return 0
    
    def calculate_churn_rate(self) -> float:
        """Calculate monthly churn rate"""
        try:
            # This would typically analyze customer cancellations
            # For now, return a simulated value
            return 0.05  # 5% monthly churn
            
        except Exception as e:
            logging.error(f"Churn rate calculation error: {e}")
            return 0
    
    def calculate_conversion_rate(self) -> float:
        """Calculate free-to-paid conversion rate"""
        try:
            # This would analyze trial-to-paid conversions
            # For now, return a simulated value
            return 0.15  # 15% conversion rate
            
        except Exception as e:
            logging.error(f"Conversion rate calculation error: {e}")
            return 0
    
    def calculate_lifetime_value(self) -> float:
        """Calculate customer lifetime value"""
        try:
            # LTV = ARPU / Churn Rate
            arpu = self.get_latest_metric('average_revenue_per_user')
            churn_rate = self.get_latest_metric('churn_rate')
            
            if churn_rate > 0:
                return arpu / (churn_rate / 100)  # Convert percentage to decimal
            return 0
            
        except Exception as e:
            logging.error(f"LTV calculation error: {e}")
            return 0
    
    def calculate_customer_acquisition_cost(self) -> float:
        """Calculate customer acquisition cost"""
        try:
            # This would analyze marketing spend vs new customers
            # For now, return a simulated value
            return 150  # $150 CAC
            
        except Exception as e:
            logging.error(f"CAC calculation error: {e}")
            return 0
    
    def calculate_net_revenue_retention(self) -> float:
        """Calculate net revenue retention"""
        try:
            # This would analyze revenue expansion vs churn
            # For now, return a simulated value
            return 110  # 110% NRR
            
        except Exception as e:
            logging.error(f"NRR calculation error: {e}")
            return 100
    
    def calculate_gross_margin(self, stats: Dict[str, Any]) -> float:
        """Calculate gross margin percentage"""
        try:
            total_revenue = stats.get('total_revenue', 0)
            # Estimate costs (infrastructure, support, etc.)
            estimated_costs = total_revenue * 0.3  # 30% cost ratio
            
            if total_revenue > 0:
                return ((total_revenue - estimated_costs) / total_revenue) * 100
            return 0
            
        except Exception as e:
            logging.error(f"Gross margin calculation error: {e}")
            return 0
    
    def get_revenue_for_period(self, start_date: datetime, end_date: datetime) -> float:
        """Get total revenue for a specific period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT SUM(value) FROM revenue_metrics 
            WHERE metric_name = 'total_revenue' 
            AND date BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result[0] else 0
            
        except Exception as e:
            logging.error(f"Revenue period calculation error: {e}")
            return 0
    
    def get_latest_metric(self, metric_name: str) -> float:
        """Get latest value for a specific metric"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT value FROM revenue_metrics 
            WHERE metric_name = ? 
            ORDER BY date DESC LIMIT 1
            ''', (metric_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            logging.error(f"Latest metric retrieval error: {e}")
            return 0
    
    def save_metric(self, metric: RevenueMetric):
        """Save metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO revenue_metrics 
        (metric_name, value, period, date, category, subcategory)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metric.metric_name, metric.value, metric.period,
            metric.date.isoformat(), metric.category, metric.subcategory
        ))
        
        conn.commit()
        conn.close()
    
    def get_metric_category(self, metric_name: str) -> str:
        """Get category for a metric"""
        categories = {
            'total_revenue': 'revenue',
            'monthly_recurring_revenue': 'revenue',
            'annual_recurring_revenue': 'revenue',
            'customer_count': 'customers',
            'active_customers': 'customers',
            'average_revenue_per_user': 'revenue',
            'growth_rate': 'growth',
            'churn_rate': 'retention',
            'conversion_rate': 'conversion',
            'lifetime_value': 'customers',
            'customer_acquisition_cost': 'acquisition',
            'net_revenue_retention': 'retention',
            'gross_margin': 'revenue'
        }
        return categories.get(metric_name, 'other')
    
    # =============================================================================
    # REVENUE FORECASTING
    # =============================================================================
    
    def generate_revenue_forecast(self, periods: int = 12) -> List[RevenueForecast]:
        """Generate revenue forecast for next N periods"""
        try:
            logging.info(f"Generating revenue forecast for {periods} periods...")
            
            # Get historical data
            historical_data = self.get_historical_revenue_data()
            
            if len(historical_data) < 3:
                logging.warning("Insufficient historical data for forecasting")
                return []
            
            # Prepare data for modeling
            X, y = self.prepare_forecast_data(historical_data)
            
            forecasts = []
            
            # Generate forecasts using different models
            for model_name, model in self.forecast_models.items():
                try:
                    # Train model
                    model.fit(X, y)
                    
                    # Generate predictions
                    future_X = self.generate_future_features(len(historical_data), periods)
                    predictions = model.predict(future_X)
                    
                    # Calculate confidence intervals (simplified)
                    std_error = np.std(y - model.predict(X))
                    
                    for i, prediction in enumerate(predictions):
                        forecast_date = datetime.now() + timedelta(days=30 * (i + 1))
                        
                        forecast = RevenueForecast(
                            period='monthly',
                            forecast_date=forecast_date,
                            predicted_value=max(0, prediction),
                            confidence_interval_lower=max(0, prediction - 1.96 * std_error),
                            confidence_interval_upper=prediction + 1.96 * std_error,
                            model_accuracy=self.calculate_model_accuracy(model, X, y),
                            factors=self.get_forecast_factors(historical_data)
                        )
                        
                        forecasts.append(forecast)
                        self.save_forecast(forecast)
                
                except Exception as e:
                    logging.error(f"Forecasting error with {model_name}: {e}")
            
            logging.info(f"Generated {len(forecasts)} revenue forecasts")
            return forecasts
            
        except Exception as e:
            logging.error(f"Revenue forecasting error: {e}")
            return []
