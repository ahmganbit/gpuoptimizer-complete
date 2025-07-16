#!/usr/bin/env python3
"""
GPUOptimizer Global Payment System
Primary payment system replacing Stripe - works worldwide including crypto
"""

import os
import json
import time
import logging
import requests
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaymentResult:
    """Payment processing result"""
    success: bool
    transaction_id: Optional[str]
    amount: float
    currency: str
    gateway: str
    status: str
    message: str
    payment_url: Optional[str] = None

class GlobalPaymentSystem:
    """Primary payment system for worldwide accessibility"""
    
    def __init__(self):
        # Optimized 3-gateway global payment system
        self.primary_gateways = {
            # 1. NOWPayments - Crypto (works everywhere, no restrictions)
            'nowpayments': {
                'name': 'Crypto Payments',
                'api_key': os.getenv('NOWPAYMENTS_API_KEY'),
                'api_url': 'https://api.nowpayments.io/v1',
                'countries': 'worldwide',
                'currencies': ['BTC', 'ETH', 'USDT', 'USDC', 'LTC', 'BCH', 'XRP', 'ADA', 'DOT', 'LINK', 'UNI'],
                'fees': '0.5%',
                'setup_difficulty': 'easy',
                'description': 'Bitcoin, Ethereum, USDT and 100+ cryptocurrencies'
            },

            # 2. Flutterwave - Africa, Europe, Americas + global cards
            'flutterwave': {
                'name': 'Flutterwave',
                'secret_key': os.getenv('FLUTTERWAVE_SECRET_KEY'),
                'public_key': os.getenv('FLUTTERWAVE_PUBLIC_KEY'),
                'api_url': 'https://api.flutterwave.com/v3',
                'countries': ['NG', 'GH', 'KE', 'UG', 'ZA', 'TZ', 'RW', 'ZM', 'US', 'GB', 'CA', 'AU', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'CH', 'SE', 'DK', 'NO', 'FI', 'BR', 'MX', 'AR'],
                'currencies': ['NGN', 'GHS', 'KES', 'UGX', 'ZAR', 'TZS', 'RWF', 'ZMW', 'USD', 'GBP', 'EUR', 'CAD', 'AUD'],
                'fees': '1.4%',
                'setup_difficulty': 'easy',
                'description': 'Cards, mobile money, bank transfers, Apple Pay, Google Pay'
            },

            # 3. Paddle - Global SaaS billing with tax handling
            'paddle': {
                'name': 'Paddle',
                'vendor_id': os.getenv('PADDLE_VENDOR_ID'),
                'vendor_auth_code': os.getenv('PADDLE_VENDOR_AUTH_CODE'),
                'api_url': 'https://vendors.paddle.com/api/2.0',
                'countries': 'worldwide',
                'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'DKK', 'NOK'],
                'fees': '5%',
                'setup_difficulty': 'medium',
                'description': 'Professional SaaS billing with automatic tax handling'
            }
        }
        
        # Pricing plans
        self.plans = {
            'free': {'price': 0, 'name': 'Free Plan'},
            'professional': {'price': 49, 'name': 'Professional Plan'},
            'enterprise': {'price': 199, 'name': 'Enterprise Plan'},
            'custom': {'price': 499, 'name': 'Custom Plan'}
        }
        
        logger.info("Global payment system initialized")
    
    def get_available_gateways(self, country_code: str = None) -> List[Dict[str, Any]]:
        """Get available payment gateways for a country"""
        available = []
        
        for gateway_id, gateway in self.primary_gateways.items():
            # Check if gateway is configured
            if self._is_gateway_configured(gateway_id):
                # Check if gateway supports the country
                if country_code and gateway['countries'] != 'worldwide':
                    if isinstance(gateway['countries'], list) and country_code not in gateway['countries']:
                        continue
                
                available.append({
                    'id': gateway_id,
                    'name': gateway['name'],
                    'currencies': gateway['currencies'],
                    'fees': gateway['fees'],
                    'recommended': gateway_id in ['nowpayments', 'paypal']
                })
        
        # If no gateways are available, add demo mode
        if not available:
            logger.warning("No payment gateways configured - adding demo gateway")
            available.append({
                'id': 'demo',
                'name': 'Demo Payment (Testing)',
                'currencies': ['USD', 'EUR', 'GBP'],
                'fees': '0% (Demo)',
                'recommended': True
            })

        # Sort by preference (crypto first, then PayPal)
        try:
            available.sort(key=lambda x: ['nowpayments', 'paypal', 'paddle', 'razorpay', 'flutterwave', 'demo'].index(x['id']))
        except ValueError:
            # If gateway not in list, keep original order
            pass

        return available
    
    def create_payment(self, amount: float, currency: str, plan: str, 
                      customer_email: str, gateway: str = None, 
                      country_code: str = None) -> PaymentResult:
        """Create payment with the best available gateway"""
        try:
            # Auto-select gateway if not specified
            if not gateway:
                gateway = self._select_best_gateway(country_code)
            
            # Validate gateway
            if not self._is_gateway_configured(gateway):
                raise ValueError(f"Gateway {gateway} is not configured")
            
            # Create payment based on gateway
            if gateway == 'nowpayments':
                return self._create_nowpayments_payment(amount, currency, plan, customer_email)
            elif gateway == 'paypal':
                return self._create_paypal_payment(amount, currency, plan, customer_email)
            elif gateway == 'paddle':
                return self._create_paddle_payment(amount, currency, plan, customer_email)
            elif gateway == 'razorpay':
                return self._create_razorpay_payment(amount, currency, plan, customer_email)
            elif gateway == 'flutterwave':
                return self._create_flutterwave_payment(amount, currency, plan, customer_email)
            elif gateway == 'demo':
                return self._create_demo_payment(amount, currency, plan, customer_email)
            else:
                raise ValueError(f"Unsupported gateway: {gateway}")
                
        except Exception as e:
            logger.error(f"Payment creation failed: {e}")
            return PaymentResult(
                success=False,
                transaction_id=None,
                amount=amount,
                currency=currency,
                gateway=gateway or 'unknown',
                status='failed',
                message=str(e)
            )
    
    def _select_best_gateway(self, country_code: str = None) -> str:
        """Select the best payment gateway for a country"""
        # Optimized 3-gateway selection logic

        if country_code:
            # Regional optimization
            if country_code in ['NG', 'GH', 'KE', 'UG', 'ZA', 'TZ', 'RW', 'ZM']:
                # Africa - Flutterwave is best for mobile money and local methods
                if self._is_gateway_configured('flutterwave'):
                    return 'flutterwave'
            elif country_code in ['US', 'GB', 'CA', 'AU', 'FR', 'DE', 'IT', 'ES', 'NL', 'BE', 'CH', 'SE', 'DK', 'NO', 'FI', 'BR', 'MX']:
                # Developed countries - Flutterwave for cards, Paddle for SaaS
                if self._is_gateway_configured('flutterwave'):
                    return 'flutterwave'
                elif self._is_gateway_configured('paddle'):
                    return 'paddle'

        # Global fallback priority
        # 1. Flutterwave (best rates, wide coverage)
        if self._is_gateway_configured('flutterwave'):
            return 'flutterwave'

        # 2. Crypto (works everywhere, no restrictions)
        if self._is_gateway_configured('nowpayments'):
            return 'nowpayments'

        # 3. Paddle (professional SaaS billing)
        if self._is_gateway_configured('paddle'):
            return 'paddle'

        # If no gateways configured, return demo mode
        logger.warning("No payment gateways configured - returning demo gateway")
        return 'demo'
    
    def _is_gateway_configured(self, gateway_id: str) -> bool:
        """Check if a gateway is properly configured"""
        gateway = self.primary_gateways.get(gateway_id)
        if not gateway:
            return False

        if gateway_id == 'nowpayments':
            configured = bool(gateway['api_key'])
            if not configured:
                logger.warning(f"NOWPayments not configured - missing NOWPAYMENTS_API_KEY")
            return configured
        elif gateway_id == 'flutterwave':
            configured = bool(gateway['secret_key'])
            if not configured:
                logger.warning(f"Flutterwave not configured - missing FLUTTERWAVE_SECRET_KEY")
            return configured
        elif gateway_id == 'paddle':
            configured = bool(gateway['vendor_id'] and gateway['vendor_auth_code'])
            if not configured:
                logger.warning(f"Paddle not configured - missing PADDLE_VENDOR_ID or PADDLE_VENDOR_AUTH_CODE")
            return configured

        return False
    
    # =============================================================================
    # NOWPAYMENTS - CRYPTO (PRIMARY CHOICE)
    # =============================================================================
    
    def _create_nowpayments_payment(self, amount: float, currency: str, plan: str, customer_email: str) -> PaymentResult:
        """Create NOWPayments crypto payment"""
        try:
            api_key = self.primary_gateways['nowpayments']['api_key']
            
            # Convert to USD (NOWPayments base currency)
            usd_amount = self._convert_to_usd(amount, currency)
            
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            
            order_id = f"gpu_{uuid.uuid4().hex[:8]}"
            
            payload = {
                'price_amount': usd_amount,
                'price_currency': 'USD',
                'pay_currency': 'btc',  # Default to Bitcoin
                'order_id': order_id,
                'order_description': f"GPUOptimizer {self.plans[plan]['name']}",
                'ipn_callback_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/api/webhooks/nowpayments",
                'success_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success?order_id={order_id}",
                'cancel_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/cancel"
            }
            
            response = requests.post(
                f"{self.primary_gateways['nowpayments']['api_url']}/payment",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return PaymentResult(
                    success=True,
                    transaction_id=data['payment_id'],
                    amount=usd_amount,
                    currency='USD',
                    gateway='nowpayments',
                    status='pending',
                    message='Crypto payment created successfully',
                    payment_url=data['payment_url']
                )
            else:
                raise Exception(f"NOWPayments API error: {response.text}")
                
        except Exception as e:
            logger.error(f"NOWPayments payment failed: {e}")
            return PaymentResult(
                success=False,
                transaction_id=None,
                amount=amount,
                currency=currency,
                gateway='nowpayments',
                status='failed',
                message=str(e)
            )
    
    # =============================================================================
    # PAYPAL - GLOBAL (SECONDARY CHOICE)
    # =============================================================================
    
    def _create_paypal_payment(self, amount: float, currency: str, plan: str, customer_email: str) -> PaymentResult:
        """Create PayPal payment"""
        try:
            client_id = self.primary_gateways['paypal']['client_id']
            client_secret = self.primary_gateways['paypal']['client_secret']
            api_url = self.primary_gateways['paypal']['api_url']
            
            # Get access token
            auth_response = requests.post(
                f"{api_url}/v1/oauth2/token",
                headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
                auth=(client_id, client_secret),
                data={'grant_type': 'client_credentials'}
            )
            
            if auth_response.status_code != 200:
                raise Exception(f"PayPal auth failed: {auth_response.text}")
            
            access_token = auth_response.json()['access_token']
            
            # Create order
            order_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': currency,
                        'value': str(amount)
                    },
                    'description': f'GPUOptimizer {self.plans[plan]["name"]}'
                }],
                'application_context': {
                    'return_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                    'cancel_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/cancel",
                    'brand_name': 'GPUOptimizer',
                    'user_action': 'PAY_NOW'
                }
            }
            
            order_response = requests.post(
                f"{api_url}/v2/checkout/orders",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                },
                json=order_data
            )
            
            if order_response.status_code == 201:
                data = order_response.json()
                approval_url = next(link['href'] for link in data['links'] if link['rel'] == 'approve')
                
                return PaymentResult(
                    success=True,
                    transaction_id=data['id'],
                    amount=amount,
                    currency=currency,
                    gateway='paypal',
                    status='pending',
                    message='PayPal payment created successfully',
                    payment_url=approval_url
                )
            else:
                raise Exception(f"PayPal order creation failed: {order_response.text}")
                
        except Exception as e:
            logger.error(f"PayPal payment failed: {e}")
            return PaymentResult(
                success=False,
                transaction_id=None,
                amount=amount,
                currency=currency,
                gateway='paypal',
                status='failed',
                message=str(e)
            )
    
    def _convert_to_usd(self, amount: float, currency: str) -> float:
        """Convert amount to USD (simplified conversion)"""
        if currency == 'USD':
            return amount
        
        # Simplified conversion rates (in production, use real-time rates)
        rates = {
            'EUR': 1.1,
            'GBP': 1.25,
            'CAD': 0.75,
            'AUD': 0.65,
            'JPY': 0.007,
            'INR': 0.012,
            'NGN': 0.0024
        }
        
        rate = rates.get(currency, 1.0)
        return round(amount * rate, 2)
    
    def get_payment_status(self, transaction_id: str, gateway: str) -> Dict[str, Any]:
        """Get payment status from gateway"""
        try:
            if gateway == 'nowpayments':
                return self._get_nowpayments_status(transaction_id)
            elif gateway == 'paypal':
                return self._get_paypal_status(transaction_id)
            # Add other gateways as needed
            
        except Exception as e:
            logger.error(f"Status check failed for {gateway}: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    def _get_nowpayments_status(self, payment_id: str) -> Dict[str, Any]:
        """Get NOWPayments payment status"""
        try:
            api_key = self.primary_gateways['nowpayments']['api_key']
            headers = {'x-api-key': api_key}
            
            response = requests.get(
                f"{self.primary_gateways['nowpayments']['api_url']}/payment/{payment_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"NOWPayments status check failed: {response.text}")
                
        except Exception as e:
            logger.error(f"NOWPayments status check failed: {e}")
            return {'status': 'unknown', 'error': str(e)}

    # =============================================================================
    # DEMO PAYMENT SYSTEM (FOR TESTING)
    # =============================================================================

    def _create_demo_payment(self, amount: float, currency: str, plan: str, customer_email: str) -> PaymentResult:
        """Create demo payment for testing when no gateways are configured"""
        try:
            transaction_id = f"demo_{uuid.uuid4().hex[:12]}"

            logger.info(f"Demo payment created: {transaction_id} for {customer_email}")

            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                gateway='demo',
                status='pending',
                message='Demo payment created - this is for testing only',
                payment_url=f"https://demo-payment.gpuoptimizer.com/pay/{transaction_id}"
            )

        except Exception as e:
            logger.error(f"Demo payment creation failed: {e}")
            return PaymentResult(
                success=False,
                transaction_id=None,
                amount=amount,
                currency=currency,
                gateway='demo',
                status='failed',
                message=f"Demo payment failed: {str(e)}"
            )
