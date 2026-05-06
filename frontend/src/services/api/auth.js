import { apiClient } from './client';
import { useAuthStore } from '../../stores/authStore';

// Helper to get store instance without React hooks
const getAuthStore = () => {
    // Note: This is a workaround to use Zustand store outside React components
    // In a real app, you might want to export the store instance directly
    return useAuthStore.getState();
};

export const authService = {
    async register(email, name, surname, patronymic, address, apartment, phone, password) {
        // Формируем объект, преобразуя необязательные поля в null
        const payload = {
            email: email && email.trim() ? email : null,
            name,
            surname,
            patronymic: patronymic && patronymic.trim() ? patronymic : null,
            address: address && address.trim() ? address : null,
            apartment: apartment && apartment.trim() ? apartment : null,
            phone,
            password,
        };
        
        const response = await apiClient.post('/auth/register', payload);
        
        // Store tokens and user data in auth store
        if (response.data?.access_token && response.data?.refresh_token) {
            const { setTokens } = getAuthStore();
            setTokens(response.data.access_token, response.data.refresh_token, response.data.user);
        }
        
        return response;
    },

    async login(phone, password) {
        const response = await apiClient.post('/auth/login', { phone, password });
        
        // Store tokens and user data in auth store
        if (response.data?.access_token && response.data?.refresh_token) {
            const { setTokens } = getAuthStore();
            setTokens(response.data.access_token, response.data.refresh_token, response.data.user);
        }
        
        return response;
    },

    // services/api/auth.ts
    async refresh(refreshToken) {
        const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
        
        if (response.data?.access_token) {
            const { setTokens, refreshToken: currentRefreshToken, user } = getAuthStore();
            const newRefreshToken = response.data.refresh_token || currentRefreshToken;
            setTokens(response.data.access_token, newRefreshToken, user);
        }
        
        return response.data; // Возвращаем data, а не весь response
    },

    async logout() {
        try {
            await apiClient.post('/auth/logout');
        } finally {
            // Clear tokens from store regardless of API success
            const { clearTokens } = getAuthStore();
            clearTokens();
        }
    },
    
    async getCurrentUser() {
            try {
                const response = await apiClient.get('/users/me');
                return response.data;
            } catch (error) {
                console.error('Ошибка получения текущего пользователя:', error);
                throw error;
            }
    },

};
