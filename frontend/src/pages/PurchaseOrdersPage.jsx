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
  Fab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { purchaseOrderAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const PurchaseOrdersPage = () => {
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create', 'edit', 'view'
  const [selectedPO, setSelectedPO] = useState(null);
  const { hasPermission, isAdmin } = useAuth();

  const [formData, setFormData] = useState({
    supplier: '',
    items: [{ name: '', quantity: 1, unit_price: 0 }],
    total_amount: 0,
    notes: '',
  });

  useEffect(() => {
    fetchPurchaseOrders();
  }, []);

  const fetchPurchaseOrders = async () => {
    try {
      setLoading(true);
      const response = await purchaseOrderAPI.getPurchaseOrders();
      setPurchaseOrders(response.data.purchase_orders || []);
    } catch (error) {
      console.error('Error fetching purchase orders:', error);
      setError('載入購買訂單時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (mode, po = null) => {
    setDialogMode(mode);
    setSelectedPO(po);
    
    if (mode === 'create') {
      setFormData({
        supplier: '',
        items: [{ name: '', quantity: 1, unit_price: 0 }],
        total_amount: 0,
        notes: '',
      });
    } else if (po) {
      setFormData({
        supplier: po.supplier,
        items: po.items,
        total_amount: po.total_amount,
        notes: po.notes || '',
      });
    }
    
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedPO(null);
    setError('');
  };

  const handleFormSubmit = async () => {
    try {
      if (dialogMode === 'create') {
        await purchaseOrderAPI.createPurchaseOrder(formData);
      } else if (dialogMode === 'edit') {
        await purchaseOrderAPI.updatePurchaseOrder(selectedPO.po_id, formData);
      }
      
      handleCloseDialog();
      fetchPurchaseOrders();
    } catch (error) {
      console.error('Error saving purchase order:', error);
      setError(error.response?.data?.error || '儲存時發生錯誤');
    }
  };

  const handleDelete = async (poId) => {
    if (window.confirm('確定要刪除這個購買訂單嗎？')) {
      try {
        await purchaseOrderAPI.deletePurchaseOrder(poId);
        fetchPurchaseOrders();
      } catch (error) {
        console.error('Error deleting purchase order:', error);
        setError('刪除時發生錯誤');
      }
    }
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index][field] = field === 'quantity' || field === 'unit_price' ? Number(value) : value;
    
    // 重新計算總金額
    const total = newItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
    
    setFormData({
      ...formData,
      items: newItems,
      total_amount: total,
    });
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { name: '', quantity: 1, unit_price: 0 }],
    });
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      const newItems = formData.items.filter((_, i) => i !== index);
      const total = newItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
      
      setFormData({
        ...formData,
        items: newItems,
        total_amount: total,
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft': return 'default';
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'draft': return '草稿';
      case 'pending': return '待處理';
      case 'approved': return '已批准';
      case 'cancelled': return '已取消';
      default: return status;
    }
  };

  const canCreatePO = isAdmin() || hasPermission('purchase_order_create');

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
          購買訂單管理
        </Typography>
        {canCreatePO && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog('create')}
          >
            建立新訂單
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
              <TableCell>訂單編號</TableCell>
              <TableCell>供應商</TableCell>
              <TableCell>總金額</TableCell>
              <TableCell>狀態</TableCell>
              <TableCell>建立日期</TableCell>
              <TableCell align="right">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {purchaseOrders.map((po) => (
              <TableRow key={po.po_id}>
                <TableCell>{po.po_id.slice(0, 8)}</TableCell>
                <TableCell>{po.supplier}</TableCell>
                <TableCell>${po.total_amount.toLocaleString()}</TableCell>
                <TableCell>
                  <Chip
                    label={getStatusText(po.status)}
                    color={getStatusColor(po.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(po.created_at).toLocaleDateString('zh-TW')}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('view', po)}
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('edit', po)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(po.po_id)}
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
          {dialogMode === 'create' ? '建立購買訂單' :
           dialogMode === 'edit' ? '編輯購買訂單' : '查看購買訂單'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="供應商"
                value={formData.supplier}
                onChange={(e) => setFormData({ ...formData, supplier: e.target.value })}
                disabled={dialogMode === 'view'}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                商品項目
              </Typography>
              {formData.items.map((item, index) => (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="商品名稱"
                        value={item.name}
                        onChange={(e) => handleItemChange(index, 'name', e.target.value)}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <TextField
                        fullWidth
                        label="數量"
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <TextField
                        fullWidth
                        label="單價"
                        type="number"
                        value={item.unit_price}
                        onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                        disabled={dialogMode === 'view'}
                      />
                    </Grid>
                    <Grid item xs={12} sm={2} display="flex" alignItems="center">
                      {dialogMode !== 'view' && (
                        <Button
                          onClick={() => removeItem(index)}
                          disabled={formData.items.length === 1}
                        >
                          移除
                        </Button>
                      )}
                    </Grid>
                  </Grid>
                </Box>
              ))}
              
              {dialogMode !== 'view' && (
                <Button onClick={addItem} variant="outlined">
                  新增商品
                </Button>
              )}
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="總金額"
                value={formData.total_amount}
                disabled
                InputProps={{
                  startAdornment: <Typography>$</Typography>,
                }}
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

export default PurchaseOrdersPage;