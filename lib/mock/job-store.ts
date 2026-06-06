import type {
  CreateTryOnJobInput,
  CreateTryOnJobResponse,
  HealthResponse,
  JobsResponse,
  ProvidersResponse,
  TryOnJobResult,
  TryOnJobSummary,
} from "@/lib/types";
import { sampleResultImages } from "@/lib/mock/sample-images";

type MockJob = {
  id: string;
  status: "queued" | "running" | "done" | "error";
  createdAt: string;
  sourceImages: string[];
  resultImages: string[];
  latencyMs: number | null;
  error?: string;
};

const jobs = new Map<string, MockJob>();

function makeId() {
  return `mock_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => {
      if (typeof reader.result === "string") {
        resolve(reader.result);
      } else {
        reject(new Error("Unable to read image preview"));
      }
    });
    reader.addEventListener("error", () => reject(new Error("Unable to read image preview")));
    reader.readAsDataURL(file);
  });
}

export async function mockCreateJob(input: CreateTryOnJobInput): Promise<CreateTryOnJobResponse> {
  const id = makeId();
  const sourceImages = await Promise.all(input.person.map((file) => fileToDataUrl(file)));
  const selectedResults = sourceImages.length > 1 ? [...sampleResultImages] : [sampleResultImages[0]];
  jobs.set(id, {
    id,
    status: "queued",
    createdAt: new Date().toISOString(),
    sourceImages,
    resultImages: selectedResults,
    latencyMs: null,
  });
  window.setTimeout(() => {
    const job = jobs.get(id);
    if (job) {
      jobs.set(id, { ...job, status: "running" });
    }
  }, 900);
  window.setTimeout(() => {
    const job = jobs.get(id);
    if (job) {
      jobs.set(id, { ...job, status: "done", latencyMs: 2400 + (input.steps ?? 6) * 120 });
    }
  }, 2600);
  return { jobId: id };
}

export async function mockGetJob(jobId: string): Promise<TryOnJobResult> {
  const job = jobs.get(jobId);
  if (!job) {
    return { status: "error", error: "Mock job not found. Start a new try-on from the studio." };
  }
  return {
    status: job.status,
    images: job.status === "done" ? job.resultImages : undefined,
    sourceImages: job.sourceImages,
    latencyMs: job.latencyMs ?? undefined,
    error: job.error,
  };
}

export async function mockGetJobs(): Promise<JobsResponse> {
  const summaries: TryOnJobSummary[] = Array.from(jobs.values())
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .map((job) => ({
      id: job.id,
      status: job.status,
      thumbnailUrl: job.resultImages[0],
      latencyMs: job.latencyMs,
      createdAt: job.createdAt,
    }));
  return { jobs: summaries };
}

export async function mockHealth(): Promise<HealthResponse> {
  return { ok: true };
}

export async function mockGetProviders(): Promise<ProvidersResponse> {
  return {
    activeProvider: "local",
    providers: [
      {
        id: "local",
        label: "Local preview compositor",
        role: "product-preview",
        status: "available",
        requires: [],
        notes: "Offline renderer for product flow validation.",
        active: true,
      },
      {
        id: "fashn",
        label: "FASHN.ai benchmark",
        role: "external-benchmark",
        status: "requires-api-key",
        requires: ["FASHN_API_KEY"],
        notes: "External baseline for launch acceleration and side-by-side quality comparison.",
        active: false,
      },
      {
        id: "idm_vton",
        label: "IDM-VTON research baseline",
        role: "open-source-research",
        status: "scaffolded",
        requires: ["IDM_VTON_REPO_PATH", "IDM_VTON_MODEL_DIR", "CUDA GPU"],
        notes: "Research provider path kept separate from proprietary VPE ownership.",
        active: false,
      },
    ],
  };
}
