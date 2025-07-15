# 💳 Worldwide Payment Setup Guide

Complete guide to set up payment processing that works in **every country** including crypto payments.

## 🌍 **Why This Payment System?**

**Problem with Stripe**: Restricted in 100+ countries including:
- Most of Africa
- Many Asian countries  
- Eastern Europe
- Latin America
- Middle East

**Our Solution**: Multiple worldwide-accessible payment gateways:
- ✅ **Crypto payments** - Works everywhere, no restrictions
- ✅ **PayPal** - 200+ countries
- ✅ **Regional specialists** - Razorpay (Asia), Flutterwave (Africa)
- ✅ **Global SaaS billing** - Paddle (worldwide)

## 🚀 **Quick Setup (5 minutes)**

### **Option 1: Crypto Only (Easiest)**
*Works everywhere, no restrictions, instant setup*

1. **Sign up for NOWPayments**: [nowpayments.io](https://nowpayments.io)
2. **Get API key**: Dashboard → API Keys
3. **Add to .env**:
   ```bash
   NOWPAYMENTS_API_KEY=your_api_key_here
   NOWPAYMENTS_IPN_SECRET=your_ipn_secret
   ```
4. **Done!** Accepts Bitcoin, Ethereum, USDT, and 100+ cryptocurrencies

### **Option 2: PayPal + Crypto (Recommended)**
*Covers 99% of the world*

1. **NOWPayments setup** (above)
2. **PayPal Developer Account**: [developer.paypal.com](https://developer.paypal.com)
3. **Create app** → Get Client ID & Secret
4. **Add to .env**:
   ```bash
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_CLIENT_SECRET=your_client_secret
   PAYPAL_MODE=sandbox
   ```

## 🔧 **Complete Setup Guide**

### **1. NOWPayments (Crypto) - PRIORITY 1**
**Coverage**: Worldwide 🌍  
**Currencies**: BTC, ETH, USDT, LTC, BCH, XRP, ADA, DOT, LINK, UNI  
**Fees**: 0.5%  
**Setup Time**: 2 minutes

```bash
# 1. Sign up: https://nowpayments.io
# 2. Verify email
# 3. Go to API Keys section
# 4. Generate API key
# 5. Add to .env:
NOWPAYMENTS_API_KEY=your_api_key_here
NOWPAYMENTS_IPN_SECRET=your_ipn_secret
```

### **2. PayPal - PRIORITY 2**
**Coverage**: 200+ countries 🌍  
**Currencies**: USD, EUR, GBP, CAD, AUD, JPY  
**Fees**: 2.9% + $0.30  
**Setup Time**: 5 minutes

```bash
# 1. Sign up: https://developer.paypal.com
# 2. Create new app
# 3. Get Client ID & Secret
# 4. Add to .env:
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_MODE=sandbox  # Change to 'live' for production
```

### **3. Razorpay (Asia) - PRIORITY 3**
**Coverage**: India, Malaysia, UAE, Singapore, Thailand 🇮🇳🇲🇾🇦🇪  
**Currencies**: INR, MYR, AED, SGD, THB  
**Fees**: 2% + ₹2  
**Setup Time**: 10 minutes

```bash
# 1. Sign up: https://dashboard.razorpay.com
# 2. Complete KYC verification
# 3. Go to Settings → API Keys
# 4. Generate keys
# 5. Add to .env:
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

### **4. Flutterwave (Africa) - PRIORITY 4**
**Coverage**: Nigeria, Ghana, Kenya, Uganda, South Africa, Tanzania 🌍  
**Currencies**: NGN, GHS, KES, UGX, ZAR, TZS, USD, GBP  
**Fees**: 1.4% + ₦100  
**Setup Time**: 15 minutes

```bash
# 1. Sign up: https://dashboard.flutterwave.com
# 2. Complete business verification
# 3. Go to Settings → API Keys
# 4. Get keys
# 5. Add to .env:
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_secret_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_public_key
```

### **5. Paddle (Global SaaS) - PRIORITY 5**
**Coverage**: Worldwide 🌍  
**Currencies**: USD, EUR, GBP, CAD, AUD, JPY, CHF  
**Fees**: 5% + $0.50  
**Setup Time**: 20 minutes

```bash
# 1. Sign up: https://vendors.paddle.com
# 2. Complete seller verification
# 3. Go to Developer Tools → Authentication
# 4. Get vendor credentials
# 5. Add to .env:
PADDLE_VENDOR_ID=your_vendor_id
PADDLE_VENDOR_AUTH_CODE=your_auth_code
```

## 🎯 **Recommended Setup by Region**

### **🌍 Global/Unknown**
```bash
NOWPAYMENTS_API_KEY=your_key    # Crypto (works everywhere)
PAYPAL_CLIENT_ID=your_id        # Traditional payments
```

### **🇺🇸 North America**
```bash
PAYPAL_CLIENT_ID=your_id        # Primary
NOWPAYMENTS_API_KEY=your_key    # Crypto option
```

### **🇪🇺 Europe**
```bash
PAYPAL_CLIENT_ID=your_id        # Primary
PADDLE_VENDOR_ID=your_id        # SaaS billing
NOWPAYMENTS_API_KEY=your_key    # Crypto option
```

### **🇮🇳 Asia (India/SEA)**
```bash
RAZORPAY_KEY_ID=your_id         # Primary
PAYPAL_CLIENT_ID=your_id        # Secondary
NOWPAYMENTS_API_KEY=your_key    # Crypto option
```

### **🌍 Africa**
```bash
FLUTTERWAVE_SECRET_KEY=your_key # Primary
NOWPAYMENTS_API_KEY=your_key    # Crypto option
PAYPAL_CLIENT_ID=your_id        # If available
```

## 🔄 **How It Works**

### **Automatic Gateway Selection**
The system automatically selects the best payment gateway based on:
1. **Customer's country**
2. **Available gateways**
3. **Currency preference**
4. **Gateway reliability**

### **Payment Flow**
```
1. Customer selects plan
2. System detects country
3. Shows available payment methods
4. Customer chooses preferred method
5. Redirects to payment gateway
6. Processes payment
7. Activates subscription
```

### **Fallback System**
```
Primary Gateway Fails
↓
Try Secondary Gateway
↓
Try Crypto Payment
↓
Show Manual Payment Option
```

## 🧪 **Testing**

### **Test Mode Setup**
```bash
# NOWPayments
NOWPAYMENTS_API_KEY=your_sandbox_key

# PayPal
PAYPAL_MODE=sandbox

# Razorpay
# Use test keys (start with rzp_test_)

# Flutterwave
# Use test keys (FLWSECK_TEST-)
```

### **Test Payments**
1. **Crypto**: Use testnet cryptocurrencies
2. **PayPal**: Use sandbox accounts
3. **Razorpay**: Use test card numbers
4. **Flutterwave**: Use test card numbers

## 📊 **Monitoring & Analytics**

### **Payment Success Rates**
```bash
# Check gateway performance
curl https://your-domain.com/api/payment/stats

# Response:
{
  "nowpayments": {"success_rate": 95.2, "avg_time": "2.3s"},
  "paypal": {"success_rate": 98.1, "avg_time": "1.8s"},
  "razorpay": {"success_rate": 97.5, "avg_time": "2.1s"}
}
```

### **Revenue by Gateway**
```bash
# Check revenue breakdown
curl https://your-domain.com/api/revenue/by-gateway

# Response:
{
  "total_revenue": 125000,
  "by_gateway": {
    "nowpayments": 45000,
    "paypal": 65000,
    "razorpay": 15000
  }
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"No payment gateways available"**
- Check API keys in .env file
- Verify internet connection
- Check gateway status pages

#### **"Payment failed"**
- Check gateway-specific logs
- Verify webhook URLs
- Check currency support

#### **"Webhook not received"**
- Verify webhook URLs are accessible
- Check firewall settings
- Test webhook endpoints manually

### **Debug Mode**
```bash
# Enable debug logging
DEBUG=true
LOG_LEVEL=DEBUG

# Check logs
tail -f logs/payment.log
```

## 🔒 **Security**

### **API Key Security**
- ✅ Store in environment variables
- ✅ Use different keys for test/production
- ✅ Rotate keys regularly
- ❌ Never commit keys to git

### **Webhook Security**
- ✅ Verify webhook signatures
- ✅ Use HTTPS only
- ✅ Validate payload structure
- ✅ Implement replay protection

## 💰 **Cost Comparison**

| Gateway | Fee | Coverage | Setup |
|---------|-----|----------|-------|
| NOWPayments | 0.5% | Worldwide | Easy |
| PayPal | 2.9% + $0.30 | 200+ countries | Easy |
| Razorpay | 2% + ₹2 | Asia | Medium |
| Flutterwave | 1.4% + ₦100 | Africa | Medium |
| Paddle | 5% + $0.50 | Worldwide | Hard |

## 🎉 **Success!**

Once configured, your payment system will:
- ✅ Accept payments from **every country**
- ✅ Support **traditional and crypto** payments
- ✅ Automatically **select best gateway**
- ✅ Handle **currency conversion**
- ✅ Provide **detailed analytics**

**Ready to accept payments worldwide!** 🚀
