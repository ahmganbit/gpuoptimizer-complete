# 🔌 GPUOptimizer API Documentation

Complete API reference for the GPUOptimizer autonomous revenue system.

## 🌐 Base URL
```
Production: https://api.gpuoptimizer.ai
Staging: https://staging-api.gpuoptimizer.ai
Local: http://localhost:5000
```

## 🔐 Authentication

### API Key Authentication
```bash
# Include in headers
Authorization: Bearer YOUR_API_KEY

# Or as query parameter
?api_key=YOUR_API_KEY
```

### JWT Authentication
```bash
# Login to get JWT token
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Use token in subsequent requests
Authorization: Bearer JWT_TOKEN
```

## 📋 Core Endpoints

### 🏥 Health & Status

#### Health Check
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "payment": "healthy"
  }
}
```

#### System Statistics
```bash
GET /api/stats
```
**Response:**
```json
{
  "total_customers": 1250,
  "total_revenue": 125000.50,
  "monthly_revenue": 15000.00,
  "active_gpus": 3420,
  "cost_savings": 2100000.00,
  "uptime": "99.9%"
}
```

### 👤 User Management

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe",
  "company": "Tech Corp"
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Get User Profile
```bash
GET /api/user/profile
Authorization: Bearer JWT_TOKEN
```

#### Update User Profile
```bash
PUT /api/user/profile
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "name": "John Smith",
  "company": "New Tech Corp",
  "phone": "+1234567890"
}
```

### 🖥️ GPU Management

#### List User's GPUs
```bash
GET /api/gpus
Authorization: Bearer JWT_TOKEN
```
**Response:**
```json
{
  "gpus": [
    {
      "id": "gpu_123",
      "name": "Training GPU 1",
      "provider": "aws",
      "instance_type": "p3.2xlarge",
      "status": "active",
      "utilization": 85.5,
      "cost_per_hour": 3.06,
      "savings": 1250.00,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

#### Add New GPU
```bash
POST /api/gpus
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "name": "Training GPU 2",
  "provider": "aws",
  "instance_type": "p3.8xlarge",
  "region": "us-east-1",
  "access_key": "AKIA...",
  "secret_key": "..."
}
```

#### Get GPU Details
```bash
GET /api/gpus/{gpu_id}
Authorization: Bearer JWT_TOKEN
```

#### Get GPU Metrics
```bash
GET /api/gpus/{gpu_id}/metrics
Authorization: Bearer JWT_TOKEN
Query Parameters:
- start_date: 2024-01-01
- end_date: 2024-01-31
- interval: hour|day|week
```

#### Get Optimization Recommendations
```bash
GET /api/gpus/{gpu_id}/optimize
Authorization: Bearer JWT_TOKEN
```
**Response:**
```json
{
  "recommendations": [
    {
      "type": "instance_type",
      "current": "p3.2xlarge",
      "recommended": "p3.xlarge",
      "potential_savings": 450.00,
      "confidence": 0.85
    },
    {
      "type": "scheduling",
      "recommendation": "Use spot instances for training",
      "potential_savings": 800.00,
      "confidence": 0.92
    }
  ],
  "total_potential_savings": 1250.00
}
```

### 💰 Revenue & Billing

#### Get Revenue Statistics
```bash
GET /api/revenue/stats
Authorization: Bearer JWT_TOKEN
Query Parameters:
- period: day|week|month|quarter|year
- start_date: 2024-01-01
- end_date: 2024-01-31
```

#### Get Customer Analytics
```bash
GET /api/analytics/customers
Authorization: Bearer JWT_TOKEN
```

#### Create Payment Intent
```bash
POST /api/payments/intent
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "amount": 4900,
  "currency": "usd",
  "plan": "professional"
}
```

#### Process Subscription
```bash
POST /api/subscriptions
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "plan": "professional",
  "payment_method": "pm_1234567890"
}
```

#### Get Billing History
```bash
GET /api/billing/history
Authorization: Bearer JWT_TOKEN
```

### 🤖 Automation & AI

#### Get Lead Generation Stats
```bash
GET /api/automation/leads
Authorization: Bearer JWT_TOKEN
```

#### Trigger Lead Generation
```bash
POST /api/automation/leads/generate
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "channels": ["github", "twitter", "linkedin"],
  "keywords": ["gpu optimization", "ml costs"],
  "limit": 50
}
```

#### Get Marketing Campaigns
```bash
GET /api/marketing/campaigns
Authorization: Bearer JWT_TOKEN
```

#### Create Marketing Campaign
```bash
POST /api/marketing/campaigns
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "name": "Q1 GPU Optimization Campaign",
  "type": "email",
  "target_audience": "ml_engineers",
  "content": "...",
  "schedule": "2024-02-01T09:00:00Z"
}
```

### 🎯 Growth & Referrals

#### Get Referral Stats
```bash
GET /api/referrals/stats
Authorization: Bearer JWT_TOKEN
```

#### Create Referral Link
```bash
POST /api/referrals/create
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "campaign": "friend_referral",
  "reward_type": "credits",
  "reward_value": 50
}
```

#### Track Referral Click
```bash
POST /api/referrals/track
Content-Type: application/json

{
  "referral_code": "GPU123ABC",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "landing_page": "/signup"
}
```

### 📊 Analytics & Reporting

#### Get Dashboard Data
```bash
GET /api/dashboard
Authorization: Bearer JWT_TOKEN
```

#### Generate Custom Report
```bash
POST /api/reports/generate
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "type": "revenue_analysis",
  "period": "last_30_days",
  "format": "pdf",
  "email": true
}
```

#### Get Growth Metrics
```bash
GET /api/analytics/growth
Authorization: Bearer JWT_TOKEN
Query Parameters:
- metric: mrr|arr|churn|ltv|cac
- period: day|week|month|quarter
```

### 🔧 Admin Endpoints

#### Get All Users (Admin Only)
```bash
GET /api/admin/users
Authorization: Bearer ADMIN_JWT_TOKEN
Query Parameters:
- page: 1
- per_page: 50
- status: active|inactive|trial
```

#### Get System Metrics (Admin Only)
```bash
GET /api/admin/metrics
Authorization: Bearer ADMIN_JWT_TOKEN
```

#### Manage Subscriptions (Admin Only)
```bash
PUT /api/admin/subscriptions/{subscription_id}
Authorization: Bearer ADMIN_JWT_TOKEN
Content-Type: application/json

{
  "status": "active",
  "plan": "enterprise",
  "discount": 20
}
```

## 🔄 Webhooks

### Payment Webhooks
```bash
POST /api/webhooks/stripe
POST /api/webhooks/flutterwave
POST /api/webhooks/nowpayments
```

### GitHub Webhooks
```bash
POST /api/webhooks/github
```

## 📝 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": "Email is required"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🚦 Rate Limiting

- **Free Tier**: 100 requests/hour
- **Professional**: 1,000 requests/hour  
- **Enterprise**: 10,000 requests/hour
- **Custom**: Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## 🔒 Security

### HTTPS Only
All API endpoints require HTTPS in production.

### Input Validation
All inputs are validated and sanitized.

### SQL Injection Protection
Parameterized queries prevent SQL injection.

### CORS Configuration
```javascript
// Allowed origins
const allowedOrigins = [
  'https://gpuoptimizer.ai',
  'https://app.gpuoptimizer.ai',
  'http://localhost:3000' // Development only
];
```

## 📚 SDKs & Libraries

### Python SDK
```python
from gpuoptimizer import GPUOptimizerClient

client = GPUOptimizerClient(api_key='your_api_key')
gpus = client.gpus.list()
```

### JavaScript SDK
```javascript
import { GPUOptimizer } from '@gpuoptimizer/sdk';

const client = new GPUOptimizer({ apiKey: 'your_api_key' });
const gpus = await client.gpus.list();
```

### cURL Examples
```bash
# Get all GPUs
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.gpuoptimizer.ai/api/gpus

# Add new GPU
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"name":"GPU 1","provider":"aws"}' \
     https://api.gpuoptimizer.ai/api/gpus
```

## 🐛 Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## 📞 Support

- **API Documentation**: [docs.gpuoptimizer.ai/api](https://docs.gpuoptimizer.ai/api)
- **Postman Collection**: [Download](https://api.gpuoptimizer.ai/postman)
- **OpenAPI Spec**: [Download](https://api.gpuoptimizer.ai/openapi.json)
- **Support Email**: api-support@gpuoptimizer.ai

**🚀 Ready to integrate? Get your API key at [app.gpuoptimizer.ai/api-keys](https://app.gpuoptimizer.ai/api-keys)**
