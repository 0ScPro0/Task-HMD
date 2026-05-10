import { useEffect } from 'react'; // ← правильный импорт
import styles from './AdminRedirect.module.css';
import { useAuthStore } from '../../stores/authStore';

export function AdminRedirect() {
    const {getAccessToken, isAdmin} = useAuthStore()
    const accessToken = getAccessToken()
    const isUserAdmin = isAdmin() 

    useEffect(() => {
        if (isUserAdmin && accessToken) {
            window.location.href = `http://127.0.0.1:8000/admins/${accessToken}`;
        }
    }, [isUserAdmin, accessToken]); 
    
    if (!isUserAdmin) {
        return (
            <div className={styles.admin__loader}>
                <h1>Недостаточно привилегий</h1>
                <h2>Доступ только для администраторов</h2>
            </div>
        );
    }

    if (!accessToken) {
        return (
            <div className={styles.admin__loader}>
                <h1>Требуется авторизация</h1>
            </div>
        );
    }

    return (
        <div className={styles.admin__loader}>
            <h1>Загрузка админки...</h1>
        </div>
    );
}