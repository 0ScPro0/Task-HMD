import styles from "./NotifyPopup.module.css"

export function NotifyPopup({ isOpen }) {
    return (
        <div className={`${styles.notifyPopup} ${isOpen ? styles.active : ''}`}>
            У вас нет новых уведомлений
        </div>
    )
}