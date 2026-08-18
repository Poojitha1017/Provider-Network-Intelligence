import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { loginApi, signupApi, getMeApi } from "../services/api";

export interface AuthUser {
  id?: string;
  fullName: string;
  email: string;
  mobile?: string;
  organization?: string;
  role: string;
}

interface SignupInput {
  fullName: string;
  email: string;
  mobile?: string;
  organization?: string;
  role: string;
  password: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
  signup: (input: SignupInput) => Promise<{ ok: boolean; error?: string }>;
  logout: () => void;
}

const SESSION_KEY = "pni_session";
const TOKEN_KEY = "pni_token";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initSession() {
      try {
        const token = localStorage.getItem(TOKEN_KEY);
        const rawUser = localStorage.getItem(SESSION_KEY);
        if (rawUser) {
          setUser(JSON.parse(rawUser) as AuthUser);
        }
        if (token) {
          try {
            const me = await getMeApi(token);
            if (me) {
              setUser(me);
              localStorage.setItem(SESSION_KEY, JSON.stringify(me));
            }
          } catch {
            // Token might be expired
          }
        }
      } catch {
        // ignore corrupt session
      } finally {
        setLoading(false);
      }
    }
    initSession();
  }, []);

  const login: AuthContextValue["login"] = async (email, password) => {
    try {
      const data = await loginApi(email, password);
      if (data && data.access_token && data.user) {
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(SESSION_KEY, JSON.stringify(data.user));
        setUser(data.user);
        return { ok: true };
      }
      return { ok: false, error: "Invalid response from authentication server." };
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Invalid email or password.";
      return { ok: false, error: errorMsg };
    }
  };

  const signup: AuthContextValue["signup"] = async (input) => {
    try {
      const res = await signupApi(input);
      if (res && res.success) {
        // If signup requires email verification, attempt login or guide user
        try {
          const loginRes = await loginApi(input.email, input.password);
          if (loginRes?.access_token && loginRes.user) {
            localStorage.setItem(TOKEN_KEY, loginRes.access_token);
            localStorage.setItem(SESSION_KEY, JSON.stringify(loginRes.user));
            setUser(loginRes.user);
            return { ok: true };
          }
        } catch {
          // Verification email was sent
        }
        return { ok: true };
      }
      return { ok: false, error: res.message || "Failed to create account." };
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Unable to register account.";
      return { ok: false, error: errorMsg };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(SESSION_KEY);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
