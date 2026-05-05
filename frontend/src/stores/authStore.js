import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/api/auth';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,

            setTokens: (access, refresh) => {
                set({ accessToken: access, refreshToken: refresh, isAuthenticated: true });
            },

            clearTokens: () => {
                set({ accessToken: null, refreshToken: null, isAuthenticated: false });
            },

            refreshAccessToken: async () => {
                const { refreshToken } = get();
                if (!refreshToken) return false;

                try {
                    const data = await authService.refresh(refreshToken);
                    if (data?.access_token) {
                        set({ accessToken: data.access_token, isAuthenticated: true });
                        return true;
                    }
                    return false;
                } catch (error) {
                    set({ isAuthenticated: false, accessToken: null, refreshToken: null });
                    return false;
                }
            },
            
            getAccessToken: () => get().accessToken,
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ refreshToken: state.refreshToken })
        }
    )
);