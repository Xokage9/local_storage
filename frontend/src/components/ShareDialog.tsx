import { useEffect, useState } from "react";
import { createShareLink, fetchShareLinks, revokeShareLink } from "../api/files";
import type { ShareLinkInfo } from "../types";

interface Props {
  fileId: string;
  onClose: () => void;
}

export default function ShareDialog({ fileId, onClose }: Props) {
  const [links, setLinks] = useState<ShareLinkInfo[]>([]);
  const [hours, setHours] = useState(24);
  const [maxDl, setMaxDl] = useState<number | "">("");
  const [copied, setCopied] = useState<string | null>(null);

  const load = () => fetchShareLinks(fileId).then(setLinks);
  useEffect(() => {
    load();
  }, [fileId]);

  const handleCreate = async () => {
    await createShareLink(fileId, hours, maxDl === "" ? undefined : maxDl);
    load();
  };

  const handleRevoke = async (token: string) => {
    await revokeShareLink(token);
    load();
  };

  const copyLink = (token: string) => {
    const url = `${window.location.origin}/api/v1/shared/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(token);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>🔗 Публичные ссылки</h2>
        </div>

        <div className="field-row" style={{ marginBottom: 20 }}>
          <span className="field-label">Часов:</span>
          <input
            className="input"
            style={{ width: 80 }}
            type="number"
            min={0}
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
          />
          <span className="field-label">Макс. скачиваний:</span>
          <input
            className="input"
            style={{ width: 90 }}
            type="number"
            min={1}
            value={maxDl}
            onChange={(e) =>
              setMaxDl(e.target.value === "" ? "" : Number(e.target.value))
            }
            placeholder="∞"
          />
          <button className="btn btn-primary" onClick={handleCreate}>
            Создать
          </button>
        </div>

        {links.length === 0 && (
          <p className="muted" style={{ textAlign: "center", padding: 12 }}>
            Нет созданных ссылок
          </p>
        )}

        {links.map((l) => (
          <div key={l.id} className="list-item">
            <div style={{ minWidth: 0 }}>
              <div className="mono" style={{ wordBreak: "break-all" }}>
                {l.token.substring(0, 24)}…
              </div>
              <div className="faint" style={{ marginTop: 3, fontSize: 12 }}>
                Скачиваний: {l.download_count}
                {l.max_downloads ? ` / ${l.max_downloads}` : ""}
                {l.is_revoked && (
                  <span style={{ color: "var(--danger)" }}> · отозвана</span>
                )}
                {l.expires_at && (
                  <span> · до {new Date(l.expires_at).toLocaleString("ru")}</span>
                )}
              </div>
            </div>
            <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => copyLink(l.token)}>
                {copied === l.token ? "✓ Готово" : "Копировать"}
              </button>
              {!l.is_revoked && (
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleRevoke(l.token)}
                >
                  Отозвать
                </button>
              )}
            </div>
          </div>
        ))}

        <div className="modal-foot">
          <button className="btn btn-ghost" onClick={onClose}>
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
}
