import styles from "./Request.module.css"
import { Header } from "../../components/layout/Header/Header"

export function Request(){
    return(
        <div className={styles.request}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   