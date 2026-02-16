import api from './api';

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    const { access_token, user } = response.data;
    
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.clear();
    }
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('accessToken');
  },
};

export const doctorService = {
  getAll: async (params) => {
    const response = await api.get('/doctors', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/doctors/${id}`);
    return response.data;
  },

  search: async (searchParams) => {
    const response = await api.get('/doctors/search', { params: searchParams });
    return response.data;
  },

  getAvailability: async (doctorId, date) => {
    const response = await api.get(`/doctors/${doctorId}/availability`, {
      params: { date },
    });
    return response.data;
  },
};

export const appointmentService = {
  create: async (appointmentData) => {
    const response = await api.post('/appointments', appointmentData);
    return response.data;
  },

  getAll: async (params) => {
    const response = await api.get('/appointments', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/appointments/${id}`);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/appointments/${id}`, data);
    return response.data;
  },

  updateStatus: async (id, statusData) => {
    const response = await api.patch(`/appointments/${id}/status`, statusData);
    return response.data;
  },

  cancel: async (id, reason) => {
    const response = await api.post(`/appointments/${id}/cancel`, { reason });
    return response.data;
  },
};

export const prescriptionService = {
  getAll: async (params) => {
    const response = await api.get('/prescriptions', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/prescriptions/${id}`);
    return response.data;
  },

  create: async (prescriptionData) => {
    const response = await api.post('/prescriptions', prescriptionData);
    return response.data;
  },

  downloadPDF: async (id) => {
    const response = await api.get(`/prescriptions/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const medicalHistoryService = {
  getAll: async (params) => {
    const response = await api.get('/medical-records', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/medical-records/${id}`);
    return response.data;
  },

  getPatientHistory: async (patientId) => {
    const response = await api.get(`/medical-records/patient/${patientId}`);
    return response.data;
  },

  create: async (historyData) => {
    const response = await api.post('/medical-records', historyData);
    return response.data;
  },

  update: async (id, historyData) => {
    const response = await api.put(`/medical-records/${id}`, historyData);
    return response.data;
  },
};

export const reportService = {
  upload: async (formData) => {
    const response = await api.post('/reports', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getAll: async (params) => {
    const response = await api.get('/reports', { params });
    return response.data;
  },

  download: async (id) => {
    const response = await api.get(`/reports/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const billingService = {
  getAll: async (params) => {
    const response = await api.get('/billing', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/billing/${id}`);
    return response.data;
  },

  create: async (billData) => {
    const response = await api.post('/billing', billData);
    return response.data;
  },

  updatePaymentStatus: async (id, paymentData) => {
    const response = await api.patch(`/billing/${id}/pay`, paymentData);
    return response.data;
  },
};
