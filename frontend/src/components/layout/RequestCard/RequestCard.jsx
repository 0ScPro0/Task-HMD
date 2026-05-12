import { useState } from "react"
import styles from "./RequestCard.module.css"

export function RequestCard({
    request,
    showActions = false,
    onAccept,
    onUpdateStatus,
    onDelete,
    isCurrentUserExecutor = false,
    userRole = null
}) {
    const {
        title,
        type,
        status,
        date,
        description,
        residentName,
        residentPhone,
        executorName,
        executorPhone,
        address,
        raw
    } = request

    const [isLoading, setIsLoading] = useState(false)
    const [actionError, setActionError] = useState(null)

    // Проверяем, совпадает ли роль пользователя с типом заявки
    const isRoleMatchesRequestType = () => {
        if (!userRole || !raw?.type) return false
        
        // Используем оригинальный тип из raw данных
        // raw.type может быть "plumber", "electrician", "general"
        return raw.type === userRole
    }

    // Определяем, можно ли показывать кнопку удаления
    const canShowDeleteButton = () => {
        if (!onDelete) return false
        
        // Для доступных заявок (где есть onAccept) не показываем удаление сотрудникам
        if (onAccept) {
            // Если это доступная заявка (есть onAccept), сотрудники не могут ее удалять
            if (userRole && (userRole === "plumber" || userRole === "electrician")) {
                return false
            }
            // Админы могут удалять любые заявки
            if (userRole === "admin") {
                return true
            }
        }
        
        // Для своих заявок (нет onAccept) показываем удаление владельцам и админам
        return true
    }

    // Определяем классы для бейджей в зависимости от типа и статуса
    const getTypeBadgeClass = () => {
        switch (type) {
            case "Сантехник":
                return styles.badgeTypePlumber
            case "Электрик":
                return styles.badgeTypeElectrician
            default:
                return styles.badgeType
        }
    }

    const getStatusBadgeClass = () => {
        switch (status) {
            case "Новая":
                return styles.badgeStatusNew
            case "В работе":
                return styles.badgeStatusInProgress
            case "Выполнена":
                return styles.badgeStatusCompleted
            case "Отменена":
                return styles.badgeStatusCancelled
            default:
                return styles.badgeStatus
        }
    }

    const handleAccept = async () => {
        if (!onAccept) return
        
        setIsLoading(true)
        setActionError(null)
        
        try {
            await onAccept(request.id)
        } catch (error) {
            console.error("Error accepting request:", error)
            setActionError(error.message || "Не удалось принять заявку")
        } finally {
            setIsLoading(false)
        }
    }

    const handleUpdateStatus = async (newStatus) => {
        if (!onUpdateStatus) return
        
        setIsLoading(true)
        setActionError(null)
        
        try {
            await onUpdateStatus(request.id, newStatus)
        } catch (error) {
            console.error("Error updating request status:", error)
            setActionError(error.message || "Не удалось обновить статус")
        } finally {
            setIsLoading(false)
        }
    }

    const handleDelete = async () => {
        if (!onDelete) return
        
        if (!window.confirm("Вы уверены, что хотите удалить эту заявку?")) {
            return
        }
        
        setIsLoading(true)
        setActionError(null)
        
        try {
            await onDelete(request.id)
        } catch (error) {
            console.error("Error deleting request:", error)
            setActionError(error.message || "Не удалось удалить заявку")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <article className={styles.requestCard}>
            <div className={styles.requestCardTop}>
                <span className={styles.requestCardTitle}>{title}</span>
                <div className={styles.requestCardMeta}>
                    <span className={`${styles.badge} ${getTypeBadgeClass()}`}>{type}</span>
                    <span className={`${styles.badge} ${getStatusBadgeClass()}`}>{status}</span>
                    <span className={styles.requestDate}>{date}</span>
                </div>
            </div>
            
            <div className={styles.requestCardDesc}>
                {description}
            </div>
            
            {/* Action error message */}
            {actionError && (
                <div className={styles.actionError}>
                    ⚠️ {actionError}
                </div>
            )}
            
            {/* Action buttons */}
            {showActions && (
                <div className={styles.actionButtons}>
                    {/* Кнопка "Принять" - только для новых заявок, если роль совпадает с типом */}
                    {(status === "Новая" || status === "new" || status === "NEW") && onAccept && isRoleMatchesRequestType() && (
                        <button
                            className={styles.btnAccept}
                            onClick={handleAccept}
                            disabled={isLoading}
                        >
                            {isLoading ? "Принятие..." : "Принять заявку"}
                        </button>
                    )}
                    
                    {/* Кнопка "Завершить" - только для исполнителя, если заявка в работе */}
                    {isCurrentUserExecutor && onUpdateStatus && status === "В работе" && (
                        <button
                            className={styles.btnComplete}
                            onClick={() => handleUpdateStatus("COMPLETED")}
                            disabled={isLoading}
                        >
                            {isLoading ? "Обновление..." : "Завершить"}
                        </button>
                    )}
                    
                    {/* Кнопка "Удалить" - только если можно показывать */}
                    {canShowDeleteButton() && (
                        <button
                            className={styles.btnDelete}
                            onClick={handleDelete}
                            disabled={isLoading}
                        >
                            {isLoading ? "Удаление..." : "Удалить"}
                        </button>
                    )}
                </div>
            )}
            
            <div className={styles.requestCardGrid}>
                <div className={styles.field}>
                    <span className={styles.fieldLabel}>Жилец</span>
                    <span className={styles.fieldValue}>{residentName}</span>
                </div>
                <div className={styles.field}>
                    <span className={styles.fieldLabel}>Телефон жильца</span>
                    <span className={styles.fieldValue}>{residentPhone}</span>
                </div>
                <div className={styles.field}>
                    <span className={styles.fieldLabel}>Исполнитель</span>
                    <span className={executorName ? styles.fieldValue : styles.fieldValueMuted}>
                        {executorName || "Не назначен"}
                    </span>
                </div>
                <div className={styles.field}>
                    <span className={styles.fieldLabel}>Телефон исполнителя</span>
                    <span className={executorPhone ? styles.fieldValue : styles.fieldValueMuted}>
                        {executorPhone || "—"}
                    </span>
                </div>
                <div className={styles.field}>
                    <span className={styles.fieldLabel}>Адрес</span>
                    <span className={styles.fieldValue}>{address}</span>
                </div>
            </div>
        </article>
    )
}