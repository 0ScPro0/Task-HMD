import styles from "./Footer.module.css"

export function Footer() {
    return (
        <footer className={styles.footer}>
            <div className={styles.footer__phone}>
                Горячая линия: <a href="tel:+79999999999">+7 (999) 999-99-99</a>
            </div>
            <div>© ЖЭУ 2026, все права защищены</div>
        </footer>
    )
}