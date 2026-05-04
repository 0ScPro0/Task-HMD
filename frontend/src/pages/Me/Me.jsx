import styles from "./Me.module.css"
import { Header } from "../../components/layout/Header/Header"

export function Me(){
    return(
        <div className={styles.me}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   