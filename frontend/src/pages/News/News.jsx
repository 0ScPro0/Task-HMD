import styles from "./News.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Footer } from "../../components/layout/Footer/Footer"
import { NewsBlock } from "../../components/layout/NewsBlock/NewsBlock"

export function News() {
    return (
        <div className={styles.news}>
            <Header />
            <main className={styles.main}>
                <h1 className={styles["page-title"]}>Новости ЖЭУ</h1>
                <NewsBlock />
            </main>
            <Footer />
        </div>
    )
}