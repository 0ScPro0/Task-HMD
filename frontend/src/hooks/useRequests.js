import { useState, useEffect } from 'react'
import { requestService } from '../services/api/requests'
import { useAuthStore } from '../stores/authStore'

export function useRequests() {
    const [myRequests, setMyRequests] = useState([])
    const [availableRequests, setAvailableRequests] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)
    
    const { user } = useAuthStore()
    
    // Check if user is employee (plumber/electrician)
    const isEmployee = user?.role === "plumber" || user?.role === "electrician"
    
    // Helper function to transform API data to RequestCard format
    const transformRequestData = (request) => {
        // Map request type from enum to readable string
        const getTypeLabel = (type) => {
            switch (type) {
                case "plumber":
                    return "Сантехник"
                case "electrician":
                    return "Электрик"
                case "general":
                    return "Общая"
                default:
                    return type || "Общая"
            }
        }
        
        // Map status from enum to readable string
        const getStatusLabel = (status) => {
            switch (status) {
                case "NEW":
                    return "Новая"
                case "IN_PROGRESS":
                    return "В работе"
                case "COMPLETED":
                    return "Выполнена"
                case "CANCELLED":
                    return "Отменена"
                default:
                    return status || "Новая"
            }
        }
        
        // Format date
        const formatDate = (dateString) => {
            if (!dateString) return "Дата не указана"
            try {
                return new Date(dateString).toLocaleDateString("ru-RU")
            } catch {
                return dateString
            }
        }
        
        // Get user display name
        const getUserDisplayName = (userObj) => {
            if (!userObj) return null
            const parts = []
            if (userObj.surname) parts.push(userObj.surname)
            if (userObj.name) parts.push(userObj.name)
            if (userObj.patronymic) parts.push(userObj.patronymic)
            return parts.length > 0 ? parts.join(" ") : "Не указан"
        }
        
        return {
            id: request.id || 0,
            title: request.title || "Без названия",
            type: getTypeLabel(request.type),
            status: getStatusLabel(request.status),
            date: formatDate(request.created_at),
            description: request.description || "Описание отсутствует",
            residentName: getUserDisplayName(request.owner) || "Не указан",
            residentPhone: request.owner?.phone || "—",
            executorName: getUserDisplayName(request.executor),
            executorPhone: request.executor?.phone || null,
            address: request.owner?.address ? 
                `${request.owner.address}${request.owner.apartment ? `, кв. ${request.owner.apartment}` : ''}` 
                : "Адрес не указан",
            // Raw data for internal use
            raw: request
        }
    }
    
    const fetchRequests = async () => {
        setIsLoading(true)
        setError(null)
        
        try {
            // Fetch user's requests
            const myRequestsData = await requestService.getMyRequests()
            const transformedMyRequests = Array.isArray(myRequestsData) 
                ? myRequestsData.map(transformRequestData)
                : []
            
            setMyRequests(transformedMyRequests)
            
            // Fetch available requests for employees
            if (isEmployee) {
                const availableRequestsData = await requestService.getAvailableRequests()
                const transformedAvailableRequests = Array.isArray(availableRequestsData)
                    ? availableRequestsData.map(transformRequestData)
                    : []
                
                setAvailableRequests(transformedAvailableRequests)
            } else {
                setAvailableRequests([])
            }
            
        } catch (err) {
            console.error('Ошибка загрузки заявок:', err)
            setError('Не удалось загрузить заявки. Попробуйте обновить страницу.')
            
            // Clear data on error
            setMyRequests([])
            setAvailableRequests([])
        } finally {
            setIsLoading(false)
        }
    }
    
    const createRequest = async (requestData) => {
        try {
            const newRequest = await requestService.createRequest(requestData)
            const transformedRequest = transformRequestData(newRequest)
            
            // Add new request to my requests
            setMyRequests(prev => [transformedRequest, ...prev])
            
            return transformedRequest
        } catch (err) {
            console.error('Ошибка создания заявки:', err)
            throw err
        }
    }
    
    const updateRequestStatus = async (requestId, status) => {
        try {
            const updatedRequest = await requestService.updateRequestStatus(requestId, status)
            const transformedRequest = transformRequestData(updatedRequest)
            
            // Update request in myRequests
            setMyRequests(prev => 
                prev.map(req => req.id === requestId ? transformedRequest : req)
            )
            
            // Update request in availableRequests if present
            setAvailableRequests(prev => 
                prev.map(req => req.id === requestId ? transformedRequest : req)
            )
            
            return transformedRequest
        } catch (err) {
            console.error('Ошибка обновления статуса заявки:', err)
            throw err
        }
    }
    
    const acceptRequest = async (requestId) => {
        try {
            const acceptedRequest = await requestService.acceptRequest(requestId)
            const transformedRequest = transformRequestData(acceptedRequest)
            
            // Remove from available requests (since it's now accepted)
            setAvailableRequests(prev => 
                prev.filter(req => req.id !== requestId)
            )
            
            // Add to my requests if current user is the executor
            if (user?.id === transformedRequest.raw.executor_id) {
                setMyRequests(prev => [transformedRequest, ...prev])
            }
            
            return transformedRequest
        } catch (err) {
            console.error('Ошибка принятия заявки:', err)
            throw err
        }
    }
    
    const deleteRequest = async (requestId) => {
        try {
            await requestService.deleteRequest(requestId)
            
            // Remove from both lists
            setMyRequests(prev => prev.filter(req => req.id !== requestId))
            setAvailableRequests(prev => prev.filter(req => req.id !== requestId))
            
            return true
        } catch (err) {
            console.error('Ошибка удаления заявки:', err)
            throw err
        }
    }
    
    useEffect(() => {
        fetchRequests()
    }, [user])
    
    return {
        myRequests,
        availableRequests,
        isLoading,
        error,
        isEmployee,
        fetchRequests,
        createRequest,
        updateRequestStatus,
        acceptRequest,
        deleteRequest
    }
}