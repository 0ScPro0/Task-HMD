import { useEffect } from "react";
import styles from "./NotifyPopup.module.css";
import { Notification } from "../Notification/Notification";
import { useNotifications } from "../../../hooks/useNotifications";

export function NotifyPopup({ isOpen }) {
    const {
        notifications,
        isLoading,
        error,
        unreadCount,
        fetchNotifications,
        markAsRead,
        markAllAsRead
    } = useNotifications();

    useEffect(() => {
        if (isOpen) {
            fetchNotifications();
        }
    }, [isOpen, fetchNotifications]);

    const handleMarkAsRead = async (notificationId) => {
        try {
            await markAsRead(notificationId);
        } catch (err) {
            console.error("Failed to mark notification as read:", err);
        }
    };

    const handleMarkAllAsRead = async () => {
        try {
            await markAllAsRead();
        } catch (err) {
            console.error("Failed to mark all notifications as read:", err);
        }
    };

    return (
        <div className={`${styles.notifyPopup} ${isOpen ? styles.active : ''}`}>
            <div className={styles.header}>
                <h3 className={styles.title}>Уведомления</h3>
                {unreadCount > 0 && (
                    <span className={styles.badge}>{unreadCount}</span>
                )}
            </div>
            
            <div className={styles.content}>
                {isLoading ? (
                    <div className={styles.loading}>Загрузка...</div>
                ) : error ? (
                    <div className={styles.error}>{error}</div>
                ) : notifications.length === 0 ? (
                    <div className={styles.empty}>У вас нет новых уведомлений</div>
                ) : (
                    <div className={styles.notificationsList}>
                        {notifications.map((notification, index) => (
                            <Notification
                                key={notification.id || notification.notification_id || index}
                                notification={notification}
                                onMarkAsRead={handleMarkAsRead}
                            />
                        ))}
                    </div>
                )}
            </div>
            
            {notifications.length > 0 && unreadCount > 0 && (
                <div className={styles.footer}>
                    <button
                        className={styles.markAllAsRead}
                        onClick={handleMarkAllAsRead}
                    >
                        Отметить все как прочитанные
                    </button>
                </div>
            )}
        </div>
    );
}