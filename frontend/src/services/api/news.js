import { apiClient } from './client';

export const newsService = {
    async getNewsList() {
        try {
            const response = await apiClient.get('/news');
            return response.data; 
        } catch (error) {
            console.log(error);
            throw error; 
        }
    },

    async getNewsLast() {
        try {
            const response = await apiClient.get('/news/last');
            return response.data; 
        } catch (error) {
            console.log(error);
            throw error; 
        }
    },

    async getNewsById(id) {
        try {
            const response = await apiClient.get(`/news/${id}`);
            return response.data; 
        } catch (error) {
            console.log(error);
            throw error; 
        }
    }
};