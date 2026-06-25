import api from "./client";
import type { FileInfo, ShareLinkInfo } from "../types";

export async function fetchFiles(
  storageId: string,
  folderId?: string | null
): Promise<FileInfo[]> {
  const params: Record<string, string> = {};
  if (folderId) params.folder_id = folderId;
  const { data } = await api.get(`/storages/${storageId}/files`, { params });
  return data;
}

export async function uploadFile(
  storageId: string,
  file: File,
  folderId?: string | null
): Promise<FileInfo> {
  const form = new FormData();
  form.append("file", file);
  const params: Record<string, string> = {};
  if (folderId) params.folder_id = folderId;
  const { data } = await api.post(`/storages/${storageId}/files`, form, {
    params,
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function downloadFile(fileId: string, filename: string) {
  const { data } = await api.get(`/files/${fileId}/download`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function viewFile(fileId: string) {
  const { data } = await api.get(`/files/${fileId}/download`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(data);
  window.open(url, "_blank", "noopener");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

export async function renameFile(
  fileId: string,
  name: string
): Promise<FileInfo> {
  const { data } = await api.put(`/files/${fileId}/rename`, { name });
  return data;
}

export async function moveFile(
  fileId: string,
  folderId: string | null
): Promise<FileInfo> {
  const { data } = await api.put(`/files/${fileId}/move`, {
    folder_id: folderId,
  });
  return data;
}

export async function deleteFile(fileId: string): Promise<void> {
  await api.delete(`/files/${fileId}`);
}

export async function searchFiles(
  storageId: string,
  query: string
): Promise<FileInfo[]> {
  const { data } = await api.get(`/storages/${storageId}/search`, {
    params: { q: query },
  });
  return data;
}

export async function createShareLink(
  fileId: string,
  expiresInHours?: number,
  maxDownloads?: number
): Promise<ShareLinkInfo> {
  const { data } = await api.post(`/files/${fileId}/share-links`, {
    expires_in_hours: expiresInHours ?? 24,
    max_downloads: maxDownloads ?? null,
  });
  return data;
}

export async function fetchShareLinks(
  fileId: string
): Promise<ShareLinkInfo[]> {
  const { data } = await api.get(`/files/${fileId}/share-links`);
  return data;
}

export async function revokeShareLink(token: string): Promise<void> {
  await api.delete(`/share-links/${token}`);
}
