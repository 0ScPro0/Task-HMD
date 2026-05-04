import styles from "./News.module.css"
import { Header } from "../../components/layout/Header/Header"

export function News(){
    return(
        <div className={styles.news}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   