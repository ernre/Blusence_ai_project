import { describe, expect, it } from "vitest";

import {
  healthResponseSchema,
  jobsResponseSchema,
  providersResponseSchema,
  tryOnJobResultSchema,
} from "@/lib/schemas";

describe("schemas", () => {
  it("parses health responses", () => {
    expect(healthResponseSchema.parse({ ok: true })).toEqual({ ok: true });
  });

  it("rejects invalid job statuses", () => {
    expect(() =>
      jobsResponseSchema.parse({
        jobs: [
          {
            id: "1",
            status: "finished",
            thumbnail_url: "thumb.png",
            latency_ms: null,
            created_at: new Date().toISOString(),
          },
        ],
      }),
    ).toThrow();
  });

  it("parses nullable backend job fields", () => {
    expect(
      tryOnJobResultSchema.parse({
        status: "running",
        images: null,
        source_images: null,
        latency_ms: null,
        error: null,
      }),
    ).toEqual({
      status: "running",
      images: null,
      source_images: null,
      latency_ms: null,
      error: null,
    });
  });

  it("parses provider responses", () => {
    expect(
      providersResponseSchema.parse({
        active_provider: "idm_vton",
        providers: [
          {
            id: "idm_vton",
            label: "IDM-VTON research baseline",
            role: "open-source-research",
            status: "scaffolded",
            requires: ["CUDA GPU"],
            notes: "Research provider path.",
            active: true,
          },
        ],
      }),
    ).toEqual({
      active_provider: "idm_vton",
      providers: [
        {
          id: "idm_vton",
          label: "IDM-VTON research baseline",
          role: "open-source-research",
          status: "scaffolded",
          requires: ["CUDA GPU"],
          notes: "Research provider path.",
          active: true,
        },
      ],
    });
  });
});
