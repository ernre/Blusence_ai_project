import {
  catalogResponseSchema,
  createTryOnJobResponseSchema,
  healthResponseSchema,
  jobsResponseSchema,
  providersResponseSchema,
  tryOnJobResultSchema,
} from "@/lib/schemas";
import type {
  ApiConfig,
  CatalogResponse,
  CreateTryOnJobInput,
  CreateTryOnJobResponse,
  HealthResponse,
  JobsResponse,
  ProvidersResponse,
  TryOnJobResult,
} from "@/lib/types";
import {
  mockCreateJob,
  mockGetJob,
  mockGetJobs,
  mockGetProviders,
  mockHealth,
} from "@/lib/mock/job-store";

const defaultBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const useMock = process.env.NEXT_PUBLIC_USE_MOCK !== "false";

export const apiConfig: ApiConfig = {
  baseUrl: defaultBaseUrl,
  mode: useMock ? "mock" : "live",
};

function normalizeBaseUrl(baseUrl: string) {
  return baseUrl.replace(/\/$/, "");
}

function toJobIdResponse(payload: { job_id: string }): CreateTryOnJobResponse {
  return { jobId: payload.job_id };
}

function toJobResult(payload: {
  status: TryOnJobResult["status"];
  images?: string[];
  source_images?: string[];
  latency_ms?: number;
  error?: string;
}): TryOnJobResult {
  return {
    status: payload.status,
    images: payload.images,
    sourceImages: payload.source_images,
    latencyMs: payload.latency_ms,
    error: payload.error,
  };
}

function toJobsResponse(payload: {
  jobs: {
    id: string;
    status: TryOnJobResult["status"];
    thumbnail_url: string;
    latency_ms: number | null;
    created_at: string;
  }[];
}): JobsResponse {
  return {
    jobs: payload.jobs.map((job) => ({
      id: job.id,
      status: job.status,
      thumbnailUrl: job.thumbnail_url,
      latencyMs: job.latency_ms,
      createdAt: job.created_at,
    })),
  };
}

function toCatalogResponse(payload: {
  garments: {
    id: string;
    name: string;
    brand: string | null;
    category: CatalogResponse["garments"][number]["category"];
    image_url: string;
    source_url: string | null;
    license: string | null;
  }[];
}): CatalogResponse {
  return {
    garments: payload.garments.map((garment) => ({
      id: garment.id,
      name: garment.name,
      brand: garment.brand,
      category: garment.category,
      imageUrl: garment.image_url,
      sourceUrl: garment.source_url,
      license: garment.license,
    })),
  };
}

function toProvidersResponse(payload: {
  active_provider: string;
  providers: {
    id: string;
    label: string;
    role: string;
    status: string;
    requires: string[];
    notes: string;
    active: boolean;
  }[];
}): ProvidersResponse {
  return {
    activeProvider: payload.active_provider,
    providers: payload.providers.map((provider) => ({
      id: provider.id,
      label: provider.label,
      role: provider.role,
      status: provider.status,
      requires: provider.requires,
      notes: provider.notes,
      active: provider.active,
    })),
  };
}

async function assertOk(response: Response) {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
}

export async function createTryOnJob(input: CreateTryOnJobInput): Promise<CreateTryOnJobResponse> {
  if (apiConfig.mode === "mock") {
    return mockCreateJob(input);
  }
  const form = new FormData();
  input.person.forEach((file) => form.append("person", file));
  form.append("garment", input.garment);
  form.append("category", input.category);
  if (input.brandId) {
    form.append("brand_id", input.brandId);
  }
  if (input.steps) {
    form.append("steps", String(input.steps));
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/v1/tryon`, {
    method: "POST",
    body: form,
  });
  await assertOk(response);
  const payload = createTryOnJobResponseSchema.parse(await response.json());
  return toJobIdResponse(payload);
}

export async function getTryOnJob(jobId: string): Promise<TryOnJobResult> {
  if (apiConfig.mode === "mock") {
    return mockGetJob(jobId);
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/v1/tryon/${jobId}`);
  await assertOk(response);
  const payload = tryOnJobResultSchema.parse(await response.json());
  return toJobResult(payload);
}

export async function getJobs(): Promise<JobsResponse> {
  if (apiConfig.mode === "mock") {
    return mockGetJobs();
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/v1/jobs`);
  await assertOk(response);
  const payload = jobsResponseSchema.parse(await response.json());
  return toJobsResponse(payload);
}

export async function getHealth(): Promise<HealthResponse> {
  if (apiConfig.mode === "mock") {
    return mockHealth();
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/healthz`);
  await assertOk(response);
  return healthResponseSchema.parse(await response.json());
}

export async function getProviders(): Promise<ProvidersResponse> {
  if (apiConfig.mode === "mock") {
    return mockGetProviders();
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/v1/providers`);
  await assertOk(response);
  const payload = providersResponseSchema.parse(await response.json());
  return toProvidersResponse(payload);
}

export async function getCatalogGarments(): Promise<CatalogResponse> {
  if (apiConfig.mode === "mock") {
    return { garments: [] };
  }
  const response = await fetch(`${normalizeBaseUrl(apiConfig.baseUrl)}/v1/catalog/garments`);
  await assertOk(response);
  const payload = catalogResponseSchema.parse(await response.json());
  return toCatalogResponse(payload);
}
