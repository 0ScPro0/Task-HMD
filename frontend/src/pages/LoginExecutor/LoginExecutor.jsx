import styles from "./LoginExecutor.module.css"
import { Header } from "../../components/layout/Header/Header"

export function LoginExecutor(){
    return(
        <div className={styles.login_executor}>
            <Header/>
            <main className={styles.main}>
            </main>
        </div>
    )
}   