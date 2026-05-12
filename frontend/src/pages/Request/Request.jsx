import { useState } from "react"
import { Link } from "react-router-dom"
import styles from "./Request.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Footer } from "../../components/layout/Footer/Footer"
import { NotifyPopup } from "../../components/layout/NotifyPopup/NotifyPopup"
import { RequestCard } from "../../components/layout/RequestCard/RequestCard"
import { useRequests } from "../../hooks/useRequests"
import { useAuthStore } from "../../stores/authStore"

export function Request() {
    const [notifyOpen, setNotifyOpen] = useState(false)
    const { user } = useAuthStore()
    
    const {
        myRequests,
        availableRequests,
        isLoading,
        error,
        isEmployee,
        fetchRequests,
        acceptRequest,
        updateRequestStatus,
        deleteRequest
    } = useRequests()
    
    const toggleNotify = () => {
        setNotifyOpen(!notifyOpen)
    }
    
    return (
        <div className={styles.request}>
            <Header />
            
            <main className={styles.main}>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Заявки</h1>
                    <Link to="/request/new" className={styles.btnNew}>
                        + Новая заявка
                    </Link>
                </div>
                
                {/* Loading state */}
                {isLoading && (
                    <div className={styles.loadingOverlay}>
                        <div className={styles.loadingSpinner}></div>
                        <p>Загрузка заявок...</p>
                    </div>
                )}
                
                {/* Error message */}
                {error && !isLoading && (
                    <div className={styles.errorMessage}>
                        ⚠️ {error}
                        <button 
                            onClick={fetchRequests}
                            style={{
                                marginLeft: '10px',
                                padding: '4px 12px',
                                background: '#ed8936',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            Попробовать снова
                        </button>
                    </div>
                )}
                
                {/* My Requests Section */}
                <section className={styles.requestsSection}>
                    <h2 className={styles.sectionTitle}>Мои заявки</h2>
                    
                    {!isLoading && myRequests.length === 0 ? (
                        <div className={styles.emptyState}>
                            У вас пока нет заявок. Создайте первую!
                        </div>
                    ) : (
                        myRequests.map(request => (
                            <RequestCard
                                key={request.id}
                                request={request}
                                showActions={true}
                                onDelete={deleteRequest}
                                onUpdateStatus={updateRequestStatus}
                                isCurrentUserExecutor={request.raw?.executor_id === user?.id}
                                userRole={user?.role}
                            />
                        ))
                    )}
                </section>
                
                {/* Available Requests Section (only for employees) */}
                {isEmployee && (
                    <section className={styles.requestsSection}>
                        <h2 className={styles.sectionTitle}>
                            Доступные заявки 
                            <span className={styles.sectionHint}>(видят только сотрудники)</span>
                        </h2>
                        
                        {!isLoading && availableRequests.length === 0 ? (
                            <div className={styles.emptyState}>
                                Нет доступных заявок для выполнения.
                            </div>
                        ) : (
                            availableRequests.map(request => (
                                <RequestCard
                                    key={request.id}
                                    request={request}
                                    showActions={true}
                                    onAccept={acceptRequest}
                                    onDelete={deleteRequest}
                                    onUpdateStatus={updateRequestStatus}
                                    isCurrentUserExecutor={false}
                                    userRole={user?.role}
                                />
                            ))
                        )}
                    </section>
                )}
            </main>
            
            <Footer />
        </div>
    )
}