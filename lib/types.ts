export type JobStatus = "queued" | "running" | "done" | "error";

export type GarmentCategory = "tops" | "bottoms" | "outerwear" | "dress" | "shoes" | "accessory";

export type TryOnJobSummary = {
  id: string;
  status: JobStatus;
  thumbnailUrl: string;
  latencyMs: number | null;
  createdAt: string;
};

export type TryOnJobResult = {
  status: JobStatus;
  images?: string[];
  sourceImages?: string[];
  latencyMs?: number;
  error?: string;
};

export type CreateTryOnJobInput = {
  person: File[];
  garment: File;
  category: GarmentCategory;
  brandId?: string;
  steps?: number;
};

export type CreateTryOnJobResponse = {
  jobId: string;
};

export type JobsResponse = {
  jobs: TryOnJobSummary[];
};

export type HealthResponse = {
  ok: boolean;
};

export type ApiMode = "mock" | "live";

export type ApiConfig = {
  baseUrl: string;
  mode: ApiMode;
};
