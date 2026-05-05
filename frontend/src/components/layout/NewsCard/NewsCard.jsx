import styles from "./NewsCard.module.css"

export function NewsCard() {
    return (
        <article className={styles.newsCard}>
            <div className={styles.newsCard__date}>5 апреля 2026</div>
            <h3 className={styles.newsCard__heading}>Плановая промывка системы отопления в домах по ул. Ленина</h3>
            <p className={styles.newsCard__body}>
                С 7 по 10 апреля 2026 года будут проводиться работы по плановой
                промывке внутридомовой системы отопления в жилых домах № 12, 14
                и 16 по улице Ленина. На период проведения работ горячее
                водоснабжение будет временно приостановлено. Приносим извинения
                за временные неудобства.
            </p>
            <a href="/news" className={styles.newsCard__link}>Все новости →</a>
        </article>
    )
}