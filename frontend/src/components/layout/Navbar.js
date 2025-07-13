import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard,
  TrendingUp,
  AttachMoney,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { motion } from 'framer-motion';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated, user, logout } = useAuth();
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);

  const navigationItems = [
    { label: 'Features', path: '/#features' },
    { label: 'Pricing', path: '/pricing' },
    { label: 'Documentation', path: '/docs' },
    { label: 'Contact', path: '/contact' },
  ];

  const userMenuItems = [
    { label: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
    { label: 'Analytics', path: '/analytics', icon: <TrendingUp /> },
    { label: 'Billing', path: '/billing', icon: <AttachMoney /> },
    { label: 'Settings', path: '/settings' },
  ];

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
    navigate('/');
  };

  const handleMobileMenuToggle = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const isHomePage = location.pathname === '/';

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          bgcolor: isHomePage ? 'transparent' : 'background.paper',
          color: isHomePage ? 'white' : 'text.primary',
          boxShadow: isHomePage ? 'none' : 1,
          backdropFilter: isHomePage ? 'blur(10px)' : 'none',
          transition: 'all 0.3s ease',
        }}
      >
        <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer',
                mr: 4,
              }}
              onClick={() => navigate('/')}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mr: 2,
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '1.2rem',
                  }}
                >
                  G
                </Typography>
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 'bold',
                  fontSize: '1.5rem',
                  background: isHomePage
                    ? 'white'
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: isHomePage ? 'white' : 'transparent',
                  color: isHomePage ? 'white' : 'transparent',
                }}
              >
                GPUOptimizer
              </Typography>
            </Box>
          </motion.div>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
              <Box sx={{ display: 'flex', gap: 3, ml: 4 }}>
                {navigationItems.map((item, index) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <Button
                      color="inherit"
                      onClick={() => {
                        if (item.path.startsWith('/#')) {
                          navigate('/');
                          setTimeout(() => {
                            const element = document.getElementById(item.path.substring(2));
                            element?.scrollIntoView({ behavior: 'smooth' });
                          }, 100);
                        } else {
                          navigate(item.path);
                        }
                      }}
                      sx={{
                        fontWeight: 500,
                        textTransform: 'none',
                        '&:hover': {
                          bgcolor: isHomePage ? 'rgba(255,255,255,0.1)' : 'rgba(102,126,234,0.1)',
                        },
                      }}
                    >
                      {item.label}
                    </Button>
                  </motion.div>
                ))}
              </Box>

              {/* Auth Buttons */}
              <Box sx={{ ml: 'auto', display: 'flex', gap: 2 }}>
                {isAuthenticated ? (
                  <>
                    <Button
                      color="inherit"
                      onClick={handleUserMenuOpen}
                      sx={{
                        textTransform: 'none',
                        fontWeight: 500,
                      }}
                    >
                      {user?.email}
                    </Button>
                    <Menu
                      anchorEl={userMenuAnchor}
                      open={Boolean(userMenuAnchor)}
                      onClose={handleUserMenuClose}
                      PaperProps={{
                        sx: { mt: 1, minWidth: 200 },
                      }}
                    >
                      {userMenuItems.map((item) => (
                        <MenuItem
                          key={item.label}
                          onClick={() => {
                            navigate(item.path);
                            handleUserMenuClose();
                          }}
                          sx={{ gap: 2 }}
                        >
                          {item.icon}
                          {item.label}
                        </MenuItem>
                      ))}
                      <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                        Logout
                      </MenuItem>
                    </Menu>
                  </>
                ) : (
                  <>
                    <Button
                      color="inherit"
                      onClick={() => navigate('/login')}
                      sx={{ textTransform: 'none', fontWeight: 500 }}
                    >
                      Login
                    </Button>
                    <Button
                      variant="contained"
                      onClick={() => navigate('/signup')}
                      sx={{
                        bgcolor: '#ff6b6b',
                        '&:hover': { bgcolor: '#ff5252' },
                        textTransform: 'none',
                        fontWeight: 600,
                      }}
                    >
                      Get Started
                    </Button>
                  </>
                )}
              </Box>
            </Box>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <Box sx={{ ml: 'auto' }}>
              <IconButton
                color="inherit"
                onClick={handleMobileMenuToggle}
                sx={{ p: 1 }}
              >
                {mobileMenuOpen ? <CloseIcon /> : <MenuIcon />}
              </IconButton>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={handleMobileMenuToggle}
        PaperProps={{
          sx: {
            width: 280,
            bgcolor: 'background.paper',
          },
        }}
      >
        <Box sx={{ p: 2, pt: 8 }}>
          <List>
            {navigationItems.map((item) => (
              <ListItem key={item.label} disablePadding>
                <ListItemButton
                  onClick={() => {
                    if (item.path.startsWith('/#')) {
                      navigate('/');
                      setTimeout(() => {
                        const element = document.getElementById(item.path.substring(2));
                        element?.scrollIntoView({ behavior: 'smooth' });
                      }, 100);
                    } else {
                      navigate(item.path);
                    }
                    setMobileMenuOpen(false);
                  }}
                >
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}

            {isAuthenticated ? (
              <>
                {userMenuItems.map((item) => (
                  <ListItem key={item.label} disablePadding>
                    <ListItemButton
                      onClick={() => {
                        navigate(item.path);
                        setMobileMenuOpen(false);
                      }}
                    >
                      <Box sx={{ mr: 2 }}>{item.icon}</Box>
                      <ListItemText primary={item.label} />
                    </ListItemButton>
                  </ListItem>
                ))}
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    sx={{ color: 'error.main' }}
                  >
                    <ListItemText primary="Logout" />
                  </ListItemButton>
                </ListItem>
              </>
            ) : (
              <>
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => {
                      navigate('/login');
                      setMobileMenuOpen(false);
                    }}
                  >
                    <ListItemText primary="Login" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton
                    onClick={() => {
                      navigate('/signup');
                      setMobileMenuOpen(false);
                    }}
                  >
                    <ListItemText primary="Get Started" />
                  </ListItemButton>
                </ListItem>
              </>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Navbar;
