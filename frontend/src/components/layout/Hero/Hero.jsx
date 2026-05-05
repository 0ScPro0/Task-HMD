import styles from "./Hero.module.css"

export function Hero() {
    return (
        <section className={styles.hero}>
            <h1 className={styles.hero__title}>Добро пожаловать в ЖЭУ</h1>
            <p className={styles.hero__text}>
                Жилищно-эксплуатационное управление — ваш надёжный помощник
                в вопросах содержания и обслуживания жилого фонда.
                Мы обеспечиваем комфорт и порядок в вашем доме.
            </p>
        </section>
    )
}