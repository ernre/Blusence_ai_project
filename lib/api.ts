import {
  createTryOnJobResponseSchema,
  healthResponseSchema,
  jobsResponseSchema,
  tryOnJobResultSchema,
} from "@/lib/schemas";
import type {
  ApiConfig,
  CreateTryOnJobInput,
  CreateTryOnJobResponse,
  HealthResponse,
  JobsResponse,
  TryOnJobResult,
} from "@/lib/types";
import { mockCreateJob, mockGetJob, mockGetJobs, mockHealth } from "@/lib/mock/job-store";

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
