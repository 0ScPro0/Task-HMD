import styles from "./Login.module.css"
import { Header } from "../../components/layout/Header/Header"

export function Login(){
    return(
        <div className={styles.login}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   