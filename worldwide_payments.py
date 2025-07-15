#!/usr/bin/env python3
"""
GPUOptimizer Worldwide Payment System
Supports payments from every country including crypto
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
    metadata: Dict[str, Any]

class WorldwidePaymentProcessor:
    """Comprehensive worldwide payment processing system"""
    
    def __init__(self):
        # Payment gateway configurations
        self.gateways = {
            # Crypto payments (worldwide)
            'nowpayments': {
                'api_key': os.getenv('NOWPAYMENTS_API_KEY'),
                'api_url': 'https://api.nowpayments.io/v1',
                'supported_countries': 'worldwide',
                'currencies': ['BTC', 'ETH', 'USDT', 'LTC', 'BCH', 'XRP', 'ADA', 'DOT', 'LINK', 'UNI']
            },
            
            # PayPal (190+ countries)
            'paypal': {
                'client_id': os.getenv('PAYPAL_CLIENT_ID'),
                'client_secret': os.getenv('PAYPAL_CLIENT_SECRET'),
                'api_url': 'https://api.paypal.com' if os.getenv('PAYPAL_MODE') == 'live' else 'https://api.sandbox.paypal.com',
                'supported_countries': 'worldwide',
                'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']
            },
            
            # Razorpay (India, Malaysia, UAE)
            'razorpay': {
                'key_id': os.getenv('RAZORPAY_KEY_ID'),
                'key_secret': os.getenv('RAZORPAY_KEY_SECRET'),
                'api_url': 'https://api.razorpay.com/v1',
                'supported_countries': ['IN', 'MY', 'AE'],
                'currencies': ['INR', 'MYR', 'AED']
            },
            
            # Flutterwave (Africa, Europe, Americas)
            'flutterwave': {
                'secret_key': os.getenv('FLUTTERWAVE_SECRET_KEY'),
                'public_key': os.getenv('FLUTTERWAVE_PUBLIC_KEY'),
                'api_url': 'https://api.flutterwave.com/v3',
                'supported_countries': ['NG', 'GH', 'KE', 'UG', 'ZA', 'TZ', 'RW', 'ZM', 'US', 'GB', 'CA'],
                'currencies': ['NGN', 'GHS', 'KES', 'UGX', 'ZAR', 'TZS', 'RWF', 'ZMW', 'USD', 'GBP', 'CAD']
            },
            
            # Paddle (Global SaaS billing)
            'paddle': {
                'vendor_id': os.getenv('PADDLE_VENDOR_ID'),
                'vendor_auth_code': os.getenv('PADDLE_VENDOR_AUTH_CODE'),
                'api_url': 'https://vendors.paddle.com/api/2.0',
                'supported_countries': 'worldwide',
                'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'DKK', 'NOK']
            },
            
            # Coinbase Commerce (Crypto worldwide)
            'coinbase': {
                'api_key': os.getenv('COINBASE_COMMERCE_API_KEY'),
                'webhook_secret': os.getenv('COINBASE_WEBHOOK_SECRET'),
                'api_url': 'https://api.commerce.coinbase.com',
                'supported_countries': 'worldwide',
                'currencies': ['BTC', 'ETH', 'LTC', 'BCH', 'USDC', 'DAI']
            },
            
            # Lemonsqueezy (Global digital products)
            'lemonsqueezy': {
                'api_key': os.getenv('LEMONSQUEEZY_API_KEY'),
                'store_id': os.getenv('LEMONSQUEEZY_STORE_ID'),
                'api_url': 'https://api.lemonsqueezy.com/v1',
                'supported_countries': 'worldwide',
                'currencies': ['USD', 'EUR', 'GBP']
            },
            
            # Stripe (backup for supported countries)
            'stripe': {
                'secret_key': os.getenv('STRIPE_SECRET_KEY'),
                'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
                'api_url': 'https://api.stripe.com/v1',
                'supported_countries': ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'SE', 'DK', 'NO', 'FI', 'IE', 'PT', 'LU', 'GR', 'CY', 'MT', 'SI', 'SK', 'EE', 'LV', 'LT', 'PL', 'CZ', 'HU', 'RO', 'BG', 'HR', 'JP', 'SG', 'HK', 'NZ', 'MX', 'BR', 'IN', 'MY', 'TH', 'PH', 'ID'],
                'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'SGD', 'HKD', 'NZD', 'MXN', 'BRL', 'INR', 'MYR', 'THB', 'PHP', 'IDR']
            }
        }
        
        # Pricing tiers (in USD)
        self.pricing_tiers = {
            'free': {'price': 0, 'features': ['basic_monitoring'], 'limits': {'gpus': 2}},
            'professional': {'price': 49, 'features': ['advanced_monitoring', 'optimization'], 'limits': {'gpus': 10}},
            'enterprise': {'price': 199, 'features': ['full_suite', 'priority_support'], 'limits': {'gpus': 100}},
            'custom': {'price': 499, 'features': ['white_label', 'custom_integration'], 'limits': {'gpus': 1000}}
        }
        
        logger.info("Worldwide payment processor initialized")
    
    def get_best_gateway_for_country(self, country_code: str, currency: str = 'USD') -> str:
        """Get the best payment gateway for a specific country"""
        try:
            # Priority order for different regions
            if country_code in ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'IT', 'ES']:
                # Developed countries - prefer Stripe, PayPal, then crypto
                if self.gateways['stripe']['secret_key']:
                    return 'stripe'
                elif self.gateways['paypal']['client_id']:
                    return 'paypal'
                else:
                    return 'nowpayments'
            
            elif country_code in ['IN', 'MY', 'AE']:
                # Razorpay supported countries
                if self.gateways['razorpay']['key_id']:
                    return 'razorpay'
                elif self.gateways['paypal']['client_id']:
                    return 'paypal'
                else:
                    return 'nowpayments'
            
            elif country_code in ['NG', 'GH', 'KE', 'UG', 'ZA', 'TZ', 'RW', 'ZM']:
                # African countries - prefer Flutterwave
                if self.gateways['flutterwave']['secret_key']:
                    return 'flutterwave'
                elif self.gateways['paypal']['client_id']:
                    return 'paypal'
                else:
                    return 'nowpayments'
            
            else:
                # All other countries - prefer crypto, PayPal, or Paddle
                if self.gateways['nowpayments']['api_key']:
                    return 'nowpayments'
                elif self.gateways['paypal']['client_id']:
                    return 'paypal'
                elif self.gateways['paddle']['vendor_id']:
                    return 'paddle'
                else:
                    return 'coinbase'
        
        except Exception as e:
            logger.error(f"Error selecting gateway for {country_code}: {e}")
            return 'nowpayments'  # Fallback to crypto
    
    def create_payment_intent(self, amount: float, currency: str, gateway: str, 
                            customer_email: str, plan: str, country_code: str = None) -> Dict[str, Any]:
        """Create payment intent with the specified gateway"""
        try:
            if gateway == 'nowpayments':
                return self.create_nowpayments_payment(amount, currency, customer_email, plan)
            elif gateway == 'paypal':
                return self.create_paypal_payment(amount, currency, customer_email, plan)
            elif gateway == 'razorpay':
                return self.create_razorpay_payment(amount, currency, customer_email, plan)
            elif gateway == 'flutterwave':
                return self.create_flutterwave_payment(amount, currency, customer_email, plan)
            elif gateway == 'paddle':
                return self.create_paddle_payment(amount, currency, customer_email, plan)
            elif gateway == 'coinbase':
                return self.create_coinbase_payment(amount, currency, customer_email, plan)
            elif gateway == 'lemonsqueezy':
                return self.create_lemonsqueezy_payment(amount, currency, customer_email, plan)
            elif gateway == 'stripe':
                return self.create_stripe_payment(amount, currency, customer_email, plan)
            else:
                raise ValueError(f"Unsupported gateway: {gateway}")
                
        except Exception as e:
            logger.error(f"Payment intent creation failed for {gateway}: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': gateway
            }
    
    # =============================================================================
    # NOWPAYMENTS (CRYPTO) - WORLDWIDE
    # =============================================================================
    
    def create_nowpayments_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create NOWPayments crypto payment"""
        try:
            api_key = self.gateways['nowpayments']['api_key']
            if not api_key:
                raise ValueError("NOWPayments API key not configured")
            
            # Convert to USD if needed (NOWPayments works with USD)
            usd_amount = self.convert_to_usd(amount, currency)
            
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'price_amount': usd_amount,
                'price_currency': 'USD',
                'pay_currency': 'btc',  # Default to Bitcoin
                'order_id': f"gpu_opt_{uuid.uuid4().hex[:8]}",
                'order_description': f"GPUOptimizer {plan.title()} Plan",
                'ipn_callback_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/api/webhooks/nowpayments",
                'success_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                'cancel_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/cancel"
            }
            
            response = requests.post(
                f"{self.gateways['nowpayments']['api_url']}/payment",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'payment_id': data['payment_id'],
                    'payment_url': data['payment_url'],
                    'amount': usd_amount,
                    'currency': 'USD',
                    'gateway': 'nowpayments',
                    'status': 'pending',
                    'expires_at': data.get('expires_at'),
                    'supported_currencies': ['BTC', 'ETH', 'USDT', 'LTC', 'BCH', 'XRP', 'ADA']
                }
            else:
                raise Exception(f"NOWPayments API error: {response.text}")
                
        except Exception as e:
            logger.error(f"NOWPayments payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'nowpayments'
            }
    
    # =============================================================================
    # PAYPAL - 190+ COUNTRIES
    # =============================================================================
    
    def create_paypal_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create PayPal payment"""
        try:
            client_id = self.gateways['paypal']['client_id']
            client_secret = self.gateways['paypal']['client_secret']
            
            if not client_id or not client_secret:
                raise ValueError("PayPal credentials not configured")
            
            # Get access token
            auth_response = requests.post(
                f"{self.gateways['paypal']['api_url']}/v1/oauth2/token",
                headers={
                    'Accept': 'application/json',
                    'Accept-Language': 'en_US',
                },
                auth=(client_id, client_secret),
                data={'grant_type': 'client_credentials'}
            )
            
            if auth_response.status_code != 200:
                raise Exception(f"PayPal auth failed: {auth_response.text}")
            
            access_token = auth_response.json()['access_token']
            
            # Create payment
            payment_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': currency,
                        'value': str(amount)
                    },
                    'description': f'GPUOptimizer {plan.title()} Plan'
                }],
                'application_context': {
                    'return_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                    'cancel_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/cancel"
                }
            }
            
            payment_response = requests.post(
                f"{self.gateways['paypal']['api_url']}/v2/checkout/orders",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                },
                json=payment_data
            )
            
            if payment_response.status_code == 201:
                data = payment_response.json()
                approval_url = next(link['href'] for link in data['links'] if link['rel'] == 'approve')
                
                return {
                    'success': True,
                    'payment_id': data['id'],
                    'payment_url': approval_url,
                    'amount': amount,
                    'currency': currency,
                    'gateway': 'paypal',
                    'status': 'pending'
                }
            else:
                raise Exception(f"PayPal payment creation failed: {payment_response.text}")
                
        except Exception as e:
            logger.error(f"PayPal payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'paypal'
            }
    
    # =============================================================================
    # RAZORPAY - INDIA, MALAYSIA, UAE
    # =============================================================================
    
    def create_razorpay_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create Razorpay payment"""
        try:
            key_id = self.gateways['razorpay']['key_id']
            key_secret = self.gateways['razorpay']['key_secret']
            
            if not key_id or not key_secret:
                raise ValueError("Razorpay credentials not configured")
            
            # Convert amount to smallest currency unit (paise for INR)
            if currency == 'INR':
                amount_in_paise = int(amount * 100)
            else:
                amount_in_paise = int(amount * 100)  # Assume cents for other currencies
            
            payment_data = {
                'amount': amount_in_paise,
                'currency': currency,
                'receipt': f"gpu_opt_{uuid.uuid4().hex[:8]}",
                'notes': {
                    'plan': plan,
                    'customer_email': customer_email
                }
            }
            
            response = requests.post(
                f"{self.gateways['razorpay']['api_url']}/orders",
                auth=(key_id, key_secret),
                json=payment_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'payment_id': data['id'],
                    'amount': amount,
                    'currency': currency,
                    'gateway': 'razorpay',
                    'status': 'pending',
                    'key_id': key_id  # Needed for frontend
                }
            else:
                raise Exception(f"Razorpay order creation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Razorpay payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'razorpay'
            }

    # =============================================================================
    # FLUTTERWAVE - AFRICA, EUROPE, AMERICAS
    # =============================================================================

    def create_flutterwave_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create Flutterwave payment"""
        try:
            secret_key = self.gateways['flutterwave']['secret_key']
            if not secret_key:
                raise ValueError("Flutterwave secret key not configured")

            payment_data = {
                'tx_ref': f"gpu_opt_{uuid.uuid4().hex[:8]}",
                'amount': amount,
                'currency': currency,
                'redirect_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                'customer': {
                    'email': customer_email,
                    'name': customer_email.split('@')[0]
                },
                'customizations': {
                    'title': 'GPUOptimizer',
                    'description': f'GPUOptimizer {plan.title()} Plan',
                    'logo': f"{os.getenv('DOMAIN', 'localhost:5000')}/static/logo.png"
                }
            }

            headers = {
                'Authorization': f'Bearer {secret_key}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f"{self.gateways['flutterwave']['api_url']}/payments",
                headers=headers,
                json=payment_data
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    return {
                        'success': True,
                        'payment_id': data['data']['id'],
                        'payment_url': data['data']['link'],
                        'amount': amount,
                        'currency': currency,
                        'gateway': 'flutterwave',
                        'status': 'pending'
                    }
                else:
                    raise Exception(f"Flutterwave error: {data['message']}")
            else:
                raise Exception(f"Flutterwave API error: {response.text}")

        except Exception as e:
            logger.error(f"Flutterwave payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'flutterwave'
            }

    # =============================================================================
    # COINBASE COMMERCE - CRYPTO WORLDWIDE
    # =============================================================================

    def create_coinbase_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create Coinbase Commerce crypto payment"""
        try:
            api_key = self.gateways['coinbase']['api_key']
            if not api_key:
                raise ValueError("Coinbase Commerce API key not configured")

            # Convert to USD if needed
            usd_amount = self.convert_to_usd(amount, currency)

            charge_data = {
                'name': f'GPUOptimizer {plan.title()} Plan',
                'description': f'Monthly subscription to GPUOptimizer {plan} plan',
                'local_price': {
                    'amount': str(usd_amount),
                    'currency': 'USD'
                },
                'pricing_type': 'fixed_price',
                'metadata': {
                    'customer_email': customer_email,
                    'plan': plan
                },
                'redirect_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                'cancel_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/cancel"
            }

            headers = {
                'Content-Type': 'application/json',
                'X-CC-Api-Key': api_key,
                'X-CC-Version': '2018-03-22'
            }

            response = requests.post(
                f"{self.gateways['coinbase']['api_url']}/charges",
                headers=headers,
                json=charge_data
            )

            if response.status_code == 201:
                data = response.json()['data']
                return {
                    'success': True,
                    'payment_id': data['id'],
                    'payment_url': data['hosted_url'],
                    'amount': usd_amount,
                    'currency': 'USD',
                    'gateway': 'coinbase',
                    'status': 'pending',
                    'expires_at': data['expires_at'],
                    'supported_currencies': ['BTC', 'ETH', 'LTC', 'BCH', 'USDC', 'DAI']
                }
            else:
                raise Exception(f"Coinbase Commerce API error: {response.text}")

        except Exception as e:
            logger.error(f"Coinbase Commerce payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'coinbase'
            }

    # =============================================================================
    # PADDLE - GLOBAL SAAS BILLING
    # =============================================================================

    def create_paddle_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create Paddle payment"""
        try:
            vendor_id = self.gateways['paddle']['vendor_id']
            vendor_auth_code = self.gateways['paddle']['vendor_auth_code']

            if not vendor_id or not vendor_auth_code:
                raise ValueError("Paddle credentials not configured")

            # Create product first (or use existing product ID)
            product_data = {
                'vendor_id': vendor_id,
                'vendor_auth_code': vendor_auth_code,
                'title': f'GPUOptimizer {plan.title()} Plan',
                'description': f'Monthly subscription to GPUOptimizer {plan} plan',
                'base_price': amount,
                'currency': currency,
                'recurring': 1,
                'recurring_type': 'month'
            }

            # For simplicity, we'll create a checkout URL
            checkout_data = {
                'vendor_id': vendor_id,
                'vendor_auth_code': vendor_auth_code,
                'prices': [f'{currency}:{amount}'],
                'return_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                'title': f'GPUOptimizer {plan.title()} Plan',
                'webhook_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/api/webhooks/paddle",
                'customer_email': customer_email
            }

            response = requests.post(
                f"{self.gateways['paddle']['api_url']}/product/generate_pay_link",
                data=checkout_data
            )

            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    return {
                        'success': True,
                        'payment_id': f"paddle_{uuid.uuid4().hex[:8]}",
                        'payment_url': data['response']['url'],
                        'amount': amount,
                        'currency': currency,
                        'gateway': 'paddle',
                        'status': 'pending'
                    }
                else:
                    raise Exception(f"Paddle error: {data['error']['message']}")
            else:
                raise Exception(f"Paddle API error: {response.text}")

        except Exception as e:
            logger.error(f"Paddle payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'paddle'
            }

    # =============================================================================
    # LEMONSQUEEZY - GLOBAL DIGITAL PRODUCTS
    # =============================================================================

    def create_lemonsqueezy_payment(self, amount: float, currency: str, customer_email: str, plan: str) -> Dict[str, Any]:
        """Create Lemonsqueezy payment"""
        try:
            api_key = self.gateways['lemonsqueezy']['api_key']
            store_id = self.gateways['lemonsqueezy']['store_id']

            if not api_key or not store_id:
                raise ValueError("Lemonsqueezy credentials not configured")

            checkout_data = {
                'data': {
                    'type': 'checkouts',
                    'attributes': {
                        'checkout_data': {
                            'email': customer_email,
                            'name': customer_email.split('@')[0]
                        },
                        'checkout_options': {
                            'embed': False,
                            'media': False,
                            'logo': True
                        },
                        'product_options': {
                            'name': f'GPUOptimizer {plan.title()} Plan',
                            'description': f'Monthly subscription to GPUOptimizer {plan} plan',
                            'media': [],
                            'redirect_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/payment/success",
                            'receipt_button_text': 'Go to Dashboard',
                            'receipt_link_url': f"{os.getenv('DOMAIN', 'localhost:5000')}/dashboard"
                        }
                    },
                    'relationships': {
                        'store': {
                            'data': {
                                'type': 'stores',
                                'id': store_id
                            }
                        }
                    }
                }
            }

            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json',
                'Authorization': f'Bearer {api_key}'
            }

            response = requests.post(
                f"{self.gateways['lemonsqueezy']['api_url']}/checkouts",
                headers=headers,
                json=checkout_data
            )

            if response.status_code == 201:
                data = response.json()['data']
                return {
                    'success': True,
                    'payment_id': data['id'],
                    'payment_url': data['attributes']['url'],
                    'amount': amount,
                    'currency': currency,
                    'gateway': 'lemonsqueezy',
                    'status': 'pending'
                }
            else:
                raise Exception(f"Lemonsqueezy API error: {response.text}")

        except Exception as e:
            logger.error(f"Lemonsqueezy payment creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'lemonsqueezy'
            }
