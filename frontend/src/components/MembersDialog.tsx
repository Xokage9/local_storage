import { useEffect, useState } from "react";
import { addMember, fetchMembers, removeMember } from "../api/storages";
import api from "../api/client";
import type { MemberInfo } from "../types";

const ROLES = ["viewer", "uploader", "editor", "admin"];
const ROLE_LABELS: Record<string, string> = {
  owner: "Владелец",
  admin: "Администратор",
  editor: "Редактор",
  viewer: "Просмотр",
  uploader: "Загрузка",
};

interface Props {
  storageId: string;
  onClose: () => void;
}

export default function MembersDialog({ storageId, onClose }: Props) {
  const [members, setMembers] = useState<MemberInfo[]>([]);
  const [searchEmail, setSearchEmail] = useState("");
  const [searchResults, setSearchResults] = useState<
    { id: string; email: string; display_name: string | null }[]
  >([]);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [role, setRole] = useState("viewer");

  const load = () => fetchMembers(storageId).then(setMembers);
  useEffect(() => {
    load();
  }, [storageId]);

  const handleSearch = async () => {
    if (!searchEmail.trim()) return;
    const { data } = await api.get("/users/search", {
      params: { q: searchEmail },
    });
    setSearchResults(data);
  };

  const handleAdd = async () => {
    if (!selectedUserId) return;
    await addMember(storageId, selectedUserId, role);
    setSelectedUserId(null);
    setSearchEmail("");
    setSearchResults([]);
    load();
  };

  const handleRemove = async (userId: string) => {
    await removeMember(storageId, userId);
    load();
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>👥 Участники хранилища</h2>
        </div>

        {members.map((m) => (
          <div key={m.id} className="list-item">
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span className="mono">{m.user_id.substring(0, 8)}…</span>
              <span className={`pill ${m.role === "owner" ? "pill-owner" : ""}`}>
                {ROLE_LABELS[m.role] || m.role}
              </span>
            </div>
            {m.role !== "owner" && (
              <button
                className="btn btn-danger btn-sm"
                onClick={() => handleRemove(m.user_id)}
              >
                Удалить
              </button>
            )}
          </div>
        ))}

        <h3 style={{ marginTop: 22, marginBottom: 10, fontSize: 14 }}>
          Добавить участника
        </h3>
        <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
          <input
            className="input"
            style={{ flex: 1 }}
            placeholder="Email пользователя"
            value={searchEmail}
            onChange={(e) => setSearchEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button className="btn btn-ghost" onClick={handleSearch}>
            Найти
          </button>
        </div>

        {searchResults.map((u) => (
          <div
            key={u.id}
            onClick={() => setSelectedUserId(u.id)}
            className={`result-item${selectedUserId === u.id ? " selected" : ""}`}
          >
            {u.email} {u.display_name ? `(${u.display_name})` : ""}
          </div>
        ))}

        {selectedUserId && (
          <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
            <select
              className="select"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABELS[r]}
                </option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={handleAdd}>
              Добавить
            </button>
          </div>
        )}

        <div className="modal-foot">
          <button className="btn btn-ghost" onClick={onClose}>
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
}
