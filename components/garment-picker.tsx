"use client";

import { RotateCw, Shirt } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useCatalogGarments } from "@/hooks/use-catalog-garments";
import type { CatalogGarment } from "@/lib/types";
import { cn } from "@/lib/utils";

type GarmentPickerProps = {
  selectedId: string | null;
  onPick: (file: File, garment: CatalogGarment) => void;
};

async function imageUrlToFile(imageUrl: string, name: string): Promise<File> {
  const response = await fetch(imageUrl);
  if (!response.ok) {
    throw new Error("Unable to load catalog image.");
  }
  const blob = await response.blob();
  const extension = blob.type.split("/")[1] || "jpg";
  return new File([blob], `${name}.${extension}`, { type: blob.type || "image/jpeg" });
}

export function GarmentPicker({ selectedId, onPick }: GarmentPickerProps) {
  const catalog = useCatalogGarments();

  if (catalog.isLoading) {
    return (
      <div className="grid gap-3">
        <p className="text-sm font-medium">Catalog</p>
        <div className="flex items-center gap-2 rounded-md border bg-secondary/40 p-3 text-sm text-muted-foreground">
          <RotateCw className="h-4 w-4 animate-spin" aria-hidden="true" />
          Loading real garments...
        </div>
      </div>
    );
  }

  if (catalog.isError) {
    return (
      <div className="grid gap-3">
        <p className="text-sm font-medium">Catalog</p>
        <div className="grid gap-3 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          <p>{catalog.error instanceof Error ? catalog.error.message : "Unable to load catalog garments."}</p>
          <Button type="button" variant="outline" onClick={() => void catalog.refetch()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const garments = catalog.data?.garments ?? [];

  return (
    <div className="grid gap-3">
      <div>
        <p className="text-sm font-medium">Catalog</p>
        <p className="text-xs text-muted-foreground">Real product images imported from your catalog manifest.</p>
      </div>
      {garments.length === 0 ? (
        <div className="grid gap-2 rounded-md border bg-secondary/30 p-3 text-sm text-muted-foreground">
          <Shirt className="h-5 w-5" aria-hidden="true" />
          <p>No catalog garments imported yet.</p>
          <p className="text-xs">Add real image files under data/catalog/images and rows in data/catalog/garments.csv.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
        {garments.map((garment) => (
          <Button
            key={garment.id}
            type="button"
            variant="outline"
            className={cn(
              "h-auto flex-col items-stretch gap-2 p-2",
              selectedId === garment.id && "border-primary ring-2 ring-ring",
            )}
            onClick={async () => onPick(await imageUrlToFile(garment.imageUrl, garment.id), garment)}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={garment.imageUrl}
              alt={garment.name}
              className="aspect-[4/5] w-full rounded object-cover"
            />
            <span className="grid gap-0.5 text-left text-xs">
              <span className="font-medium">{garment.name}</span>
              <span className="text-muted-foreground">{garment.brand ?? garment.category}</span>
            </span>
          </Button>
        ))}
        </div>
      )}
    </div>
  );
}
