# 🚀 GPUOptimizer Deployment Guide

Complete deployment guide for the GPUOptimizer autonomous revenue system.

## 🎯 Quick Deploy Options

### Option 1: One-Click Railway Deploy (Recommended)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click the Railway button above
2. Connect your GitHub account
3. Set environment variables (see below)
4. Deploy automatically!

### Option 2: Render Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option 3: Heroku Deploy
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## 🔧 Environment Variables Setup

### Required Variables (Minimum for Basic Operation)
```bash
SECRET_KEY=your-32-character-secret-key
ENCRYPTION_KEY=your-32-character-encryption-key
DOMAIN=your-domain.com
STRIPE_SECRET_KEY=sk_live_your_stripe_key
SENDGRID_API_KEY=SG.your_sendgrid_key
```

### Recommended Variables (For Full Automation)
```bash
# AI Services
OPENAI_API_KEY=sk-your_openai_key

# Social Media
TWITTER_API_KEY=your_twitter_key
LINKEDIN_CLIENT_ID=your_linkedin_id

# Additional Payment Methods
FLUTTERWAVE_SECRET_KEY=FLWSECK_your_key
NOWPAYMENTS_API_KEY=your_crypto_key
```

## 🏗️ Infrastructure Options

### 1. Cloud Platform Deployment

#### Railway (Recommended for Startups)
- **Cost**: $5-20/month
- **Pros**: Easy setup, automatic scaling, built-in monitoring
- **Best for**: MVP and early growth

```bash
# Deploy to Railway
npm install -g @railway/cli
railway login
railway init
railway up
```

#### AWS (Enterprise Scale)
- **Cost**: $50-500/month
- **Pros**: Full control, enterprise features, global scale
- **Best for**: Large scale operations

```bash
# Deploy with Terraform
cd infrastructure/terraform
terraform init
terraform plan -var-file="production.tfvars"
terraform apply
```

#### Google Cloud Platform
- **Cost**: $30-300/month
- **Pros**: AI/ML integration, competitive pricing
- **Best for**: AI-heavy workloads

#### Azure
- **Cost**: $40-400/month
- **Pros**: Enterprise integration, hybrid cloud
- **Best for**: Enterprise customers

### 2. VPS Deployment

#### DigitalOcean Droplet
```bash
# Create droplet
doctl compute droplet create gpuoptimizer \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --region nyc1

# Deploy with Docker
git clone https://github.com/yourusername/gpuoptimizer-complete.git
cd gpuoptimizer-complete
docker-compose up -d
```

#### Linode
```bash
# Similar to DigitalOcean
linode-cli linodes create \
  --type g6-standard-2 \
  --region us-east \
  --image linode/ubuntu22.04
```

### 3. Kubernetes Deployment

```bash
# Deploy to any Kubernetes cluster
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/configmap.yaml
kubectl apply -f deployment/k8s/
```

## 🔐 Security Configuration

### SSL/TLS Setup
```bash
# Automatic with Let's Encrypt (recommended)
certbot --nginx -d yourdomain.com

# Or use Cloudflare (easier)
# Just point your domain to Cloudflare and enable SSL
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### Environment Security
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use secrets management in production
# Railway: Environment variables in dashboard
# AWS: AWS Secrets Manager
# GCP: Secret Manager
# Azure: Key Vault
```

## 📊 Monitoring Setup

### Application Monitoring
```bash
# Sentry for error tracking
SENTRY_DSN=your_sentry_dsn

# Grafana for metrics
GRAFANA_PASSWORD=your_secure_password
```

### Infrastructure Monitoring
```bash
# Prometheus + Grafana stack included
docker-compose up -d prometheus grafana

# Access dashboards
# Grafana: http://your-domain:3000
# Prometheus: http://your-domain:9090
```

## 🗄️ Database Configuration

### Development (SQLite)
```bash
# Default - no setup required
DATABASE_URL=sqlite:///gpuoptimizer.db
```

### Production (PostgreSQL)
```bash
# Managed database (recommended)
# Railway: Built-in PostgreSQL
# AWS: RDS
# GCP: Cloud SQL
# Azure: Database for PostgreSQL

DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Caching (Redis)
```bash
# Managed Redis (recommended)
REDIS_URL=redis://user:pass@host:6379/0
```

## 🚀 Deployment Steps

### Step 1: Prepare Repository
```bash
# Clone your repository
git clone https://github.com/yourusername/gpuoptimizer-complete.git
cd gpuoptimizer-complete

# Install dependencies locally (optional)
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

### Step 3: Deploy
```bash
# Option A: Cloud platform (Railway/Render/Heroku)
# Just connect GitHub and deploy

# Option B: Docker deployment
docker-compose up -d

# Option C: Manual deployment
python start_autopilot.py
```

### Step 4: Verify Deployment
```bash
# Health check
curl https://your-domain.com/api/health

# Test payment flow
curl -X POST https://your-domain.com/api/test-payment

# Check automation systems
curl https://your-domain.com/api/stats
```

## 🔄 CI/CD Pipeline

### GitHub Actions (Included)
- Automatic testing on pull requests
- Security scanning
- Automatic deployment to staging/production
- Performance testing

### Manual Deployment
```bash
# Build and deploy
./deploy.sh -e production -t aws

# Or use the deployment script
python deploy.py --environment production --platform railway
```

## 📈 Scaling Configuration

### Horizontal Scaling
```bash
# Kubernetes
kubectl scale deployment gpuoptimizer-app --replicas=5

# Docker Swarm
docker service scale gpuoptimizer_app=5
```

### Vertical Scaling
```bash
# Increase resources
# Railway: Upgrade plan in dashboard
# AWS: Change instance type
# Docker: Update resource limits
```

### Database Scaling
```bash
# Read replicas
DATABASE_READ_URL=postgresql://readonly@host:5432/db

# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database URL
echo $DATABASE_URL

# Test connection
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

#### 2. Redis Connection Issues
```bash
# Check Redis URL
echo $REDIS_URL

# Test connection
redis-cli -u $REDIS_URL ping
```

#### 3. Payment Gateway Issues
```bash
# Test Stripe connection
curl -u $STRIPE_SECRET_KEY: https://api.stripe.com/v1/charges
```

#### 4. Email Service Issues
```bash
# Test SendGrid
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f app

# View specific service logs
docker-compose logs -f redis

# Check system resources
docker stats
```

## 🔧 Maintenance

### Regular Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

### Backup Strategy
```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Automated backups (included)
docker-compose run backup
```

### Performance Optimization
```bash
# Monitor performance
docker-compose up -d prometheus grafana

# Optimize database
VACUUM ANALYZE;

# Clear cache
redis-cli FLUSHALL
```

## 📞 Support

- **Documentation**: [docs.gpuoptimizer.ai](https://docs.gpuoptimizer.ai)
- **Discord**: [discord.gg/gpuoptimizer](https://discord.gg/gpuoptimizer)
- **Email**: support@gpuoptimizer.ai
- **GitHub Issues**: [github.com/yourusername/gpuoptimizer-complete/issues](https://github.com/yourusername/gpuoptimizer-complete/issues)

## 🎉 Success Checklist

- [ ] Application deployed and accessible
- [ ] Database connected and migrated
- [ ] Payment processing working
- [ ] Email service configured
- [ ] SSL certificate installed
- [ ] Monitoring dashboards accessible
- [ ] Backup system configured
- [ ] Domain configured with proper DNS
- [ ] Environment variables secured
- [ ] CI/CD pipeline working

**🚀 Congratulations! Your GPUOptimizer autonomous revenue system is now live!**
