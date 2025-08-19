import axios from 'axios';

// API 基礎 URL - 在生產環境中應該從環境變數取得
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001';

// 建立 axios 實例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器 - 自動添加認證 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器 - 處理認證錯誤
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 清除本地儲存的認證資訊
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      // 重新導向到登入頁面
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 認證 API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  register: (userData) => api.post('/auth/register', userData),
};

// 使用者管理 API
export const userAPI = {
  getUsers: () => api.get('/users'),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

// 購買訂單 API
export const purchaseOrderAPI = {
  getPurchaseOrders: () => api.get('/purchase-orders'),
  getPurchaseOrder: (poId) => api.get(`/purchase-orders/${poId}`),
  createPurchaseOrder: (poData) => api.post('/purchase-orders', poData),
  updatePurchaseOrder: (poId, poData) => api.put(`/purchase-orders/${poId}`, poData),
  deletePurchaseOrder: (poId) => api.delete(`/purchase-orders/${poId}`),
};

// 貨運 API
export const shipmentAPI = {
  getShipments: (poId = null) => {
    const url = poId ? `/shipments?po_id=${poId}` : '/shipments';
    return api.get(url);
  },
  getShipment: (shipmentId) => api.get(`/shipments/${shipmentId}`),
  createShipment: (shipmentData) => api.post('/shipments', shipmentData),
  updateShipment: (shipmentId, shipmentData) => api.put(`/shipments/${shipmentId}`, shipmentData),
  deleteShipment: (shipmentId) => api.delete(`/shipments/${shipmentId}`),
};

export default api;