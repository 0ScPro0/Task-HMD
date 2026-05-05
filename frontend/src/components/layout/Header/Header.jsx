import { useState } from "react"
import styles from "./Header.module.css"
import { NotifyPopup } from "../NotifyPopup/NotifyPopup"

export function Header(){
    const [notifyOpen, setNotifyOpen] = useState(false)

    const toggleNotify = (e) => {
        e.stopPropagation()
        setNotifyOpen(prev => !prev)
    }

    const closeNotify = () => {
        setNotifyOpen(false)
    }

    // Закрытие при клике вне popup
    useState(() => {
        const handleClick = () => closeNotify()
        document.addEventListener('click', handleClick)
        return () => document.removeEventListener('click', handleClick)
    }, [])

    return (
        <header className={styles.header}>
            <a href="/" className={styles.header__logo}>ЖЭУ</a>

            <nav className={styles.header__right}>
                <a href="/news" className={styles.header__link}>Новости</a>

                <button className={styles.header__notify} onClick={toggleNotify} title="Уведомления">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0 1 18
                            14.158V11a6.002 6.002 0 0 0-4-5.659V5a2
                            2 0 1 0-4 0v.341C7.67 6.165 6 8.388 6
                            11v3.159c0 .538-.214 1.055-.595
                            1.436L4 17h5m6 0v1a3 3 0 1 1-6
                            0v-1m6 0H9" />
                    </svg>
                </button>

                <a href="/me" className={styles.header__link}>Личный кабинет</a>
            </nav>
            <NotifyPopup isOpen={notifyOpen} />
        </header>
    )
}