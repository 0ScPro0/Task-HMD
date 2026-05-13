import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import styles from "./RequestNew.module.css"
import { useRequests } from "../../hooks/useRequests"
import { useAuthStore } from "../../stores/authStore"
import { NotifyPopup } from "../../components/layout/NotifyPopup/NotifyPopup"
import { Footer } from "../../components/layout/Footer/Footer"

export function RequestNew() {
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const { createRequest } = useRequests()
    
    const [formData, setFormData] = useState({
        title: "",
        type: "",
        description: "",
    })
    
    const [notifyOpen, setNotifyOpen] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [submitError, setSubmitError] = useState("")
    const [submitSuccess, setSubmitSuccess] = useState(false)
    
    const toggleNotify = (e) => {
        e.stopPropagation()
        setNotifyOpen(prev => !prev)
    }
    
    const closeNotify = () => {
        setNotifyOpen(false)
    }
    
    useEffect(() => {
        const handleClick = () => closeNotify()
        document.addEventListener('click', handleClick)
        return () => document.removeEventListener('click', handleClick)
    }, [])
    
    const handleChange = (e) => {
        const { id, value } = e.target
        const fieldName = id === "requestTitle" ? "title" : 
                         id === "requestType" ? "type" : 
                         id === "requestDesc" ? "description" : id
        
        setFormData(prev => ({
            ...prev,
            [fieldName]: value
        }))
        
        // Clear error
        setSubmitError("")
    }
    
    const validateForm = () => {
        if (!formData.title.trim()) {
            setSubmitError("Введите название заявки")
            return false
        }
        
        if (!formData.type) {
            setSubmitError("Выберите тип заявки")
            return false
        }
        
        if (!formData.description.trim()) {
            setSubmitError("Введите описание заявки")
            return false
        }
        
        if (formData.description.trim().length < 10) {
            setSubmitError("Описание должно содержать минимум 10 символов")
            return false
        }
        
        return true
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (!validateForm()) {
            return
        }
        
        setIsSubmitting(true)
        setSubmitError("")
        
        try {
            // Prepare request data according to backend schema
            const requestData = {
                title: formData.title.trim(),
                type: formData.type,
                description: formData.description.trim(),
                status: "new",
                admin_comment: "",
                owner_id: user?.id,
                executor_id: 0,
                executor: null,
            }
            
            await createRequest(requestData)
            
            // Show success
            setSubmitSuccess(true)
            
            // Redirect to requests page after 1.5 seconds
            setTimeout(() => {
                navigate("/request")
            }, 1500)
            
        } catch (err) {
            console.error("Ошибка при создании заявки:", err)
            
            let errorMessage = "Не удалось создать заявку. Попробуйте снова."
            
            if (err.response?.data?.detail) {
                errorMessage = err.response.data.detail
            } else if (err.message) {
                errorMessage = err.message
            }
            
            setSubmitError(errorMessage)
        } finally {
            setIsSubmitting(false)
        }
    }
    
    const handleCancel = () => {
        navigate("/request")
    }
    
    return (
        <div className={styles.request_new}>
            {/* ════════ HEADER ════════ */}
            <header className={styles.header}>
                <Link to="/" className={styles.header__logo}>ЖЭУ</Link>
                <nav className={styles.header__right}>
                    <Link to="/news" className={styles.header__link}>Новости</Link>
                    <button 
                        className={styles.header__notify} 
                        onClick={toggleNotify}
                        title="Уведомления"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                            strokeWidth="2">
                            <path strokeLinecap="round" strokeLinejoin="round"
                                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0 1 18 14.158V11a6.002 6.002 0 0 0-4-5.659V5a2 2 0 1 0-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9" />
                        </svg>
                    </button>
                    <Link to="/me" className={styles.header__link}>Личный кабинет</Link>
                </nav>
            </header>
            
            {/* Notify Popup */}
            <NotifyPopup isOpen={notifyOpen} />
            
            {/* ════════ MAIN ════════ */}
            <main className={styles.main}>
                <form className={styles.form_card} onSubmit={handleSubmit} id="newRequestForm">
                    <h1 className={styles.form_title}>Новая заявка</h1>
                    
                    {/* Error message */}
                    {submitError && (
                        <div className={styles.error_message}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                            </svg>
                            {submitError}
                        </div>
                    )}
                    
                    {/* Success message */}
                    {submitSuccess && (
                        <div className={styles.success_message}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                <polyline points="22 4 12 14.01 9 11.01"></polyline>
                            </svg>
                            Заявка успешно создана! Вы будете перенаправлены на страницу заявок...
                        </div>
                    )}
                    
                    {/* Loading overlay */}
                    {isSubmitting && (
                        <div className={styles.loading_overlay}>
                            <div className={styles.loading_spinner}></div>
                            <p>Создание заявки...</p>
                        </div>
                    )}
                    
                    {/* Form fields */}
                    {!isSubmitting && !submitSuccess && (
                        <>
                            <div className={styles.form_group}>
                                <label className={styles.form_label} htmlFor="requestTitle">
                                    Название заявки
                                </label>
                                <input 
                                    className={styles.form_input} 
                                    id="requestTitle" 
                                    type="text" 
                                    placeholder="Например: Протечка трубы" 
                                    required
                                    value={formData.title}
                                    onChange={handleChange}
                                    disabled={isSubmitting}
                                />
                            </div>

                            <div className={styles.form_group}>
                                <label className={styles.form_label} htmlFor="requestType">
                                    Кто нужен / Тип заявки
                                </label>
                                <select 
                                    className={styles.form_select} 
                                    id="requestType" 
                                    required
                                    value={formData.type}
                                    onChange={handleChange}
                                    disabled={isSubmitting}
                                >
                                    <option value="" disabled>Выберите специалиста</option>
                                    <option value="plumber">Сантехник</option>
                                    <option value="electrician">Электрик</option>
                                    <option value="other">Другое</option>
                                </select>
                            </div>

                            <div className={styles.form_group}>
                                <label className={styles.form_label} htmlFor="requestDesc">
                                    Описание заявки
                                </label>
                                <textarea 
                                    className={styles.form_textarea} 
                                    id="requestDesc" 
                                    placeholder="Подробно опишите проблему..."
                                    required
                                    value={formData.description}
                                    onChange={handleChange}
                                    disabled={isSubmitting}
                                />
                            </div>

                            <div className={styles.form_actions}>
                                <button 
                                    type="submit" 
                                    className={styles.btn_submit}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? "Отправка..." : "Отправить заявку"}
                                </button>
                                <button 
                                    type="button" 
                                    className={styles.btn_back}
                                    onClick={handleCancel}
                                    disabled={isSubmitting}
                                >
                                    Отмена
                                </button>
                            </div>
                        </>
                    )}
                </form>
            </main>

            {/* ════════ FOOTER ════════ */}
            <Footer />
        </div>
    )
}