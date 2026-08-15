import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      const user = {
        id: localStorage.getItem("user_id"),
        username: localStorage.getItem("username"),
        role: localStorage.getItem("role"),
        token,
      };
      setAuth(user);
    }
    setLoading(false);
  }, []);

  const login = (token_data) => {
    const user = {
      id: token_data.user_id,
      username: token_data.username,
      role: token_data.role,
      token: token_data.access_token,
    };
    setAuth(user);
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    setAuth(null);
  };

  const value = {
    auth,
    loading,
    login,
    logout,
    isAuthenticated: !!auth,
    token: auth?.token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// The provider and its hook intentionally share one small module.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
