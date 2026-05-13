import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { changePassword as changePasswordRequest, getCurrentUser, login as loginRequest } from "../api/authApi";
import { AUTH_TOKEN_STORAGE_KEY } from "../api/httpClient";
import type { AuthUser, LoginRequest } from "../types/auth";
import type { Role } from "../types/common";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginRequest) => Promise<AuthUser>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<AuthUser>;
  logout: () => void;
  hasRole: (roles: Role[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY));
  const [isLoading, setIsLoading] = useState<boolean>(token !== null);

  const logout = useCallback((): void => {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    window.addEventListener("auth:logout", logout);
    return () => {
      window.removeEventListener("auth:logout", logout);
    };
  }, [logout]);

  useEffect(() => {
    let isMounted = true;
    async function hydrateUser(): Promise<void> {
      if (token === null) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await getCurrentUser();
        if (isMounted) {
          setUser(currentUser);
        }
      } catch {
        if (isMounted) {
          logout();
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }
    void hydrateUser();
    return () => {
      isMounted = false;
    };
  }, [logout, token]);

  const login = useCallback(async (payload: LoginRequest): Promise<AuthUser> => {
    const authToken = await loginRequest(payload);
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, authToken.access_token);
    setToken(authToken.access_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    return currentUser;
  }, []);

  const changePassword = useCallback(
    async (currentPassword: string, newPassword: string): Promise<AuthUser> => {
      const updatedUser = await changePasswordRequest({
        current_password: currentPassword,
        new_password: newPassword
      });
      setUser(updatedUser);
      return updatedUser;
    },
    []
  );

  const hasRole = useCallback(
    (roles: Role[]): boolean => user !== null && roles.includes(user.role),
    [user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: user !== null && token !== null,
      isLoading,
      login,
      changePassword,
      logout,
      hasRole
    }),
    [changePassword, hasRole, isLoading, login, logout, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return context;
}
