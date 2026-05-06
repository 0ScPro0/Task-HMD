import { useState, useEffect, useCallback } from "react";
import { notificationService } from "../services/api/notifications";

export function useNotifications() {
    const [notifications, setNotifications] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Функция для нормализации данных уведомления
    const normalizeNotification = (notification) => {
        return {
            ...notification,
            // Приводим статус прочтения к единому формату
            read: notification.is_read || notification.read || false,
            // Сохраняем оригинальный id для API
            user_notification_id: notification.user_notification_id || notification.id,
        };
    };

    const fetchNotifications = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await notificationService.getUserNotifications();
            // Нормализуем каждое уведомление и сортируем от новых к старым
            const normalizedData = Array.isArray(data) 
                ? data
                    .map(normalizeNotification)
                    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                : [];
            setNotifications(normalizedData);
            return normalizedData;
        } catch (err) {
            console.error("Failed to fetch notifications:", err);
            setError("Не удалось загрузить уведомления");
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const markAsRead = useCallback(async (userNotificationId) => {
        try {
            await notificationService.readNotification(userNotificationId);
            setNotifications(prev =>
                prev.map(notification => {
                    const notificationId = notification.user_notification_id || notification.id;
                    if (notificationId === userNotificationId) {
                        return { ...notification, read: true, is_read: true };
                    }
                    return notification;
                })
            );
            return true;
        } catch (err) {
            console.error("Failed to mark notification as read:", err);
            throw err;
        }
    }, []);

    const markAllAsRead = useCallback(async () => {
        // Получаем ID только непрочитанных уведомлений
        const unreadNotifications = notifications.filter(n => !n.read);
        
        if (unreadNotifications.length === 0) return true;
        
        const promises = unreadNotifications.map(notification => {
            const notificationId = notification.user_notification_id || notification.id;
            return notificationService.readNotification(notificationId);
        });
        
        try {
            await Promise.all(promises);
            // Помечаем все как прочитанные
            setNotifications(prev =>
                prev.map(notification => ({ 
                    ...notification, 
                    read: true, 
                    is_read: true 
                }))
            );
            return true;
        } catch (err) {
            console.error("Failed to mark all notifications as read:", err);
            throw err;
        }
    }, [notifications]);

    // Правильный подсчет непрочитанных
    const unreadCount = notifications.filter(n => !n.read).length;

    // Refresh notifications periodically (optional)
    useEffect(() => {
        // Initial fetch
        fetchNotifications();

        // Set up periodic refresh every 60 seconds
        const intervalId = setInterval(fetchNotifications, 60000);
        
        return () => clearInterval(intervalId);
    }, [fetchNotifications]);

    return {
        notifications,
        isLoading,
        error,
        unreadCount,
        fetchNotifications,
        markAsRead,
        markAllAsRead,
        setNotifications
    };
}