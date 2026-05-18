import type {
  DashboardMetrics,
  HealthResponse,
  LoginRequest,
  LoginResponse,
  PreviewResponse,
  ProcessResponse,
  QueueStats,
  RecentActivity,
  SchemaInfo,
  TaskStatusResponse,
  User,
  WorkerStatus,
} from '@/types/api';

const API_ROOT = `${(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '')}/api/v1`;
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

export function getAccessToken() {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

function setTokens(tokens: { access_token?: string; refresh_token?: string }) {
  if (typeof window === 'undefined') return;
  if (tokens.access_token) window.localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  if (tokens.refresh_token) window.localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

function clearTokens() {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(init.headers || {});
  if (!headers.has('Accept')) headers.set('Accept', 'application/json');
  if (token && !headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`);

  const isForm = typeof FormData !== 'undefined' && init.body instanceof FormData;
  if (init.body && !isForm && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  });

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === 'string'
      ? payload
      : (payload as { detail?: string; message?: string })?.detail ||
        (payload as { detail?: string; message?: string })?.message ||
        `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

async function apiBlob(path: string, init: RequestInit = {}) {
  const token = getAccessToken();
  const headers = new Headers(init.headers || {});
  if (token && !headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  });
  if (!response.ok) {
    throw new ApiError(`Download failed (${response.status})`, response.status);
  }
  return response.blob();
}

function normaliseDashboardMetrics(data: unknown): DashboardMetrics {
  const d = (data || {}) as Record<string, any>;
  const processing = d.processing || {};
  const queue = d.queue || {};
  return {
    documents_processed_today: processing.documents_processed_today || 0,
    documents_processed_week: processing.documents_processed_week || 0,
    success_rate: processing.success_rate || 0,
    average_processing_time: processing.average_processing_time || 0,
    active_tasks: queue.active_tasks || 0,
    pending_tasks: queue.pending_tasks || 0,
    failed_tasks_today: processing.failed_today || 0,
    human_review_pending: processing.human_review_pending || 0,
  };
}

export const authApi = {
  async login(payload: LoginRequest): Promise<LoginResponse> {
    const data = await apiFetch<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    setTokens(data);
    return data;
  },
  async signup(payload: Record<string, unknown>) {
    return apiFetch('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async getCurrentUser(): Promise<User> {
    return apiFetch<User>('/auth/me');
  },
  async logout() {
    try {
      await apiFetch('/auth/logout', { method: 'POST' });
    } finally {
      clearTokens();
    }
  },
};

export const healthApi = {
  async basic(): Promise<HealthResponse> {
    return apiFetch<HealthResponse>('/health');
  },
  async detailed(): Promise<HealthResponse> {
    try {
      return await apiFetch<HealthResponse>('/health/detailed');
    } catch {
      return healthApi.basic();
    }
  },
};

export const dashboardApi = {
  async getMetrics(): Promise<DashboardMetrics> {
    const data = await apiFetch('/dashboard/metrics');
    return normaliseDashboardMetrics(data);
  },
  async getActivity(limit = 10): Promise<RecentActivity[]> {
    return apiFetch<RecentActivity[]>(`/dashboard/activity?limit=${limit}`);
  },
};

export const tasksApi = {
  async listActive(): Promise<TaskStatusResponse[]> {
    return apiFetch<TaskStatusResponse[]>('/tasks/active');
  },
  async list(): Promise<TaskStatusResponse[]> {
    return tasksApi.listActive();
  },
  async get(taskId: string): Promise<TaskStatusResponse> {
    return apiFetch<TaskStatusResponse>(`/tasks/${taskId}`);
  },
  async cancel(taskId: string) {
    return apiFetch(`/tasks/${taskId}`, { method: 'DELETE' });
  },
  async retry(taskId: string) {
    return apiFetch(`/tasks/${taskId}/retry`, { method: 'POST' });
  },
};

export const queueApi = {
  async getStats(): Promise<QueueStats[]> {
    return apiFetch<QueueStats[]>('/queue/stats');
  },
  async getWorkers(): Promise<WorkerStatus[]> {
    return apiFetch<WorkerStatus[]>('/queue/workers');
  },
};

export const schemaApi = {
  async list(): Promise<SchemaInfo[]> {
    const data = await apiFetch<{ schemas?: SchemaInfo[] } | SchemaInfo[]>('/schemas');
    return Array.isArray(data) ? data : data.schemas || [];
  },
  async get(name: string) {
    return apiFetch(`/schemas/${encodeURIComponent(name)}`);
  },
};

export const documentsApi = {
  async upload(file: File, options: Record<string, unknown>) {
    const formData = new FormData();
    formData.append('file', file);
    for (const [key, value] of Object.entries(options)) {
      if (value === undefined || value === null) continue;
      if (Array.isArray(value)) {
        value.forEach((entry) => formData.append(key, String(entry)));
      } else {
        formData.append(key, String(value));
      }
    }
    return apiFetch<{ task_id: string; status: string; message: string; status_url: string }>('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },
  async listRecent(): Promise<ProcessResponse[]> {
    return [];
  },
  async get(processingId: string): Promise<ProcessResponse> {
    return apiFetch<ProcessResponse>(`/documents/${processingId}`);
  },
  async reprocess(processingId: string) {
    return apiFetch(`/documents/${processingId}/reprocess`, { method: 'POST' });
  },
  async delete(processingId: string) {
    return apiFetch(`/documents/${processingId}`, { method: 'DELETE' });
  },
  async export(processingId: string, format: 'json' | 'excel' | 'markdown') {
    if (format === 'markdown') {
      const preview = await apiFetch<PreviewResponse>(`/documents/${processingId}/preview`, {
        method: 'POST',
      });
      return new Blob([preview.content], { type: 'text/markdown;charset=utf-8' });
    }
    const doc = await apiFetch<ProcessResponse>(`/documents/${processingId}`);
    return new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json;charset=utf-8' });
  },
};

export const previewApi = {
  async markdown(processingId: string, maskPhi = false) {
    const data = await apiFetch<PreviewResponse>(`/documents/${processingId}/preview?mask_phi=${maskPhi ? 'true' : 'false'}`, {
      method: 'POST',
    });
    return data.content;
  },
};

export const exportApi = {
  async download(processingId: string, format: 'json' | 'excel' | 'markdown' | 'fhir') {
    const blob = format === 'markdown'
      ? await documentsApi.export(processingId, 'markdown')
      : await documentsApi.export(processingId, 'json');
    const ext = format === 'excel' ? 'xlsx' : format === 'fhir' ? 'json' : format;
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${processingId}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};

export { apiBlob, apiFetch };
