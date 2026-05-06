// components/AuthLoader/AuthLoader.jsx
import { useEffect, useState, useRef } from 'react';
import { useAuthStore } from '../../../stores/authStore';
import { authService } from '../../../services/api/auth';

export function AuthLoader({ children }) {
    const [isChecking, setIsChecking] = useState(true);
    const { refreshToken, refreshAccessToken, setUserData } = useAuthStore();
    const hasCheckedRef = useRef(false);

    useEffect(() => {
        // Предотвращаем двойной вызов в StrictMode
        if (hasCheckedRef.current) return;
        hasCheckedRef.current = true;

        const checkAuth = async () => {
            console.log('[AuthLoader] Начало проверки, refreshToken:', refreshToken ? 'есть' : 'нет');
            
            if (refreshToken) {
                const success = await refreshAccessToken();
                
                if (success) {
                    // После успешного обновления токена, загружаем данные пользователя
                    try {
                        const userData = await authService.getCurrentUser();
                        setUserData(userData);
                        console.log('Пользователь загружен:', userData);
                    } catch (error) {
                        console.error('Ошибка загрузки пользователя:', error);
                    }
                } else {
                    // Токен не обновился, пользователь не авторизован
                    const { clearTokens } = useAuthStore.getState();
                    clearTokens();
                    console.log('Пользователь не авторизован');
                }
            } else {
                console.log('Нет refreshToken');
            }
            
            // Получаем финального пользователя
            const { user } = useAuthStore.getState();
            console.log('Текущий пользователь после загрузки:', user);
            
            setIsChecking(false);
        };
        
        checkAuth();
    }, [refreshToken, refreshAccessToken, setUserData]); // Добавили зависимости

    if (isChecking) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh' 
            }}>
                Загрузка...
            </div>
        );
    }

    return children;
}