import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import keycloak from "./keycloak";

interface AuthContextType {
  authenticated: boolean;
  token: string | null;
  login: () => void;
  logout: () => void;
  username: string | null;
}

const AuthContext = createContext<AuthContextType>({
  authenticated: false,
  token: null,
  login: () => {},
  logout: () => {},
  username: null,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    keycloak
      .init({ onLoad: "login-required", checkLoginIframe: false })
      .then((auth) => {
        setAuthenticated(auth);
        setToken(keycloak.token || null);
        setLoading(false);

        setInterval(() => {
          keycloak
            .updateToken(30)
            .then((refreshed) => {
              if (refreshed) setToken(keycloak.token || null);
            })
            .catch(() => keycloak.logout());
        }, 10000);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="center-screen">
        <div className="spinner" />
        <div>Загрузка…</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        token,
        login: () => keycloak.login(),
        logout: () => keycloak.logout(),
        username:
          keycloak.tokenParsed?.preferred_username ||
          keycloak.tokenParsed?.email ||
          null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
