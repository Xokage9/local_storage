import { Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthProvider";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import StoragePage from "./pages/StoragePage";

export default function App() {
  const { authenticated } = useAuth();

  if (!authenticated) {
    return (
      <div className="center-screen">
        <div className="spinner" />
        <div>Авторизация через Keycloak…</div>
      </div>
    );
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/storage/:storageId" element={<StoragePage />} />
      </Route>
    </Routes>
  );
}
