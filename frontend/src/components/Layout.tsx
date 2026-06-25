import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Layout() {
  const { username, logout } = useAuth();
  const initial = (username || "?").charAt(0);

  return (
    <>
      <header className="app-header">
        <Link to="/" className="app-logo">
          <span className="logo-mark">☁</span>
          Файловое хранилище
        </Link>
        <div className="user-block">
          <span className="user-name">
            <span className="user-avatar">{initial}</span>
            {username}
          </span>
          <button className="btn btn-ghost btn-sm" onClick={logout}>
            Выйти
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </>
  );
}
