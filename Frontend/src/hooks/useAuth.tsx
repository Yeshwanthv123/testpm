import React, { createContext, useContext, useEffect, useState } from "react";
import { login as loginApi, register as registerApi, me as meApi, logout as logoutApi } from "../utils/auth";
import type { User } from "../utils/auth";

type Ctx = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  reload: () => Promise<void>;
};

const AuthCtx = createContext<Ctx | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function reload() {
    try {
      const u = await meApi();
      setUser(u);
    } catch {
      setUser(null);
    }
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    await loginApi(email, password);
    await reload();
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await registerApi(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    logoutApi();
    setUser(null);
  };

  return (
    <AuthCtx.Provider value={{ user, loading, login, register, logout, reload }}>
      {children}
    </AuthCtx.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
