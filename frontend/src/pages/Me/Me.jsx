import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import styles from "./Me.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Footer } from "../../components/layout/Footer/Footer"
import { useAuthStore } from "../../stores/authStore"
import { authService } from "../../services/api/auth"
import { userService } from "../../services/api/users"

export function Me() {
    const [isEditing, setIsEditing] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [isFetching, setIsFetching] = useState(false)
    const [fetchError, setFetchError] = useState(null)
    const [saveError, setSaveError] = useState(null)
    const [saveSuccess, setSaveSuccess] = useState(false)
    const [formData, setFormData] = useState({})
    
    const navigate = useNavigate()
    const { clearTokens, user, setUserData } = useAuthStore()

    // Fetch user data from backend (only once on mount or when user changes)
    const fetchUserData = async () => {
        if (!user) return; // No user in store, probably not authenticated
        
        setIsFetching(true)
        setFetchError(null)
        
        try {
            const userData = await userService.getCurrentUser()
            
            // Update form data with fresh data from backend
            setFormData({
                name: userData.name || "",
                surname: userData.surname || "",
                patronymic: userData.patronymic || "",
                phone: userData.phone || "",
                email: userData.email || "",
                address: userData.address || "",
                apartment: userData.apartment || "",
                role: userData.role || "Жилец",
                create_at: userData.create_at || null,
            })
            
        } catch (error) {
            console.error("Error fetching user data:", error)
            setFetchError("Не удалось загрузить данные профиля. Попробуйте обновить страницу.")
        } finally {
            setIsFetching(false)
        }
    }

    useEffect(() => {
        console.log("Профиль из store:", user)
        
        // Initialize form data with user data from store
        if (user) {
            setFormData({
                name: user.name || "",
                surname: user.surname || "",
                patronymic: user.patronymic || "",
                phone: user.phone || "",
                email: user.email || "",
                address: user.address || "",
                apartment: user.apartment || "",
                role: user.role || "Жилец",
                create_at: user.create_at || null
            })
            
            // Optionally fetch fresh data from backend (commented out to avoid infinite loop)
            // fetchUserData()
        } else {
            // If no user in store, initialize with empty data
            setFormData({
                name: "",
                surname: "",
                patronymic: "",
                phone: "",
                email: "",
                address: "",
                apartment: "",
                role: "Жилец",
            })
        }
    }, [user])

    const handleLogout = async () => {
        setIsLoading(true)
        try {
            await authService.logout()
            clearTokens()
            navigate("/login")
        } catch (error) {
            console.error("Logout error:", error)
            // Still clear tokens and redirect on error
            clearTokens()
            navigate("/login")
        } finally {
            setIsLoading(false)
        }
    }

    const handleEditToggle = () => {
        setIsEditing(!isEditing)
        // Reset error and success states
        setSaveError(null)
        setSaveSuccess(false)
        
        // Reset form data to original user data when canceling
        if (isEditing) {
            setFormData({
                name: user.name || "",
                surname: user.surname || "",
                patronymic: user.patronymic || "",
                phone: user.phone || "",
                email: user.email || "",
                address: user.address || "",
                apartment: user.apartment || "",
                role: user.role || "Жилец",
                create_at: user.create_at || null
            })
        }
    }

    const handleSave = async () => {
        // Basic validation
        const errors = validateForm(formData)
        if (Object.keys(errors).length > 0) {
            // In a real app, you would display these errors to the user
            console.error("Validation errors:", errors)
            alert("Пожалуйста, исправьте ошибки в форме")
            return
        }
        
        // Clear previous states
        setSaveError(null)
        setSaveSuccess(false)
        setIsSaving(true)
        
        try {
            // Call user service stub
            var validatedFormData = formData
            delete validatedFormData.create_at
            const updatedUser = await userService.updateProfile(validatedFormData)
            
            // Update auth store with new user data
            if (setUserData) {
                setUserData(updatedUser)
            }
            
            // Show success and exit edit mode
            setSaveSuccess(true)
            setIsEditing(false)
            
            // Log success (in real app, you might show a toast notification)
            console.log("Profile updated successfully:", updatedUser)
            
        } catch (error) {
            // Handle error
            console.error("Failed to update profile:", error)
            setSaveError(error.message || "Не удалось сохранить изменения. Попробуйте еще раз.")
            
            // Keep user in edit mode so they can fix errors
        } finally {
            setIsSaving(false)
        }
    }

    const validateForm = (data) => {
        const errors = {}
        
        if (!data.name?.trim()) {
            errors.name = "Имя обязательно"
        }
        
        if (!data.surname?.trim()) {
            errors.surname = "Фамилия обязательна"
        }
        
        if (data.email && !/\S+@\S+\.\S+/.test(data.email)) {
            errors.email = "Некорректный email"
        }
        
        if (data.phone && !/^[\d\s\-\+\(\)]+$/.test(data.phone)) {
            errors.phone = "Некорректный номер телефона"
        }
        
        return errors
    }

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }))
    }

    // Generate initials for avatar
    const getInitials = () => {
        const first = formData.name?.[0] || "И"
        const last = formData.surname?.[0] || "И"
        return `${first}${last}`
    }

    // Render field value or input based on edit mode
    const renderField = (field, value, type = "text") => {
        if (!isEditing) {
            return <span className={styles.infoValue}>{value || "-"}</span>
        }
        
        return (
            <input
                type={type}
                value={value || ""}
                onChange={(e) => handleInputChange(field, e.target.value)}
                className={styles.editInput}
                placeholder={field}
            />
        )
    }

    return (
        <div className={styles.me}>
            <Header />
            <main className={styles.main}>
                <div className={styles.profileContainer}>
                    <div className={styles.profileCard}>
                        {/* Fetch error message (only show if there was an error) */}
                        {fetchError && (
                            <div className={styles.fetchErrorMessage}>
                                ⚠️ {fetchError}
                                <button
                                    className={styles.retryButton}
                                    onClick={fetchUserData}
                                >
                                    Попробовать снова
                                </button>
                            </div>
                        )}
                        
                        {/* Profile Header */}
                        <div className={styles.profileHeader}>
                            <div className={styles.profileAvatar}>
                                {getInitials()}
                            </div>
                            <div className={styles.profileHeaderInfo}>
                                <h1 className={styles.profileName}>
                                    {formData.surname} {formData.name} {formData.patronymic}
                                </h1>
                                <span className={styles.profileBadge}>{formData.role}</span>
                            </div>
                            <button
                                className={styles.btnEdit}
                                onClick={handleEditToggle}
                            >
                                {isEditing ? "Отменить редактирование" : "Изменить профиль"}
                            </button>
                        </div>

                        {/* Profile Grid */}
                        <div className={styles.profileGrid}>
                            {/* Personal Data */}
                            <div className={styles.infoGroup}>
                                <h3 className={styles.groupTitle}>Персональные данные</h3>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Имя</span>
                                    {renderField("name", formData.name)}
                                </div>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Фамилия</span>
                                    {renderField("surname", formData.surname)}
                                </div>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Отчество</span>
                                    {renderField("patronymic", formData.patronymic)}
                                </div>
                            </div>

                            {/* Contacts */}
                            <div className={styles.infoGroup}>
                                <h3 className={styles.groupTitle}>Контакты</h3>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Телефон</span>
                                    {renderField("phone", formData.phone, "tel")}
                                </div>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Email</span>
                                    {renderField("email", formData.email, "email")}
                                </div>
                            </div>

                            {/* Address */}
                            <div className={styles.infoGroup}>
                                <h3 className={styles.groupTitle}>Адрес проживания</h3>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Адрес</span>
                                    {renderField("address", formData.address)}
                                </div>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Квартира</span>
                                    {renderField("apartment", formData.apartment)}
                                </div>
                            </div>

                            {/* System Data */}
                            <div className={styles.infoGroup}>
                                <h3 className={styles.groupTitle}>Системные данные</h3>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Роль</span>
                                    <span className={styles.infoValue}>
                                        <span className={styles.profileBadge}>{formData.role}</span>
                                    </span>
                                </div>
                                <div className={styles.infoRow}>
                                    <span className={styles.infoLabel}>Дата регистрации</span>
                                    <span className={styles.infoValue}>{formData.create_at}</span>
                                </div>
                            </div>
                        </div>

                        {/* Action Buttons when editing */}
                        {isEditing && (
                            <div className={styles.editActions}>
                                {/* Error message */}
                                {saveError && (
                                    <div className={styles.errorMessage}>
                                        {saveError}
                                    </div>
                                )}
                                
                                {/* Success message */}
                                {saveSuccess && (
                                    <div className={styles.successMessage}>
                                        Изменения успешно сохранены!
                                    </div>
                                )}
                                
                                <button
                                    className={styles.btnCancel}
                                    onClick={handleEditToggle}
                                    disabled={isSaving}
                                >
                                    Отменить
                                </button>
                                <button
                                    className={styles.btnSave}
                                    onClick={handleSave}
                                    disabled={isSaving}
                                >
                                    {isSaving ? (
                                        <>
                                            <span className={styles.loadingSpinner}></span>
                                            Сохранение...
                                        </>
                                    ) : (
                                        "Сохранить изменения"
                                    )}
                                </button>
                            </div>
                        )}

                        {/* Logout Button */}
                        <button
                            className={styles.btnLogout}
                            onClick={handleLogout}
                            disabled={isLoading}
                        >
                            {isLoading ? "Выход..." : "Выйти из аккаунта"}
                        </button>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    )
}