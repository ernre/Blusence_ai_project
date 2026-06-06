import { describe, expect, it } from "vitest";

import { healthResponseSchema, jobsResponseSchema } from "@/lib/schemas";

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
});
