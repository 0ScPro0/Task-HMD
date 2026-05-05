import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import styles from "./Register.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Footer } from "../../components/layout/Footer/Footer"
import { authService } from "../../services/api/auth"

export function Register() {
    const [form, setForm] = useState({
        email: "",
        phone: "",
        lastName: "",
        firstName: "",
        middleName: "",
        address: "",
        apartment: "",
        password: "",
        confirmPassword: ""
    })
    const [error, setError] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    const navigate = useNavigate()

    const handleChange = (e) => {
        const { id, value } = e.target
        setForm(prev => ({ ...prev, [id]: value }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")

        // Валидация паролей
        if (form.password !== form.confirmPassword) {
            setError("Пароли не совпадают")
            return
        }

        // Валидация email
        if (form.email && !form.email.includes("@")) {
            setError("Введите корректный email")
            return
        }

        // Валидация обязательных полей
        if (!form.phone || !form.lastName || !form.firstName || !form.password) {
            setError("Заполните обязательные поля")
            return
        }

        setIsLoading(true)

        try {
            // Вызов API регистрации
            const response = await authService.register(
                form.email, 
                form.firstName, 
                form.lastName,
                form.middleName, 
                form.address, 
                form.apartment, 
                form.phone, 
                form.password,   
            )

            // После успешной регистрации перенаправляем в Home
            if (response.status === 200){
                navigate("/")
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Ошибка регистрации. Попробуйте позже.")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className={styles.register}>
            <Header />
            <main className={styles.main}>
                <div className={styles.authCard}>
                    <h1 className={styles.authTitle}>Регистрация</h1>
                    <form onSubmit={handleSubmit}>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="email">
                                Email <span className={styles.optional}>(опционально)</span>
                            </label>
                            <input
                                className={styles.formInput}
                                id="email"
                                type="email"
                                placeholder="example@mail.ru"
                                value={form.email}
                                onChange={handleChange}
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="phone">
                                Номер телефона
                            </label>
                            <input
                                className={styles.formInput}
                                id="phone"
                                type="tel"
                                placeholder="+7 (___) ___-__-__"
                                value={form.phone}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className={styles.formRow}>
                            <div className={styles.formGroup}>
                                <label className={styles.formLabel} htmlFor="lastName">
                                    Фамилия
                                </label>
                                <input
                                    className={styles.formInput}
                                    id="lastName"
                                    type="text"
                                    placeholder="Иванов"
                                    value={form.lastName}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label className={styles.formLabel} htmlFor="firstName">
                                    Имя
                                </label>
                                <input
                                    className={styles.formInput}
                                    id="firstName"
                                    type="text"
                                    placeholder="Иван"
                                    value={form.firstName}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="middleName">
                                Отчество <span className={styles.optional}>(опционально)</span>
                            </label>
                            <input
                                className={styles.formInput}
                                id="middleName"
                                type="text"
                                placeholder="Иванович"
                                value={form.middleName}
                                onChange={handleChange}
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="address">
                                Адрес <span className={styles.optional}>(опционально)</span>
                            </label>
                            <input
                                className={styles.formInput}
                                id="address"
                                type="text"
                                placeholder="ул. Примерная, д. 1"
                                value={form.address}
                                onChange={handleChange}
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label className={styles.formLabel} htmlFor="apartment">
                                Номер квартиры <span className={styles.optional}>(опционально)</span>
                            </label>
                            <input
                                className={styles.formInput}
                                id="apartment"
                                type="text"
                                placeholder="42"
                                value={form.apartment}
                                onChange={handleChange}
                            />
                        </div>

                        <div className={styles.formRow}>
                            <div className={styles.formGroup}>
                                <label className={styles.formLabel} htmlFor="password">
                                    Пароль
                                </label>
                                <input
                                    className={styles.formInput}
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={form.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label className={styles.formLabel} htmlFor="confirmPassword">
                                    Подтверждение пароля
                                </label>
                                <input
                                    className={styles.formInput}
                                    id="confirmPassword"
                                    type="password"
                                    placeholder="••••••••"
                                    value={form.confirmPassword}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        {error && <div className={styles.error}>{error}</div>}

                        <button
                            type="submit"
                            className={styles.btnSubmit}
                            disabled={isLoading}
                        >
                            {isLoading ? "Регистрация..." : "Зарегистрироваться"}
                        </button>
                    </form>
                    <Link to="/login" className={styles.authLink}>
                        Войти
                    </Link>
                </div>
            </main>
            <Footer />
        </div>
    )
}