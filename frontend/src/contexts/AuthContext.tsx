import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin, getMe } from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  family_id?: string;
  member_id?: string;
  department_id?: number;
  department_name?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isGovernment: boolean;
  isCitizen: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('pravi_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      getMe()
        .then((res) => setUser(res.data.data))
        .catch(() => { localStorage.removeItem('pravi_token'); setToken(null); })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    const res = await apiLogin(username, password);
    const { access_token, user: userData } = res.data.data;
    localStorage.setItem('pravi_token', access_token);
    localStorage.setItem('pravi_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('pravi_token');
    localStorage.removeItem('pravi_user');
    setToken(null);
    setUser(null);
  };

  const isGovernment = !!user && user.role !== 'citizen';
  const isCitizen = !!user && user.role === 'citizen';

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isGovernment, isCitizen, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
