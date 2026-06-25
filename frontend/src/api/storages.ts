import api from "./client";
import type {
  FolderInfo,
  MemberInfo,
  StorageInfo,
  StorageList,
  StorageStats,
} from "../types";

export async function fetchStorages(): Promise<StorageList> {
  const { data } = await api.get("/storages");
  return data;
}

export async function createStorage(
  name: string,
  storageType = "global"
): Promise<StorageInfo> {
  const { data } = await api.post("/storages", {
    name,
    storage_type: storageType,
  });
  return data;
}

export async function getStorage(id: string): Promise<StorageInfo> {
  const { data } = await api.get(`/storages/${id}`);
  return data;
}

export async function deleteStorage(id: string): Promise<void> {
  await api.delete(`/storages/${id}`);
}

export async function getStorageStats(id: string): Promise<StorageStats> {
  const { data } = await api.get(`/storages/${id}/stats`);
  return data;
}

export async function fetchFolders(
  storageId: string,
  parentId?: string | null
): Promise<FolderInfo[]> {
  const params: Record<string, string> = {};
  if (parentId) params.parent_id = parentId;
  const { data } = await api.get(`/storages/${storageId}/folders`, { params });
  return data;
}

export async function createFolder(
  storageId: string,
  name: string,
  parentId?: string | null
): Promise<FolderInfo> {
  const { data } = await api.post(`/storages/${storageId}/folders`, {
    name,
    parent_id: parentId || null,
  });
  return data;
}

export async function renameFolder(
  folderId: string,
  name: string
): Promise<FolderInfo> {
  const { data } = await api.put(`/folders/${folderId}`, { name });
  return data;
}

export async function deleteFolder(folderId: string): Promise<void> {
  await api.delete(`/folders/${folderId}`);
}

export async function fetchMembers(storageId: string): Promise<MemberInfo[]> {
  const { data } = await api.get(`/storages/${storageId}/members`);
  return data;
}

export async function addMember(
  storageId: string,
  userId: string,
  role: string
): Promise<MemberInfo> {
  const { data } = await api.post(`/storages/${storageId}/members`, {
    user_id: userId,
    role,
  });
  return data;
}

export async function removeMember(
  storageId: string,
  userId: string
): Promise<void> {
  await api.delete(`/storages/${storageId}/members/${userId}`);
}
