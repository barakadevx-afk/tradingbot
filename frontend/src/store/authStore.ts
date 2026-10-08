import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Token } from '../types';

interface AuthState {
  user: User | null;
  tokens: Token | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
  setTokens: (tokens: Token) => void;
  setUser: (user: User) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
          }

          const data = await response.json();
          const tokens: Token = {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            token_type: data.token_type || 'bearer',
            expires_in: data.expires_in || 1800,
          };

          localStorage.setItem('baraka_tokens', JSON.stringify(tokens));
          set({ tokens, isAuthenticated: true, isLoading: false });

          // Fetch user profile
          const profileResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/profile`, {
            headers: { Authorization: `Bearer ${tokens.access_token}` },
          });

          if (profileResponse.ok) {
            const user = await profileResponse.json();
            localStorage.setItem('baraka_user', JSON.stringify(user));
            set({ user });
          }
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
          throw error;
        }
      },

      register: async (email: string, password: string, full_name: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
          }

          set({ isLoading: false });
          // Auto-login after registration
          await get().login(email, password);
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('baraka_tokens');
        localStorage.removeItem('baraka_user');
        set({ user: null, tokens: null, isAuthenticated: false, error: null });
      },

      setTokens: (tokens: Token) => {
        localStorage.setItem('baraka_tokens', JSON.stringify(tokens));
        set({ tokens, isAuthenticated: true });
      },

      setUser: (user: User) => {
        localStorage.setItem('baraka_user', JSON.stringify(user));
        set({ user });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'baraka-auth',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
