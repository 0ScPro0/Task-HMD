import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import styles from "./Login.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Footer } from "../../components/layout/Footer/Footer"
import { authService } from "../../services/api/auth"

export function Login() {
    const [identity, setIdentity] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")
        setIsLoading(true)

        // Валидация: identity может быть email или телефон
        if (!identity.trim() || !password) {
            setError("Заполните все поля")
            setIsLoading(false)
            return
        }

        try {
            // Вызов API входа (токены автоматически сохраняются в store через authService)
            const response = await authService.login(identity, password)
            // Перенаправляем на главную
            if (response.status === 200){
                navigate("/")
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Неверный email/телефон или пароль")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className={styles.login}>
            <Header />
            <main className={styles.main}>
                <div className={styles.authCard}>
                    <h1 className={styles.authTitle}>Вход в личный кабинет</h1>
                    <form onSubmit={handleSubmit}>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="loginIdentity">
                                Телефон
                            </label>
                            <input
                                className={styles.formInput}
                                id="loginIdentity"
                                type="text"
                                placeholder="+7987..."
                                value={identity}
                                onChange={(e) => setIdentity(e.target.value)}
                                required
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="loginPassword">
                                Пароль
                            </label>
                            <input
                                className={styles.formInput}
                                id="loginPassword"
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        {error && <div className={styles.error}>{error}</div>}
                        <button
                            type="submit"
                            className={styles.btnSubmit}
                            disabled={isLoading}
                        >
                            {isLoading ? "Вход..." : "Войти"}
                        </button>
                    </form>
                    <Link to="/register" className={styles.authLink}>
                        Зарегистрироваться
                    </Link>
                </div>
            </main>
            <Footer />
        </div>
    )
}