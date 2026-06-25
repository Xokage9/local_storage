import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  deleteFile,
  downloadFile,
  fetchFiles,
  moveFile,
  renameFile,
  searchFiles,
  uploadFile,
  viewFile,
} from "../api/files";
import {
  createFolder,
  deleteFolder,
  deleteStorage,
  fetchFolders,
  getStorage,
  getStorageStats,
  renameFolder,
} from "../api/storages";
import ShareDialog from "../components/ShareDialog";
import MembersDialog from "../components/MembersDialog";
import type { FileInfo, FolderInfo, StorageInfo, StorageStats } from "../types";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} ГБ`;
}

export default function StoragePage() {
  const { storageId } = useParams<{ storageId: string }>();
  const [storage, setStorage] = useState<StorageInfo | null>(null);
  const [stats, setStats] = useState<StorageStats | null>(null);
  const [folders, setFolders] = useState<FolderInfo[]>([]);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [path, setPath] = useState<{ id: string | null; name: string }[]>([
    { id: null, name: "Корень" },
  ]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<FileInfo[] | null>(null);
  const [newFolderName, setNewFolderName] = useState("");
  const [shareFileId, setShareFileId] = useState<string | null>(null);
  const [showMembers, setShowMembers] = useState(false);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [movingFileId, setMovingFileId] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const currentFolderId = path[path.length - 1].id;

  const load = useCallback(() => {
    if (!storageId) return;
    getStorage(storageId).then(setStorage);
    getStorageStats(storageId).then(setStats);
    fetchFolders(storageId, currentFolderId).then(setFolders);
    fetchFiles(storageId, currentFolderId).then(setFiles);
  }, [storageId, currentFolderId]);

  useEffect(() => {
    load();
  }, [load]);

  const openFolder = (folder: FolderInfo) => {
    setSearchResults(null);
    setPath((p) => [...p, { id: folder.id, name: folder.name }]);
  };

  const goTo = (idx: number) => {
    setSearchResults(null);
    setPath((p) => p.slice(0, idx + 1));
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !storageId) return;
    await uploadFile(storageId, file, currentFolderId);
    load();
    e.target.value = "";
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim() || !storageId) return;
    await createFolder(storageId, newFolderName.trim(), currentFolderId);
    setNewFolderName("");
    load();
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !storageId) return;
    const res = await searchFiles(storageId, searchQuery.trim());
    setSearchResults(res);
  };

  const handleRenameFile = async (fileId: string) => {
    if (!renameValue.trim()) return;
    await renameFile(fileId, renameValue.trim());
    setRenamingId(null);
    load();
  };

  const handleRenameFolder = async (folderId: string) => {
    if (!renameValue.trim()) return;
    await renameFolder(folderId, renameValue.trim());
    setRenamingId(null);
    load();
  };

  const handleMoveFile = async (fileId: string, targetFolderId: string | null) => {
    await moveFile(fileId, targetFolderId);
    setMovingFileId(null);
    load();
  };

  const handleDeleteStorage = async () => {
    if (!storageId || !confirm("Удалить хранилище?")) return;
    await deleteStorage(storageId);
    window.location.href = "/";
  };

  if (!storage) {
    return (
      <div className="center-screen">
        <div className="spinner" />
        <div>Загрузка…</div>
      </div>
    );
  }

  const displayFiles = searchResults ?? files;
  const isEmpty =
    displayFiles.length === 0 && (searchResults ? true : folders.length === 0);

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          marginBottom: 18,
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div>
          <Link to="/" className="faint" style={{ fontSize: 13 }}>
            ← Все хранилища
          </Link>
          <h1 className="page-title" style={{ marginTop: 6 }}>
            {storage.name}
          </h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" onClick={() => setShowMembers(true)}>
            👥 Участники
          </button>
          <button className="btn btn-danger" onClick={handleDeleteStorage}>
            Удалить
          </button>
        </div>
      </div>

      {stats && (
        <div className="quota">
          <div className="quota-head">
            <span>
              {formatSize(stats.total_size_bytes)} из {formatSize(stats.quota_bytes)}
            </span>
            <span className="faint">
              {stats.usage_percent}% · файлов: {stats.total_files}
            </span>
          </div>
          <div className="quota-track">
            <div
              className="quota-fill"
              style={{ width: `${Math.min(stats.usage_percent, 100)}%` }}
            />
          </div>
        </div>
      )}

      <div className="breadcrumb">
        {path.map((p, i) => (
          <span key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            {i > 0 && <span className="crumb-sep">/</span>}
            <span
              onClick={() => i < path.length - 1 && goTo(i)}
              className={`crumb${i === path.length - 1 ? " current" : ""}`}
            >
              {p.name}
            </span>
          </span>
        ))}
      </div>

      <div className="toolbar">
        <input
          type="file"
          ref={fileInput}
          onChange={handleUpload}
          style={{ display: "none" }}
        />
        <button className="btn btn-primary" onClick={() => fileInput.current?.click()}>
          ⬆ Загрузить файл
        </button>
        <input
          className="input"
          placeholder="Новая папка"
          value={newFolderName}
          onChange={(e) => setNewFolderName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreateFolder()}
        />
        <button className="btn btn-ghost" onClick={handleCreateFolder}>
          + Папка
        </button>
        <div className="toolbar-spacer" />
        <div className="search-wrap">
          <input
            className="input"
            placeholder="Поиск файлов…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button className="btn btn-outline" onClick={handleSearch}>
            Найти
          </button>
          {searchResults && (
            <button
              className="btn btn-outline"
              onClick={() => {
                setSearchResults(null);
                setSearchQuery("");
              }}
            >
              Сброс
            </button>
          )}
        </div>
      </div>

      {isEmpty ? (
        <div className="empty">
          <div className="empty-icon">📂</div>
          <div>
            {searchResults
              ? "Ничего не найдено"
              : "Хранилище пусто. Загрузите файлы или создайте папку."}
          </div>
        </div>
      ) : (
        <div className="panel">
          {!searchResults &&
            folders.map((f) => (
              <div key={f.id} className="row">
                <div className="row-main">
                  <span className="row-icon">📁</span>
                  {renamingId === f.id ? (
                    <input
                      className="input"
                      value={renameValue}
                      autoFocus
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleRenameFolder(f.id)}
                      onBlur={() => setRenamingId(null)}
                    />
                  ) : (
                    <span
                      className="row-name clickable"
                      onClick={() => openFolder(f)}
                    >
                      {f.name}
                    </span>
                  )}
                </div>
                <div className="row-actions">
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => {
                      setRenamingId(f.id);
                      setRenameValue(f.name);
                    }}
                  >
                    Переименовать
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={async () => {
                      await deleteFolder(f.id);
                      load();
                    }}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}

          {displayFiles.map((f) => (
            <div key={f.id} className="row">
              <div className="row-main">
                <span className="row-icon">📄</span>
                {renamingId === f.id ? (
                  <input
                    className="input"
                    value={renameValue}
                    autoFocus
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleRenameFile(f.id)}
                    onBlur={() => setRenamingId(null)}
                  />
                ) : (
                  <span className="row-name">{f.original_name}</span>
                )}
                <span className="row-size">{formatSize(f.size_bytes)}</span>
              </div>
              <div className="row-actions">
                <button className="btn btn-ghost btn-sm" onClick={() => viewFile(f.id)}>
                  Просмотр
                </button>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => downloadFile(f.id, f.original_name)}
                >
                  Скачать
                </button>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => {
                    setRenamingId(f.id);
                    setRenameValue(f.original_name);
                  }}
                >
                  Переименовать
                </button>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => setMovingFileId(movingFileId === f.id ? null : f.id)}
                >
                  Переместить
                </button>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => setShareFileId(f.id)}
                >
                  Поделиться
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={async () => {
                    await deleteFile(f.id);
                    load();
                  }}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {movingFileId && (
        <div
          style={{
            padding: 14,
            background: "var(--surface-2)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            marginTop: 14,
            fontSize: 13,
          }}
        >
          <strong>Переместить в:</strong>
          <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
            {currentFolderId && (
              <button
                className="btn btn-outline btn-sm"
                onClick={() => handleMoveFile(movingFileId, null)}
              >
                📂 Корень
              </button>
            )}
            {folders.map((f) => (
              <button
                key={f.id}
                className="btn btn-outline btn-sm"
                onClick={() => handleMoveFile(movingFileId, f.id)}
              >
                📁 {f.name}
              </button>
            ))}
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setMovingFileId(null)}
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {shareFileId && (
        <ShareDialog fileId={shareFileId} onClose={() => setShareFileId(null)} />
      )}

      {showMembers && storageId && (
        <MembersDialog storageId={storageId} onClose={() => setShowMembers(false)} />
      )}
    </div>
  );
}
