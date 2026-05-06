import { useState } from "react";
import styles from "./Notification.module.css";
import { notificationService } from "../../../services/api/notifications";

export function Notification({ notification, onMarkAsRead }) {
    const [isHovered, setIsHovered] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    
    // Берем статус напрямую из пропсов
    const isRead = notification?.is_read || notification?.read || false;

    const handleMarkAsRead = async () => {
        if (isRead || isLoading) return;
        
        setIsLoading(true);
        try {
            const notificationId = notification.user_notification_id || notification.id;
            await notificationService.readNotification(notificationId);
            
            // Сообщаем родителю, что нужно обновить данные
            if (onMarkAsRead) {
                onMarkAsRead(notificationId);
            }
        } catch (error) {
            console.error("Failed to mark notification as read:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    const formatDate = (dateString) => {
        if (!dateString) return "";
        const date = new Date(dateString);
        return date.toLocaleDateString("ru-RU", {
            day: "numeric",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        });
    };

    return (
        <div 
            className={`${styles.notification} ${isRead ? styles.read : styles.unread}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <div className={styles.content}>
                <h4 className={styles.title}>{notification.title || "Уведомление"}</h4>
                <p className={styles.message}>{notification.message || notification.body || notification.content || ""}</p>
                {notification.created_at && (
                    <time className={styles.time}>{formatDate(notification.created_at)}</time>
                )}
            </div>
            
            {!isRead && (isHovered || isLoading) && (
                <button 
                    className={styles.markAsReadButton}
                    onClick={handleMarkAsRead}
                    disabled={isLoading}
                >
                    {isLoading ? "..." : "✓"}
                </button>
            )}
        </div>
    );
}