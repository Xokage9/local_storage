export interface UserInfo {
  id: string;
  keycloak_id: string;
  email: string;
  display_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface StorageInfo {
  id: string;
  name: string;
  owner_id: string;
  storage_type: string;
  is_active: boolean;
  created_at: string;
}

export interface FolderInfo {
  id: string;
  storage_id: string;
  parent_id: string | null;
  name: string;
  created_at: string;
}

export interface FileInfo {
  id: string;
  storage_id: string;
  folder_id: string | null;
  original_name: string;
  mime_type: string | null;
  size_bytes: number;
  is_deleted: boolean;
  uploaded_by: string;
  created_at: string;
}

export interface MemberInfo {
  id: string;
  storage_id: string;
  user_id: string;
  role: string;
  created_at: string;
}

export interface ShareLinkInfo {
  id: string;
  token: string;
  file_id: string;
  created_by: string;
  expires_at: string | null;
  max_downloads: number | null;
  download_count: number;
  is_revoked: boolean;
  created_at: string;
}

export interface StorageStats {
  total_files: number;
  total_size_bytes: number;
  quota_bytes: number;
  usage_percent: number;
}

export interface StorageList {
  own: StorageInfo[];
  shared: StorageInfo[];
  global: StorageInfo[];
}
