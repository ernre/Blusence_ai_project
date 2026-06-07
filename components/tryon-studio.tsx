"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronDown, Cpu, Loader2, Wand2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";

import { GarmentPicker } from "@/components/garment-picker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Uploader } from "@/components/uploader";
import { useCreateJob } from "@/hooks/use-create-job";
import { useProviders } from "@/hooks/use-providers";
import { tryOnFormSchema, type TryOnFormValues } from "@/lib/schemas";
import type { GarmentCategory } from "@/lib/types";

const categories: { value: GarmentCategory; label: string }[] = [
  { value: "tops", label: "Tops" },
  { value: "bottoms", label: "Bottoms" },
  { value: "outerwear", label: "Outerwear" },
  { value: "dress", label: "Dress" },
  { value: "shoes", label: "Shoes" },
  { value: "accessory", label: "Accessory" },
];

export function TryOnStudio() {
  const router = useRouter();
  const createJob = useCreateJob();
  const providers = useProviders();
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [pickedGarmentId, setPickedGarmentId] = useState<string | null>(null);
  const activeProvider = providers.data?.providers.find((provider) => provider.active);
  const form = useForm<TryOnFormValues>({
    resolver: zodResolver(tryOnFormSchema),
    defaultValues: {
      person: [],
      category: "outerwear",
      brandId: "",
      steps: 6,
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    const response = await createJob.mutateAsync(values);
    router.push(`/results/${response.jobId}`);
  });

  return (
    <form className="grid gap-6 lg:grid-cols-[1fr_360px]" onSubmit={onSubmit}>
      <div className="grid gap-5">
        <Controller
          name="person"
          control={form.control}
          render={({ field, fieldState }) => (
            <Uploader
              label="Person photos"
              description="Add a primary photo and optional extra views."
              value={field.value}
              onChange={field.onChange}
              multiple
              maxFiles={4}
              error={fieldState.error?.message}
            />
          )}
        />
        <Controller
          name="garment"
          control={form.control}
          render={({ field, fieldState }) => (
            <Uploader
              label="Garment image"
              description="Upload a product image with the garment visible."
              value={field.value ? [field.value] : []}
              onChange={(files) => {
                setPickedGarmentId(null);
                field.onChange(files[0]);
              }}
              error={fieldState.error?.message}
            />
          )}
        />
      </div>
      <aside className="grid content-start gap-5">
        <div className="grid gap-2 rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Cpu className="h-4 w-4 text-primary" aria-hidden="true" />
            Provider
          </div>
          <p className="text-sm">{activeProvider?.label ?? providers.data?.activeProvider ?? "Checking provider..."}</p>
          <p className="text-xs text-muted-foreground">
            {activeProvider?.id === "local"
              ? "Preview only"
              : activeProvider?.id === "idm_vton"
                ? "Hosted model"
                : activeProvider?.status ?? ""}
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <GarmentPicker
            selectedId={pickedGarmentId}
            onPick={(file, garment) => {
              setPickedGarmentId(garment.id);
              form.setValue("garment", file, { shouldValidate: true });
              form.setValue("category", garment.category, { shouldValidate: true });
              if (garment.brand) {
                form.setValue("brandId", garment.brand, { shouldValidate: true });
              }
            }}
          />
        </div>
        <div className="grid gap-4 rounded-lg border bg-card p-4">
          <div className="grid gap-2">
            <Label htmlFor="category">Category</Label>
            <Controller
              name="category"
              control={form.control}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Choose category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="brandId">Brand</Label>
            <Input id="brandId" placeholder="Optional brand id" {...form.register("brandId")} />
          </div>
          <Button
            type="button"
            variant="ghost"
            className="justify-between px-0"
            onClick={() => setAdvancedOpen((open) => !open)}
            aria-expanded={advancedOpen}
          >
            Advanced
            <ChevronDown className="h-4 w-4" aria-hidden="true" />
          </Button>
          {advancedOpen ? (
            <Controller
              name="steps"
              control={form.control}
              render={({ field }) => (
                <div className="grid gap-3">
                  <div className="flex items-center justify-between text-sm">
                    <Label>Sampling steps</Label>
                    <span className="font-medium">{field.value}</span>
                  </div>
                  <Slider
                    min={4}
                    max={8}
                    step={1}
                    value={[field.value ?? 6]}
                    onValueChange={(value) => field.onChange(value[0])}
                    aria-label="Sampling steps"
                  />
                </div>
              )}
            />
          ) : null}
          {createJob.error ? (
            <p className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {createJob.error instanceof Error ? createJob.error.message : "Unable to start try-on."}
            </p>
          ) : null}
          <Button type="submit" disabled={createJob.isPending}>
            {createJob.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
            Run try-on
          </Button>
        </div>
      </aside>
    </form>
  );
}
