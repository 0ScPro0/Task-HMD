import { apiClient } from './client';
import { useAuthStore } from '../../stores/authStore';

// Helper to get store instance without React hooks
const getAuthStore = () => {
    return useAuthStore.getState();
};

export const userService = {
    /**
     * Get current user profile
     * @returns {Promise<Object>} User profile data
     */
    async getCurrentUser() {
        try {
            const response = await apiClient.get('/users/me');
            return response.data;
        } catch (error) {
            console.error('Error fetching current user:', error);
            throw error;
        }
    },

    /**
     * Update current user profile
     * @param {Object} userData - User data to update
     * @param {string} userData.name - User name
     * @param {string} userData.surname - User surname
     * @param {string} userData.patronymic - User patronymic (optional)
     * @param {string} userData.phone - User phone
     * @param {string} userData.email - User email (optional)
     * @param {string} userData.address - User address (optional)
     * @param {string} userData.apartment - User apartment (optional)
     * @returns {Promise<Object>} Updated user profile
     */
    async updateProfile(userData) {
        try {
            const response = await apiClient.patch('/users/me', userData);
            
            // Update auth store with new user data
            const { setUserData } = getAuthStore();
            if (setUserData) {
                setUserData(response.data);
            }
            
            return response.data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            throw error;
        }
    }
};