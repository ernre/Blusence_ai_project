import { z } from "zod";

const fileSchema =
  typeof File === "undefined"
    ? z.custom<File>((value) => value instanceof Blob, "Expected an image file")
    : z.instanceof(File);

export const jobStatusSchema = z.enum(["queued", "running", "done", "error"]);

export const garmentCategorySchema = z.enum([
  "tops",
  "bottoms",
  "outerwear",
  "dress",
  "shoes",
  "accessory",
]);

export const createTryOnJobResponseSchema = z.object({
  job_id: z.string().min(1),
});

export const tryOnJobResultSchema = z.object({
  status: jobStatusSchema,
  images: z.array(z.string().min(1)).nullable().optional(),
  source_images: z.array(z.string().min(1)).nullable().optional(),
  latency_ms: z.number().int().nonnegative().nullable().optional(),
  error: z.string().nullable().optional(),
});

export const jobsResponseSchema = z.object({
  jobs: z.array(
    z.object({
      id: z.string().min(1),
      status: jobStatusSchema,
      thumbnail_url: z.string().min(1),
      latency_ms: z.number().int().nonnegative().nullable(),
      created_at: z.string().min(1),
    }),
  ),
});

export const healthResponseSchema = z.object({
  ok: z.boolean(),
});

export const providersResponseSchema = z.object({
  active_provider: z.string().min(1),
  providers: z.array(
    z.object({
      id: z.string().min(1),
      label: z.string().min(1),
      role: z.string().min(1),
      status: z.string().min(1),
      requires: z.array(z.string()),
      notes: z.string(),
      active: z.boolean(),
    }),
  ),
});

export const catalogResponseSchema = z.object({
  garments: z.array(
    z.object({
      id: z.string().min(1),
      name: z.string().min(1),
      brand: z.string().nullable(),
      category: garmentCategorySchema,
      image_url: z.string().min(1),
      source_url: z.string().nullable(),
      license: z.string().nullable(),
    }),
  ),
});

export const tryOnFormSchema = z.object({
  person: z.array(fileSchema).min(1).max(4),
  garment: fileSchema,
  category: garmentCategorySchema,
  brandId: z.string().trim().optional(),
  steps: z.number().int().min(4).max(8).optional(),
});

export type TryOnFormValues = z.infer<typeof tryOnFormSchema>;
