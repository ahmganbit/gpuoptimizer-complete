import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Memory,
  Speed,
  Thermostat,
  AttachMoney,
  Refresh,
  Settings,
  Download,
} from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { useAuth } from '../contexts/AuthContext';
import { apiService, wsService } from '../services/apiService';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';
import DashboardLayout from '../components/layout/DashboardLayout';
import { motion } from 'framer-motion';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard = () => {
  const { user, apiKey, isAuthenticated } = useAuth();
  const [realtimeData, setRealtimeData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch dashboard data
  const { data: analyticsData, isLoading, refetch } = useQuery(
    ['analytics', apiKey],
    () => apiService.getUserAnalytics(apiKey),
    {
      enabled: !!apiKey,
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  useEffect(() => {
    if (!isAuthenticated) return;

    // Setup WebSocket for real-time updates
    wsService.connect(apiKey);
    
    wsService.subscribe('gpu_update', (data) => {
      setRealtimeData(data);
    });

    wsService.subscribe('cost_alert', (data) => {
      toast.error(`Cost Alert: ${data.message}`);
    });

    wsService.subscribe('optimization_suggestion', (data) => {
      toast.success(`Optimization Tip: ${data.message}`);
    });

    return () => {
      wsService.disconnect();
    };
  }, [apiKey, isAuthenticated]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refetch();
      toast.success('Dashboard refreshed');
    } catch (error) {
      toast.error('Failed to refresh dashboard');
    } finally {
      setRefreshing(false);
    }
  };

  const handleExportData = async () => {
    try {
      const blob = await apiService.exportUsageData(apiKey, 'csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gpu-usage-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Data exported successfully');
    } catch (error) {
      toast.error('Failed to export data');
    }
  };

  if (!isAuthenticated) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography variant="h6">Please log in to access the dashboard</Typography>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <Typography variant="h6">Loading dashboard...</Typography>
        </Box>
      </DashboardLayout>
    );
  }

  const mockGpuData = realtimeData || [
    {
      id: 0,
      name: 'Tesla V100',
      utilization: 85,
      memoryUsed: 12000,
      memoryTotal: 16000,
      temperature: 75,
      powerUsage: 250,
      costPerHour: 3.06,
      status: 'active',
    },
    {
      id: 1,
      name: 'Tesla V100',
      utilization: 12,
      memoryUsed: 2000,
      memoryTotal: 16000,
      temperature: 65,
      powerUsage: 80,
      costPerHour: 3.06,
      status: 'idle',
    },
  ];

  const totalCostPerHour = mockGpuData.reduce((sum, gpu) => sum + gpu.costPerHour, 0);
  const potentialSavings = mockGpuData
    .filter(gpu => gpu.utilization < 20)
    .reduce((sum, gpu) => sum + gpu.costPerHour * 0.5, 0);

  const utilizationChartData = {
    labels: ['GPU 0', 'GPU 1'],
    datasets: [
      {
        label: 'GPU Utilization (%)',
        data: mockGpuData.map(gpu => gpu.utilization),
        backgroundColor: ['#667eea', '#764ba2'],
        borderColor: ['#667eea', '#764ba2'],
        borderWidth: 2,
      },
    ],
  };

  const costTrendData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Daily Cost ($)',
        data: [245, 189, 267, 198, 234, 156, 178],
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Optimized Cost ($)',
        data: [180, 142, 201, 149, 176, 117, 134],
        borderColor: '#48bb78',
        backgroundColor: 'rgba(72, 187, 120, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <DashboardLayout>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              GPU Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Welcome back, {user?.email}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportData}
            >
              Export Data
            </Button>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefresh}
              disabled={refreshing}
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Box>
        </Box>

        {/* Key Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Total GPUs
                      </Typography>
                      <Typography variant="h4" fontWeight="bold">
                        {mockGpuData.length}
                      </Typography>
                    </Box>
                    <Memory color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Hourly Cost
                      </Typography>
                      <Typography variant="h4" fontWeight="bold">
                        ${totalCostPerHour.toFixed(2)}
                      </Typography>
                    </Box>
                    <AttachMoney color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Potential Savings
                      </Typography>
                      <Typography variant="h4" fontWeight="bold" color="success.main">
                        ${potentialSavings.toFixed(2)}/hr
                      </Typography>
                    </Box>
                    <TrendingDown color="success" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography color="text.secondary" gutterBottom>
                        Avg Utilization
                      </Typography>
                      <Typography variant="h4" fontWeight="bold">
                        {Math.round(mockGpuData.reduce((sum, gpu) => sum + gpu.utilization, 0) / mockGpuData.length)}%
                      </Typography>
                    </Box>
                    <Speed color="primary" sx={{ fontSize: 40 }} />
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cost Trend Analysis
                </Typography>
                <Box sx={{ height: 300 }}>
                  <Line
                    data={costTrendData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  GPU Utilization
                </Typography>
                <Box sx={{ height: 300 }}>
                  <Doughnut
                    data={utilizationChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* GPU Details Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              GPU Details
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>GPU</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Utilization</TableCell>
                    <TableCell>Memory</TableCell>
                    <TableCell>Temperature</TableCell>
                    <TableCell>Cost/Hour</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockGpuData.map((gpu) => (
                    <TableRow key={gpu.id}>
                      <TableCell>
                        <Typography variant="subtitle2">{gpu.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          GPU {gpu.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={gpu.status}
                          color={gpu.status === 'active' ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={gpu.utilization}
                            sx={{ width: 60, height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="body2">{gpu.utilization}%</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {(gpu.memoryUsed / 1000).toFixed(1)}GB / {(gpu.memoryTotal / 1000).toFixed(1)}GB
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Thermostat fontSize="small" />
                          <Typography variant="body2">{gpu.temperature}°C</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          ${gpu.costPerHour.toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="GPU Settings">
                          <IconButton size="small">
                            <Settings />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Container>
    </DashboardLayout>
  );
};

export default Dashboard;
