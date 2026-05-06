// components/AuthLoader/AuthLoader.jsx
import { useEffect, useState } from 'react';
import { useAuthStore } from '../../../stores/authStore';

export function AuthLoader({ children }) {
    const [isChecking, setIsChecking] = useState(true);
    const { refreshToken, refreshAccessToken } = useAuthStore();

    useEffect(() => {
        const checkAuth = async () => {
            if (refreshToken) {
                const success = await refreshAccessToken();
                if (!success) {
                    // Токен не обновился, пользователь не авторизован
                    const { clearTokens } = useAuthStore.getState();
                    clearTokens();
                }
            }
            setIsChecking(false);
        };

        checkAuth();
    }, []);

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