import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Receipt,
  LocalShipping,
  TrendingUp,
  CheckCircle,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { purchaseOrderAPI, shipmentAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const [stats, setStats] = useState({
    totalPOs: 0,
    pendingPOs: 0,
    totalShipments: 0,
    deliveredShipments: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [poResponse, shipmentResponse] = await Promise.all([
        purchaseOrderAPI.getPurchaseOrders(),
        shipmentAPI.getShipments(),
      ]);

      const purchaseOrders = poResponse.data.purchase_orders || [];
      const shipments = shipmentResponse.data.shipments || [];

      setStats({
        totalPOs: purchaseOrders.length,
        pendingPOs: purchaseOrders.filter(po => po.status === 'pending').length,
        totalShipments: shipments.length,
        deliveredShipments: shipments.filter(s => s.status === 'delivered').length,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('載入儀表板資料時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: '50%',
              p: 1,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h3" component="div" color={`${color}.main`}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        儀表板
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        歡迎回來，{user?.email}！
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 統計卡片 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="總購買訂單"
            value={stats.totalPOs}
            icon={<Receipt />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="待處理訂單"
            value={stats.pendingPOs}
            icon={<TrendingUp />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="總貨運"
            value={stats.totalShipments}
            icon={<LocalShipping />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="已送達"
            value={stats.deliveredShipments}
            icon={<CheckCircle />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* 快速操作 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          快速操作
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">購買訂單管理</Typography>
                <Typography variant="body2" color="text.secondary">
                  查看、建立和管理購買訂單
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  onClick={() => navigate('/purchase-orders')}
                >
                  前往管理
                </Button>
              </CardActions>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">貨運管理</Typography>
                <Typography variant="body2" color="text.secondary">
                  追蹤和管理貨運狀態
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  onClick={() => navigate('/shipments')}
                >
                  前往管理
                </Button>
              </CardActions>
            </Card>
          </Grid>
          {isAdmin() && (
            <Grid item xs={12} sm={6} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6">使用者管理</Typography>
                  <Typography variant="body2" color="text.secondary">
                    管理系統使用者和權限
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => navigate('/users')}
                  >
                    前往管理
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  );
};

export default DashboardPage;