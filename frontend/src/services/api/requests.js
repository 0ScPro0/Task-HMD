import { apiClient } from './client';

export const requestService = {
    /**
     * Get user's requests (my requests)
     * @returns {Promise<Array>} List of user's requests
     */
    async getMyRequests() {
        try {
            const response = await apiClient.get('/requests/my');
            return response.data;
        } catch (error) {
            console.error('Error fetching user requests:', error);
            throw error;
        }
    },

    /**
     * Get available requests for employees (new requests by executor role)
     * @returns {Promise<Array>} List of available requests
     */
    async getAvailableRequests() {
        try {
            const response = await apiClient.get('/requests/new');
            return response.data || [];
        } catch (error) {
            console.error('Error fetching available requests:', error);
            throw error;
        }
    },

    /**
     * Create new request
     * @param {Object} requestData - Request data
     * @returns {Promise<Object>} Created request
     */
    async createRequest(requestData) {
        try {
            const response = await apiClient.post('/requests/create', requestData);
            return response.data;
        } catch (error) {
            console.error('Error creating request:', error);
            throw error;
        }
    },

    /**
     * Update request status
     * @param {number} requestId - Request ID
     * @param {string} status - New status
     * @returns {Promise<Object>} Updated request
     */
    async updateRequestStatus(requestId, status) {
        try {
            const response = await apiClient.patch(`/requests/${requestId}/status`, null, {
                params: { status }
            });
            return response.data;
        } catch (error) {
            console.error('Error updating request status:', error);
            throw error;
        }
    },

    /**
     * Accept request as executor
     * @param {number} requestId - Request ID
     * @returns {Promise<Object>} Accepted request
     */
    async acceptRequest(requestId) {
        try {
            const response = await apiClient.patch(`/requests/${requestId}/accept`);
            return response.data;
        } catch (error) {
            console.error('Error accepting request:', error);
            throw error;
        }
    },

    /**
     * Get request by ID
     * @param {number} requestId - Request ID
     * @returns {Promise<Object>} Request details
     */
    async getRequestById(requestId) {
        try {
            const response = await apiClient.get(`/requests/${requestId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching request:', error);
            throw error;
        }
    },

    /**
     * Delete request
     * @param {number} requestId - Request ID
     * @returns {Promise<Object>} Deleted request
     */
    async deleteRequest(requestId) {
        try {
            const response = await apiClient.delete(`/requests/${requestId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting request:', error);
            throw error;
        }
    }
};