import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { shipmentAPI, purchaseOrderAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ShipmentsPage = () => {
  const [shipments, setShipments] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('create');
  const [selectedShipment, setSelectedShipment] = useState(null);
  const { hasPermission, isAdmin } = useAuth();

  const [formData, setFormData] = useState({
    po_id: '',
    tracking_number: '',
    carrier: '',
    status: 'pending',
    estimated_delivery: '',
    actual_delivery: '',
    notes: '',
  });

  useEffect(() => {
    fetchShipments();
    fetchPurchaseOrders();
  }, []);

  const fetchShipments = async () => {
    try {
      setLoading(true);
      const response = await shipmentAPI.getShipments();
      setShipments(response.data.shipments || []);
    } catch (error) {
      console.error('Error fetching shipments:', error);
      setError('載入貨運資料時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  const fetchPurchaseOrders = async () => {
    try {
      const response = await purchaseOrderAPI.getPurchaseOrders();
      setPurchaseOrders(response.data.purchase_orders || []);
    } catch (error) {
      console.error('Error fetching purchase orders:', error);
    }
  };

  const handleOpenDialog = (mode, shipment = null) => {
    setDialogMode(mode);
    setSelectedShipment(shipment);
    
    if (mode === 'create') {
      setFormData({
        po_id: '',
        tracking_number: '',
        carrier: '',
        status: 'pending',
        estimated_delivery: '',
        actual_delivery: '',
        notes: '',
      });
    } else if (shipment) {
      setFormData({
        po_id: shipment.po_id,
        tracking_number: shipment.tracking_number,
        carrier: shipment.carrier,
        status: shipment.status,
        estimated_delivery: shipment.estimated_delivery || '',
        actual_delivery: shipment.actual_delivery || '',
        notes: shipment.notes || '',
      });
    }
    
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedShipment(null);
    setError('');
  };

  const handleFormSubmit = async () => {
    try {
      const submitData = { ...formData };
      
      // 移除空的日期欄位
      if (!submitData.estimated_delivery) delete submitData.estimated_delivery;
      if (!submitData.actual_delivery) delete submitData.actual_delivery;
      
      if (dialogMode === 'create') {
        await shipmentAPI.createShipment(submitData);
      } else if (dialogMode === 'edit') {
        await shipmentAPI.updateShipment(selectedShipment.shipment_id, submitData);
      }
      
      handleCloseDialog();
      fetchShipments();
    } catch (error) {
      console.error('Error saving shipment:', error);
      setError(error.response?.data?.error || '儲存時發生錯誤');
    }
  };

  const handleDelete = async (shipmentId) => {
    if (window.confirm('確定要刪除這個貨運記錄嗎？')) {
      try {
        await shipmentAPI.deleteShipment(shipmentId);
        fetchShipments();
      } catch (error) {
        console.error('Error deleting shipment:', error);
        setError('刪除時發生錯誤');
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'in_transit': return 'info';
      case 'delivered': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return '待發貨';
      case 'in_transit': return '運送中';
      case 'delivered': return '已送達';
      case 'cancelled': return '已取消';
      default: return status;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-TW');
  };

  const canCreateShipment = isAdmin() || hasPermission('shipment_create');

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          貨運管理
        </Typography>
        {canCreateShipment && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog('create')}
          >
            建立新貨運
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>貨運編號</TableCell>
              <TableCell>訂單編號</TableCell>
              <TableCell>追蹤號碼</TableCell>
              <TableCell>承運商</TableCell>
              <TableCell>狀態</TableCell>
              <TableCell>預計送達</TableCell>
              <TableCell>實際送達</TableCell>
              <TableCell align="right">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {shipments.map((shipment) => (
              <TableRow key={shipment.shipment_id}>
                <TableCell>{shipment.shipment_id.slice(0, 8)}</TableCell>
                <TableCell>{shipment.po_id.slice(0, 8)}</TableCell>
                <TableCell>{shipment.tracking_number}</TableCell>
                <TableCell>{shipment.carrier}</TableCell>
                <TableCell>
                  <Chip
                    label={getStatusText(shipment.status)}
                    color={getStatusColor(shipment.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{formatDate(shipment.estimated_delivery)}</TableCell>
                <TableCell>{formatDate(shipment.actual_delivery)}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('view', shipment)}
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('edit', shipment)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(shipment.shipment_id)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 對話框 */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? '建立貨運' :
           dialogMode === 'edit' ? '編輯貨運' : '查看貨運'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth disabled={dialogMode === 'view' || dialogMode === 'edit'}>
                <InputLabel>購買訂單</InputLabel>
                <Select
                  value={formData.po_id}
                  onChange={(e) => setFormData({ ...formData, po_id: e.target.value })}
                  label="購買訂單"
                >
                  {purchaseOrders.map((po) => (
                    <MenuItem key={po.po_id} value={po.po_id}>
                      {po.po_id.slice(0, 8)} - {po.supplier}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="追蹤號碼"
                value={formData.tracking_number}
                onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="承運商"
                value={formData.carrier}
                onChange={(e) => setFormData({ ...formData, carrier: e.target.value })}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth disabled={dialogMode === 'view'}>
                <InputLabel>狀態</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  label="狀態"
                >
                  <MenuItem value="pending">待發貨</MenuItem>
                  <MenuItem value="in_transit">運送中</MenuItem>
                  <MenuItem value="delivered">已送達</MenuItem>
                  <MenuItem value="cancelled">已取消</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="預計送達日期"
                type="date"
                value={formData.estimated_delivery}
                onChange={(e) => setFormData({ ...formData, estimated_delivery: e.target.value })}
                disabled={dialogMode === 'view'}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="實際送達日期"
                type="date"
                value={formData.actual_delivery}
                onChange={(e) => setFormData({ ...formData, actual_delivery: e.target.value })}
                disabled={dialogMode === 'view'}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="備註"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                disabled={dialogMode === 'view'}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            {dialogMode === 'view' ? '關閉' : '取消'}
          </Button>
          {dialogMode !== 'view' && (
            <Button onClick={handleFormSubmit} variant="contained">
              {dialogMode === 'create' ? '建立' : '更新'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ShipmentsPage;