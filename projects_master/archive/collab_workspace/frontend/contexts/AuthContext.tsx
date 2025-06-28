'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/services/api';

interface ServiceMember {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  service_branch: 'ARMY' | 'NAVY' | 'AIR_FORCE' | 'MARINES' | 'COAST_GUARD' | 'SPACE_FORCE';
  rank: string;
  mos_code: string;
  service_status: 'ACTIVE' | 'RESERVE' | 'NATIONAL_GUARD' | 'VETERAN' | 'RETIRED';
  deployment_status?: 'STATESIDE' | 'DEPLOYED' | 'COMBAT_ZONE' | 'TRAINING';
  unit?: string;
  base_location?: string;
  years_of_service: number;
  is_verified: boolean;
  verification_method?: 'CAC' | 'DD214' | 'MILITARY_EMAIL' | 'MANUAL';
  privacy_settings: {
    show_unit: boolean;
    show_location: boolean;
    show_deployment_status: boolean;
    allow_messages_from: 'ALL' | 'CONNECTIONS' | 'SAME_BRANCH' | 'SAME_UNIT' | 'NONE';
  };
  requires_2fa: boolean;
  has_2fa_enabled: boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
  two_factor_code?: string;
}

interface AuthContextType {
  user: ServiceMember | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isVerified: boolean;
  login: (credentials: LoginCredentials) => Promise<{ requires2FA: boolean }>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  updateProfile: (data: Partial<ServiceMember>) => Promise<void>;
  refreshToken: () => Promise<void>;
  checkOPSEC: (content: string) => Promise<OPSECCheckResult>;
}

interface RegisterData {
  email: string;
  password: string;
  username: string;
  first_name: string;
  last_name: string;
  service_branch: string;
  rank: string;
  mos_code: string;
  service_status: string;
  years_of_service: number;
}

interface OPSECCheckResult {
  is_safe: boolean;
  violations: Array<{
    type: string;
    severity: 'high' | 'medium' | 'low';
    message: string;
  }>;
  warning_message?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<ServiceMember | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in on mount
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      // Token invalid or expired
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      const { access_token, refresh_token, requires_2fa, user } = response.data;

      if (requires_2fa && !credentials.two_factor_code) {
        // Return early, user needs to provide 2FA code
        return { requires2FA: true };
      }

      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Set auth header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(user);
      router.push('/dashboard');
      
      return { requires2FA: false };
    } catch (error: any) {
      if (error.response?.status === 429) {
        throw new Error('Account locked due to too many failed attempts. Please try again later.');
      }
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if server request fails
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
      router.push('/');
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const response = await api.post('/auth/register', data);
      const { access_token, refresh_token, user } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(user);
      router.push('/verify'); // Redirect to verification page
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  };

  const updateProfile = async (data: Partial<ServiceMember>) => {
    try {
      const response = await api.patch('/users/me', data);
      setUser(response.data);
    } catch (error) {
      throw error;
    }
  };

  const refreshToken = async () => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      if (!refresh_token) throw new Error('No refresh token');

      const response = await api.post('/auth/refresh', { refresh_token });
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error) {
      // Refresh failed, logout user
      await logout();
      throw error;
    }
  };

  const checkOPSEC = async (content: string): Promise<OPSECCheckResult> => {
    try {
      const response = await api.post('/security/check-opsec', { content });
      return response.data;
    } catch (error) {
      // Return safe by default if check fails
      return { is_safe: true, violations: [] };
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isVerified: user?.is_verified || false,
    login,
    logout,
    register,
    updateProfile,
    refreshToken,
    checkOPSEC,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}