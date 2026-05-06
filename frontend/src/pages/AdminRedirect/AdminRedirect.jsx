import { useEffect } from 'react'; // ← правильный импорт
import styles from './AdminRedirect.module.css';

export function AdminRedirect() {
    useEffect(() => {
        window.location.href = 'https://127.0.0.1:8000/admin';
    }, []);
    
    return (
        <div className={styles.admin__loader}>
            <h1>Загрузка админки...</h1>
        </div>
    );
}