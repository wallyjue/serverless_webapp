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
  FormControlLabel,
  Checkbox,
  FormGroup,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { userAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('create');
  const [selectedUser, setSelectedUser] = useState(null);
  const { isAdmin } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'user',
    permissions: [],
  });

  const availablePermissions = [
    { value: 'purchase_order_create', label: '建立購買訂單' },
    { value: 'purchase_order_edit', label: '編輯購買訂單' },
    { value: 'purchase_order_delete', label: '刪除購買訂單' },
    { value: 'shipment_create', label: '建立貨運' },
    { value: 'shipment_edit', label: '編輯貨運' },
    { value: 'shipment_delete', label: '刪除貨運' },
  ];

  useEffect(() => {
    if (isAdmin()) {
      fetchUsers();
    }
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getUsers();
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('載入使用者資料時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (mode, user = null) => {
    setDialogMode(mode);
    setSelectedUser(user);
    
    if (mode === 'create') {
      setFormData({
        email: '',
        password: '',
        role: 'user',
        permissions: [],
      });
    } else if (user) {
      setFormData({
        email: user.email,
        password: '', // 不顯示現有密碼
        role: user.role,
        permissions: user.permissions || [],
      });
    }
    
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedUser(null);
    setError('');
  };

  const handleFormSubmit = async () => {
    try {
      const submitData = { ...formData };
      
      // 編輯模式時，如果密碼為空則不包含密碼欄位
      if (dialogMode === 'edit' && !submitData.password) {
        delete submitData.password;
        delete submitData.email; // email 不允許修改
      }
      
      if (dialogMode === 'create') {
        await userAPI.createUser(submitData);
      } else if (dialogMode === 'edit') {
        await userAPI.updateUser(selectedUser.user_id, submitData);
      }
      
      handleCloseDialog();
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      setError(error.response?.data?.error || '儲存時發生錯誤');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('確定要刪除這個使用者嗎？')) {
      try {
        await userAPI.deleteUser(userId);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        setError('刪除時發生錯誤');
      }
    }
  };

  const handlePermissionChange = (permission, checked) => {
    const newPermissions = checked
      ? [...formData.permissions, permission]
      : formData.permissions.filter(p => p !== permission);
    
    setFormData({ ...formData, permissions: newPermissions });
  };

  const getRoleText = (role) => {
    return role === 'admin' ? '管理者' : '一般使用者';
  };

  const getRoleColor = (role) => {
    return role === 'admin' ? 'error' : 'primary';
  };

  // 只有管理者可以訪問此頁面
  if (!isAdmin()) {
    return (
      <Box>
        <Alert severity="error">
          您沒有權限訪問此頁面
        </Alert>
      </Box>
    );
  }

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
          使用者管理
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog('create')}
        >
          建立新使用者
        </Button>
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
              <TableCell>電子郵件</TableCell>
              <TableCell>角色</TableCell>
              <TableCell>權限</TableCell>
              <TableCell>建立日期</TableCell>
              <TableCell align="right">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.user_id}>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip
                    label={getRoleText(user.role)}
                    color={getRoleColor(user.role)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {user.permissions && user.permissions.length > 0 ? (
                    <Typography variant="body2">
                      {user.permissions.length} 項權限
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      無特殊權限
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString('zh-TW')}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('view', user)}
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog('edit', user)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(user.user_id)}
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
          {dialogMode === 'create' ? '建立使用者' :
           dialogMode === 'edit' ? '編輯使用者' : '查看使用者'}
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
                label="電子郵件"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={dialogMode === 'view' || dialogMode === 'edit'}
              />
            </Grid>
            
            {(dialogMode === 'create' || dialogMode === 'edit') && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={dialogMode === 'edit' ? '新密碼（留空表示不更改）' : '密碼'}
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required={dialogMode === 'create'}
                />
              </Grid>
            )}
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth disabled={dialogMode === 'view'}>
                <InputLabel>角色</InputLabel>
                <Select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  label="角色"
                >
                  <MenuItem value="user">一般使用者</MenuItem>
                  <MenuItem value="admin">管理者</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {formData.role === 'user' && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  權限設定
                </Typography>
                <FormGroup>
                  {availablePermissions.map((permission) => (
                    <FormControlLabel
                      key={permission.value}
                      control={
                        <Checkbox
                          checked={formData.permissions.includes(permission.value)}
                          onChange={(e) => handlePermissionChange(permission.value, e.target.checked)}
                          disabled={dialogMode === 'view'}
                        />
                      }
                      label={permission.label}
                    />
                  ))}
                </FormGroup>
              </Grid>
            )}
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

export default UsersPage;