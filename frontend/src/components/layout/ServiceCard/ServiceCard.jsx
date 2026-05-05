import styles from "./ServiceCard.module.css"

export function ServiceCard({ icon, name, description, onClick }) {
    return (
        <div className={styles.serviceCard} onClick={onClick}>
            <div className={styles.serviceCard__icon}>
                {icon}
            </div>
            <div className={styles.serviceCard__name}>{name}</div>
            <div className={styles.serviceCard__desc}>{description}</div>
        </div>
    )
}