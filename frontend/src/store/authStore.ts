import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, API_CONFIGURED } from '../services/api';
import type { User, Token } from '../types';

function ensureApiConfigured(): void {
  if (!API_CONFIGURED) {
    throw new Error(
      'Account access is unavailable because the trading API has not been deployed yet.',
    );
  }
}

function normalizeError(error: unknown, fallback: string): string {
  if (typeof error === 'string' && error.trim()) {
    return error;
  }

  const maybeError = error as { response?: { data?: { detail?: string } }; message?: string };
  const detail = maybeError?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  const message = maybeError?.message;
  if (typeof message === 'string' && message.trim()) {
    return message;
  }

  return fallback;
}

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
          ensureApiConfigured();

          const loginResponse = await authApi.login({ email, password });
          const tokens: Token = {
            access_token: loginResponse.data.access_token,
            refresh_token: loginResponse.data.refresh_token,
            token_type: loginResponse.data.token_type || 'bearer',
            expires_in: loginResponse.data.expires_in || 1800,
          };

          const profileResponse = await authApi.getProfile();
          const user = profileResponse.data as User;

          localStorage.setItem('baraka_tokens', JSON.stringify(tokens));
          localStorage.setItem('baraka_user', JSON.stringify(user));
          set({ tokens, user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          const message = normalizeError(error, 'Login failed');
          set({ error: message, isLoading: false });
          throw new Error(message);
        }
      },

      register: async (email: string, password: string, full_name: string) => {
        set({ isLoading: true, error: null });
        try {
          ensureApiConfigured();
          await authApi.register({ email, password, full_name });
          set({ isLoading: false });
          await get().login(email, password);
        } catch (error) {
          const message = normalizeError(error, 'Registration failed');
          set({ error: message, isLoading: false });
          throw new Error(message);
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
