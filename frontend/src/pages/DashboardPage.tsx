import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createStorage, fetchStorages } from "../api/storages";
import type { StorageInfo, StorageList } from "../types";

export default function DashboardPage() {
  const [storages, setStorages] = useState<StorageList | null>(null);
  const [newName, setNewName] = useState("");

  const load = () => fetchStorages().then(setStorages);

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createStorage(newName.trim());
    setNewName("");
    load();
  };

  if (!storages) {
    return (
      <div className="center-screen">
        <div className="spinner" />
        <div>Загрузка…</div>
      </div>
    );
  }

  const renderSection = (
    items: StorageInfo[],
    label: string,
    icon: string,
    emptyText: string
  ) => (
    <div className="section">
      <div className="section-head">
        <h2>{label}</h2>
        <span className="count-badge">{items.length}</span>
      </div>
      {items.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">{icon}</div>
          <div>{emptyText}</div>
        </div>
      ) : (
        <div className="card-grid">
          {items.map((s) => (
            <Link key={s.id} to={`/storage/${s.id}`} className="storage-card">
              <div className="storage-card-top">
                <span className="storage-icon">
                  {s.storage_type === "personal" ? "🗂️" : "🌐"}
                </span>
                <span className="storage-name">{s.name}</span>
              </div>
              <div className="storage-meta">
                <span className="pill pill-accent">
                  {s.storage_type === "personal" ? "Личное" : "Глобальное"}
                </span>
                <span>{new Date(s.created_at).toLocaleDateString("ru")}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div>
      <h1 className="page-title">Мои хранилища</h1>
      <p className="page-sub">
        Создавайте личные хранилища, делитесь файлами и управляйте доступом.
      </p>

      <div className="field-row" style={{ marginBottom: 36 }}>
        <input
          className="input"
          style={{ minWidth: 280 }}
          placeholder="Название нового хранилища"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />
        <button className="btn btn-primary" onClick={handleCreate}>
          + Создать хранилище
        </button>
      </div>

      {renderSection(storages.own, "Мои хранилища", "🗂️", "У вас пока нет хранилищ")}
      {renderSection(storages.shared, "Доступные мне", "🤝", "Вам пока ничего не открыли")}
      {renderSection(storages.global, "Глобальные", "🌐", "Глобальных хранилищ нет")}
    </div>
  );
}
