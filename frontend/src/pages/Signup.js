import React, { useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Link,
  Divider,
  Chip,
  Alert,
} from '@mui/material';
import { CheckCircle, Email, Security, Speed } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

const Signup = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { signup, loading } = useAuth();
  
  const [email, setEmail] = useState(location.state?.email || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const result = await signup(email);
      
      if (result.success) {
        setShowSuccess(true);
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    } catch (error) {
      console.error('Signup error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const benefits = [
    {
      icon: <Speed />,
      title: 'Instant Setup',
      description: 'Get started in under 5 minutes',
    },
    {
      icon: <Security />,
      title: 'Secure & Private',
      description: 'Enterprise-grade security',
    },
    {
      icon: <CheckCircle />,
      title: 'Free Trial',
      description: '14 days free, no credit card required',
    },
  ];

  if (showSuccess) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card sx={{ maxWidth: 500, textAlign: 'center', p: 4 }}>
            <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Welcome to GPUOptimizer!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Your account has been created successfully. You'll be redirected to your dashboard shortly.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Check your email for your API key and setup instructions.
            </Typography>
          </Card>
        </motion.div>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Box sx={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            {/* Left side - Benefits */}
            <Box sx={{ flex: 1, color: 'white', display: { xs: 'none', md: 'block' } }}>
              <Typography variant="h3" fontWeight="bold" sx={{ mb: 3 }}>
                Start Optimizing Your GPU Costs Today
              </Typography>
              
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                Join thousands of companies saving millions on GPU infrastructure
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
                <Chip
                  icon={<CheckCircle />}
                  label="Free 14-day trial"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
                <Chip
                  icon={<CheckCircle />}
                  label="No credit card required"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
                <Chip
                  icon={<CheckCircle />}
                  label="Cancel anytime"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit.title}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: '50%',
                          bgcolor: 'rgba(255,255,255,0.2)',
                        }}
                      >
                        {benefit.icon}
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight="bold">
                          {benefit.title}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.8 }}>
                          {benefit.description}
                        </Typography>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
              </Box>
            </Box>

            {/* Right side - Signup Form */}
            <Box sx={{ flex: { xs: 1, md: 0.6 } }}>
              <Card sx={{ p: 4, borderRadius: 3 }}>
                <CardContent>
                  <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
                    Get Started Free
                  </Typography>
                  
                  <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
                    Create your account and start optimizing GPU costs in minutes
                  </Typography>

                  <form onSubmit={handleSubmit}>
                    <TextField
                      fullWidth
                      label="Work Email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      sx={{ mb: 3 }}
                      InputProps={{
                        startAdornment: <Email sx={{ mr: 1, color: 'text.secondary' }} />,
                      }}
                    />

                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      size="large"
                      disabled={isSubmitting || loading}
                      sx={{
                        py: 1.5,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        mb: 3,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      }}
                    >
                      {isSubmitting ? 'Creating Account...' : 'Create Free Account'}
                    </Button>

                    <Alert severity="info" sx={{ mb: 3 }}>
                      By signing up, you agree to our Terms of Service and Privacy Policy. 
                      No credit card required for the free trial.
                    </Alert>

                    <Divider sx={{ my: 3 }}>
                      <Typography variant="body2" color="text.secondary">
                        Already have an account?
                      </Typography>
                    </Divider>

                    <Box sx={{ textAlign: 'center' }}>
                      <Link
                        component="button"
                        type="button"
                        variant="body1"
                        onClick={() => navigate('/login')}
                        sx={{ fontWeight: 600 }}
                      >
                        Sign in to your account
                      </Link>
                    </Box>
                  </form>
                </CardContent>
              </Card>

              {/* Trust indicators */}
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="rgba(255,255,255,0.8)" sx={{ mb: 2 }}>
                  Trusted by 15,000+ companies worldwide
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, opacity: 0.7 }}>
                  <Typography variant="body2" color="white">🔒 SOC 2 Compliant</Typography>
                  <Typography variant="body2" color="white">🛡️ GDPR Ready</Typography>
                  <Typography variant="body2" color="white">⚡ 99.9% Uptime</Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Signup;
