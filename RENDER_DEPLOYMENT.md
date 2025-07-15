# 🎨 Render Deployment Guide

Deploy your GPUOptimizer project to Render in 5 minutes.

## 🚀 **Quick Deploy Steps**

### **Step 1: Push to GitHub**

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: GPUOptimizer complete system"
   ```

2. **Create GitHub Repository**:
   - Go to [github.com/new](https://github.com/new)
   - Repository name: `gpuoptimizer-complete`
   - Make it **Public** (for free Render deployment)
   - **Don't** initialize with README
   - Click **"Create repository"**

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOURUSERNAME/gpuoptimizer-complete.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Deploy to Render**

1. **Go to Render**: [render.com](https://render.com)
2. **Sign up** with GitHub account
3. **Click "New +"** → **"Web Service"**
4. **Connect your repository**: `gpuoptimizer-complete`
5. **Configure deployment**:

   **Basic Settings:**
   - **Name**: `gpuoptimizer`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)` (or closest to you)
   - **Branch**: `main`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python gpu_optimizer_system.py`

6. **Click "Create Web Service"**

### **Step 3: Configure Environment Variables**

In your Render dashboard, go to **Environment** tab and add:

```bash
# Required
SECRET_KEY=your-secret-key-32-characters-minimum
ENCRYPTION_KEY=your-encryption-key-32-characters
FLASK_ENV=production

# Payment Gateways (add as you set them up)
NOWPAYMENTS_API_KEY=your_nowpayments_api_key
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_secret_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_public_key
PADDLE_VENDOR_ID=your_paddle_vendor_id
PADDLE_VENDOR_AUTH_CODE=your_paddle_auth_code

# Email (optional)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### **Step 4: Test Your Deployment**

1. **Wait for deployment** (2-3 minutes)
2. **Visit your app**: `https://gpuoptimizer.onrender.com`
3. **Test health check**: `https://gpuoptimizer.onrender.com/api/health`
4. **Test signup**: Try creating an account

## 🔧 **Render Configuration Files**

Your project includes these Render-optimized files:

### **render.yaml** (Optional - for advanced users)
```yaml
services:
  - type: web
    name: gpuoptimizer
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python gpu_optimizer_system.py
    healthCheckPath: /api/health
```

### **build.sh** (Automatic build script)
- Installs dependencies
- Sets up database
- Prepares application

### **start.sh** (Startup script)
- Configures environment
- Starts the Flask application

## 🌍 **Custom Domain (Optional)**

1. **In Render dashboard** → **Settings** → **Custom Domains**
2. **Add your domain**: `gpuoptimizer.yourdomain.com`
3. **Update DNS** with provided CNAME record
4. **SSL certificate** is automatically provisioned

## 📊 **Monitoring & Logs**

### **View Logs**
- **Render Dashboard** → **Logs** tab
- Real-time application logs
- Error tracking and debugging

### **Health Monitoring**
- **Health Check URL**: `/api/health`
- **Automatic restarts** if health check fails
- **Uptime monitoring** included

### **Performance Metrics**
- **CPU and Memory usage**
- **Request response times**
- **Error rates**

## 🔒 **Security Configuration**

### **Environment Variables**
- ✅ All secrets stored securely
- ✅ No sensitive data in code
- ✅ Automatic encryption

### **HTTPS**
- ✅ Automatic SSL certificates
- ✅ Force HTTPS redirects
- ✅ Security headers enabled

### **Database**
- ✅ SQLite for development
- ✅ Can upgrade to PostgreSQL later
- ✅ Automatic backups

## 💰 **Render Pricing**

### **Free Tier** (Perfect for testing)
- ✅ 750 hours/month
- ✅ Automatic sleep after 15 min inactivity
- ✅ Custom domains
- ✅ SSL certificates

### **Starter Plan** ($7/month)
- ✅ Always-on service
- ✅ No sleep mode
- ✅ Better performance
- ✅ Priority support

## 🚀 **Scaling Options**

### **Vertical Scaling**
- Upgrade to higher CPU/memory plans
- $7/month → $25/month → $85/month

### **Database Scaling**
- Start with SQLite (included)
- Upgrade to PostgreSQL ($7/month)
- Redis for caching ($7/month)

### **CDN & Performance**
- Automatic CDN for static files
- Global edge locations
- Optimized for speed

## 🔄 **Automatic Deployments**

### **GitHub Integration**
- ✅ Auto-deploy on git push
- ✅ Preview deployments for PRs
- ✅ Rollback to previous versions

### **Build Process**
1. **Code push** to GitHub
2. **Automatic build** triggered
3. **Tests run** (if configured)
4. **Deploy** if successful
5. **Health check** verification

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Build Fails**
- Check `requirements.txt` for typos
- Verify Python version compatibility
- Check build logs in Render dashboard

#### **App Won't Start**
- Verify `start command` is correct
- Check environment variables
- Review application logs

#### **Database Errors**
- SQLite file permissions
- Database initialization
- Check disk space

#### **Payment Gateway Issues**
- Verify API keys are correct
- Check webhook URLs
- Test in sandbox mode first

### **Debug Commands**
```bash
# Check logs
curl https://your-app.onrender.com/api/health

# Test payment gateways
curl https://your-app.onrender.com/api/payment/gateways

# View stats
curl https://your-app.onrender.com/api/stats
```

## 📞 **Support**

### **Render Support**
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)

### **GPUOptimizer Support**
- **GitHub Issues**: Create issues in your repository
- **Email**: Use the contact form on your deployed app

## 🎉 **Success Checklist**

- [ ] ✅ Code pushed to GitHub
- [ ] ✅ Render service created
- [ ] ✅ Environment variables configured
- [ ] ✅ App deployed successfully
- [ ] ✅ Health check passing
- [ ] ✅ Payment gateways configured
- [ ] ✅ Custom domain set up (optional)
- [ ] ✅ Monitoring configured

## 🚀 **Next Steps**

1. **Set up payment gateways** using `SIMPLE_PAYMENT_SETUP.md`
2. **Configure custom domain** for professional appearance
3. **Set up monitoring** and alerts
4. **Start marketing** your GPUOptimizer service
5. **Scale up** as you get customers

**🎉 Congratulations! Your GPUOptimizer is now live and ready to generate revenue!**

**Your app will be available at**: `https://gpuoptimizer.onrender.com`
