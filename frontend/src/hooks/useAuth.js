import { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export function useAuthInit() {
    const navigate = useNavigate();
    const location = useLocation();
    const { refreshToken, refreshAccessToken } = useAuthStore();
    const isInitializedRef = useRef(false);

    useEffect(() => {
        const initAuth = async () => {
            // Предотвращаем повторную инициализацию
            if (isInitializedRef.current) return;
            
            const authPages = ['/login', '/register', '/login-executor'];
            const isAuthPage = authPages.includes(location.pathname);

            // Если на странице авторизации и есть refreshToken - редирект на главную
            if (isAuthPage && refreshToken) {
                isInitializedRef.current = true;
                navigate('/');
                return;
            }

            // Если не на странице авторизации
            if (!isAuthPage) {
                isInitializedRef.current = true;
                
                if (refreshToken) {
                    const success = await refreshAccessToken();
                    if (!success) {
                        navigate('/login');
                    }
                } else {
                    navigate('/login');
                }
            }
        };

        initAuth();
    }, [location.pathname]); // Только при смене пути

    // Сброс флага при полной перезагрузке страницы
    useEffect(() => {
        isInitializedRef.current = false;
    }, []);
}