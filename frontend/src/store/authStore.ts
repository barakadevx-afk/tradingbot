import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Token } from '../types';
import { API_BASE_URL, API_CONFIGURED } from '../services/api';

function ensureApiConfigured(): void {
  if (!API_CONFIGURED) {
    throw new Error(
      'Account access is unavailable because the trading API has not been deployed yet.',
    );
  }
}

async function getErrorMessage(response: Response, fallback: string): Promise<string> {
  const body = await response.text();
  if (body) {
    try {
      const parsed = JSON.parse(body) as { detail?: unknown };
      if (typeof parsed.detail === 'string') return parsed.detail;
    } catch {
      // Use the HTTP status when the API response is not JSON.
    }
  }

  return response.status >= 500
    ? `Server error (${response.status}). Please try again later.`
    : `${fallback} (${response.status}).`;
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
          const response = await fetch(`${API_BASE_URL}/auth/login/json`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          });

          if (!response.ok) {
            throw new Error(await getErrorMessage(response, 'Login failed'));
          }

          const data = await response.json();
          const tokens: Token = {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            token_type: data.token_type || 'bearer',
            expires_in: data.expires_in || 1800,
          };

          // Fetch user profile
          const profileResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${tokens.access_token}` },
          });

          if (!profileResponse.ok) {
            throw new Error('Signed in, but could not load your user profile.');
          }

          const user = await profileResponse.json();
          localStorage.setItem('baraka_tokens', JSON.stringify(tokens));
          localStorage.setItem('baraka_user', JSON.stringify(user));
          set({ tokens, user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({ error: (error as Error).message, isLoading: false });
          throw error;
        }
      },

      register: async (email: string, password: string, full_name: string) => {
        set({ isLoading: true, error: null });
        try {
          ensureApiConfigured();
          const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name }),
          });

          if (!response.ok) {
            throw new Error(await getErrorMessage(response, 'Registration failed'));
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
