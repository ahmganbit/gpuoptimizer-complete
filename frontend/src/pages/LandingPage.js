import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  Chip,
  Avatar,
  Rating,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Security,
  Analytics,
  CloudQueue,
  MonetizationOn,
  CheckCircle,
  Star,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

const LandingPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalSavings: 2500000,
    activeUsers: 15000,
    gpusMonitored: 50000,
  });

  const [heroRef, heroInView] = useInView({ threshold: 0.1, triggerOnce: true });
  const [featuresRef, featuresInView] = useInView({ threshold: 0.1, triggerOnce: true });
  const [statsRef, statsInView] = useInView({ threshold: 0.1, triggerOnce: true });

  useEffect(() => {
    // Fetch real stats
    const fetchStats = async () => {
      try {
        const data = await apiService.getStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
  }, []);

  const handleGetStarted = async () => {
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.submitLead({
        email,
        source: 'landing_page',
        interest: 'get_started',
      });

      if (response.success) {
        toast.success('Thanks! We\'ll be in touch soon.');
        navigate('/signup', { state: { email } });
      }
    } catch (error) {
      toast.error('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <TrendingUp />,
      title: 'Cost Optimization',
      description: 'Reduce GPU costs by up to 70% with intelligent monitoring and optimization algorithms.',
    },
    {
      icon: <Speed />,
      title: 'Real-time Monitoring',
      description: 'Monitor GPU utilization, memory usage, and performance metrics in real-time.',
    },
    {
      icon: <Analytics />,
      title: 'Advanced Analytics',
      description: 'Get detailed insights and recommendations to optimize your GPU infrastructure.',
    },
    {
      icon: <Security />,
      title: 'Enterprise Security',
      description: 'Bank-grade security with encryption, compliance, and audit trails.',
    },
    {
      icon: <CloudQueue />,
      title: 'Multi-Cloud Support',
      description: 'Works with AWS, GCP, Azure, and on-premise GPU infrastructure.',
    },
    {
      icon: <MonetizationOn />,
      title: 'ROI Tracking',
      description: 'Track your return on investment with detailed cost savings reports.',
    },
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'CTO, AI Startup',
      avatar: '/avatars/sarah.jpg',
      rating: 5,
      text: 'GPUOptimizer saved us $50k in the first month. The insights are incredible!',
    },
    {
      name: 'Michael Rodriguez',
      role: 'ML Engineer, TechCorp',
      avatar: '/avatars/michael.jpg',
      rating: 5,
      text: 'Finally, a tool that actually helps optimize our GPU spending. Highly recommended!',
    },
    {
      name: 'Dr. Emily Watson',
      role: 'Research Director',
      avatar: '/avatars/emily.jpg',
      rating: 5,
      text: 'The real-time monitoring has transformed how we manage our research infrastructure.',
    },
  ];

  return (
    <Box>
      <Navbar />
      
      {/* Hero Section */}
      <Box
        ref={heroRef}
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={heroInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8 }}
          >
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    fontWeight: 800,
                    mb: 3,
                    lineHeight: 1.2,
                  }}
                >
                  Save 70% on GPU Costs with AI-Powered Optimization
                </Typography>
                
                <Typography
                  variant="h5"
                  sx={{
                    mb: 4,
                    opacity: 0.9,
                    fontWeight: 400,
                    lineHeight: 1.6,
                  }}
                >
                  Monitor, analyze, and optimize your GPU infrastructure in real-time. 
                  Join 15,000+ companies already saving millions on GPU costs.
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
                    label="Setup in 5 minutes"
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 2, maxWidth: 500 }}>
                  <TextField
                    fullWidth
                    placeholder="Enter your work email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    sx={{
                      bgcolor: 'white',
                      borderRadius: 2,
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': { border: 'none' },
                      },
                    }}
                  />
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleGetStarted}
                    disabled={loading}
                    sx={{
                      bgcolor: '#ff6b6b',
                      '&:hover': { bgcolor: '#ff5252' },
                      px: 4,
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {loading ? 'Processing...' : 'Get Started Free'}
                  </Button>
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={heroInView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.8, delay: 0.2 }}
                >
                  <Box
                    component="img"
                    src="/images/dashboard-preview.png"
                    alt="GPUOptimizer Dashboard"
                    sx={{
                      width: '100%',
                      height: 'auto',
                      borderRadius: 3,
                      boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
                    }}
                  />
                </motion.div>
              </Grid>
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box ref={statsRef} sx={{ py: 8, bgcolor: 'background.paper' }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={statsInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <Grid container spacing={4} textAlign="center">
              <Grid item xs={12} md={4}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  ${(stats.totalSavings / 1000000).toFixed(1)}M+
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Total Savings Generated
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {(stats.activeUsers / 1000).toFixed(0)}K+
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Active Users
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {(stats.gpusMonitored / 1000).toFixed(0)}K+
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  GPUs Monitored
                </Typography>
              </Grid>
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* Features Section */}
      <Box ref={featuresRef} sx={{ py: 12, bgcolor: 'background.default' }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={featuresInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <Typography
              variant="h2"
              textAlign="center"
              sx={{ mb: 2, fontWeight: 700 }}
            >
              Why Choose GPUOptimizer?
            </Typography>
            
            <Typography
              variant="h6"
              textAlign="center"
              color="text.secondary"
              sx={{ mb: 8, maxWidth: 600, mx: 'auto' }}
            >
              Powerful features designed to maximize your GPU ROI and minimize costs
            </Typography>

            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={featuresInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                  >
                    <Card
                      sx={{
                        height: '100%',
                        textAlign: 'center',
                        p: 3,
                        transition: 'transform 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-8px)',
                          boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                        },
                      }}
                    >
                      <Box
                        sx={{
                          display: 'inline-flex',
                          p: 2,
                          borderRadius: '50%',
                          bgcolor: 'primary.main',
                          color: 'white',
                          mb: 3,
                        }}
                      >
                        {feature.icon}
                      </Box>
                      
                      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                      
                      <Typography color="text.secondary" sx={{ lineHeight: 1.6 }}>
                        {feature.description}
                      </Typography>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box sx={{ py: 12, bgcolor: 'background.paper' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            textAlign="center"
            sx={{ mb: 2, fontWeight: 700 }}
          >
            Loved by Developers Worldwide
          </Typography>
          
          <Typography
            variant="h6"
            textAlign="center"
            color="text.secondary"
            sx={{ mb: 8 }}
          >
            See what our customers are saying
          </Typography>

          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card sx={{ height: '100%', p: 3 }}>
                  <CardContent>
                    <Rating value={testimonial.rating} readOnly sx={{ mb: 2 }} />
                    
                    <Typography
                      variant="body1"
                      sx={{ mb: 3, fontStyle: 'italic', lineHeight: 1.6 }}
                    >
                      "{testimonial.text}"
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar src={testimonial.avatar} />
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {testimonial.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {testimonial.role}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box
        sx={{
          py: 12,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" sx={{ mb: 3, fontWeight: 700 }}>
            Ready to Optimize Your GPU Costs?
          </Typography>
          
          <Typography variant="h6" sx={{ mb: 6, opacity: 0.9 }}>
            Join thousands of companies saving millions on GPU infrastructure costs
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/signup')}
            sx={{
              bgcolor: '#ff6b6b',
              '&:hover': { bgcolor: '#ff5252' },
              px: 6,
              py: 2,
              fontSize: '1.2rem',
            }}
          >
            Start Free Trial
          </Button>
        </Container>
      </Box>

      <Footer />
    </Box>
  );
};

export default LandingPage;
