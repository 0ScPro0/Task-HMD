import { apiClient } from './client';

export const notificationService = {
    async getUserNotifications() {
        try {
            const response = await apiClient.get('/notifications/user');
            return response.data; 
        } catch (error) {
            console.log(error);
            throw error; 
        }
    },

    async readNotification(userNotificationId) {
        try {
            const response = await apiClient.post(`/notifications/user/${userNotificationId}/read`);
            return response.data;
        } catch (error) {
            console.log(error);
            throw error;
        }
    },

};