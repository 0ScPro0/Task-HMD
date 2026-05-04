import styles from "./Home.module.css"
import { Header } from "../../components/layout/Header/Header"

export function Home(){
    return(
        <div className={styles.home}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   