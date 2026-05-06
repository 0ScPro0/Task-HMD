import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/api/auth';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            userRole: null,
            user: null,

            setTokens: (access, refresh, user = null) => {
                set({
                    accessToken: access,
                    refreshToken: refresh,
                    isAuthenticated: true,
                    userRole: user?.role || null,
                    user: user || null,
                });
            },

            clearTokens: () => {
                set({
                    accessToken: null,
                    refreshToken: null,
                    isAuthenticated: false,
                    userRole: null,
                    user: null,
                });
            },

            setUserData: (user) => {
                set({ userRole: user?.role || null, user: user || null });
            },
                        
            
            // Исправленный метод getCurrentUser
            getCurrentUser: async () => {
                const { accessToken, user } = get();
                
                // Если пользователь уже есть в store, возвращаем его
                if (user) return user;
                
                // Если нет токена, возвращаем null
                if (!accessToken) return null;
                
                try {
                    // Нужно добавить метод в authService для получения текущего пользователя
                    const currentUser = await authService.getCurrentUser();
                    set({ 
                        user: currentUser,
                        userRole: currentUser?.role || null
                    });
                    return currentUser;
                } catch (error) {
                    console.error("Failed to get current user:", error);
                    return null;
                }
            },

            refreshAccessToken: async () => {
                const { refreshToken } = get();
                if (!refreshToken) return false;

                try {
                    const data = await authService.refresh(refreshToken);
                    if (data?.access_token) {
                        set({ accessToken: data.access_token, isAuthenticated: true });
                        // Note: role is not updated on refresh, need to fetch user data separately
                        return true;
                    }
                    return false;
                } catch (error) {
                    set({ isAuthenticated: false, accessToken: null, refreshToken: null, userRole: null, user: null });
                    return false;
                }
            },
            
            getAccessToken: () => get().accessToken,
            isAdmin: () => get().userRole === 'admin',
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ refreshToken: state.refreshToken })
        }
    )
);