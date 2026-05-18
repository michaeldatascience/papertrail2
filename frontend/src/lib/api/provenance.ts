import { ApiError, apiFetch } from '@/lib/api';

const API_BASE = `${(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '')}/api/v1`;

export interface NormalisedBbox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
  pixel_x?: number;
  pixel_y?: number;
  pixel_width?: number;
  pixel_height?: number;
}

export interface ProvenanceStage {
  stage: string;
  agent?: string;
  confidence?: number;
  reason?: string;
  timestamp?: string;
}

export interface FieldProvenance {
  field_name: string;
  page: number;
  bbox?: NormalisedBbox;
  confidence: number;
  extraction_path: string[];
  agent_signatures: string[];
  stages?: ProvenanceStage[];
  tiebreaker?: string;
  source_text?: string;
}

export interface DocumentProvenanceResponse {
  processing_id: string;
  engine: string;
  field_count: number;
  fields: Record<string, FieldProvenance>;
}

function normaliseField(fieldName: string, raw: Record<string, any>): FieldProvenance {
  const bbox = raw.bbox
    ? {
        page: Number(raw.bbox.page || raw.page || 1),
        x: Number(raw.bbox.x || 0),
        y: Number(raw.bbox.y || 0),
        width: Number(raw.bbox.width ?? raw.bbox.w ?? 0),
        height: Number(raw.bbox.height ?? raw.bbox.h ?? 0),
        pixel_x: raw.bbox.pixel_x,
        pixel_y: raw.bbox.pixel_y,
        pixel_width: raw.bbox.pixel_width,
        pixel_height: raw.bbox.pixel_height,
      }
    : undefined;

  return {
    field_name: fieldName,
    page: Number(raw.page || bbox?.page || 1),
    bbox,
    confidence: Number(raw.confidence ?? 0),
    extraction_path: Array.isArray(raw.extraction_path) ? raw.extraction_path : [],
    agent_signatures: Array.isArray(raw.agent_signatures) ? raw.agent_signatures : [],
    stages: Array.isArray(raw.stages) ? raw.stages : undefined,
    tiebreaker: raw.tiebreaker,
    source_text: raw.source_text,
  };
}

export async function fetchProvenance(processingId: string): Promise<DocumentProvenanceResponse> {
  const data = await apiFetch<DocumentProvenanceResponse>(`/documents/${processingId}/provenance`);
  const rawFields = (data.fields || {}) as Record<string, Record<string, any>>;
  const fields = Object.fromEntries(
    Object.entries(rawFields).map(([name, raw]) => [name, normaliseField(name, raw)]),
  );
  return { ...data, fields };
}

export function isProvenanceEmpty(data: DocumentProvenanceResponse | null | undefined) {
  return !data || !data.fields || Object.keys(data.fields).length === 0;
}

export function pageImageUrl(processingId: string, pageNumber: number) {
  return `${API_BASE}/documents/${processingId}/pages/${pageNumber}`;
}

export function pdfDownloadUrl(processingId: string) {
  return `${API_BASE}/documents/${processingId}/pdf`;
}

export { ApiError };
