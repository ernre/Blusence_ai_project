"use client";

import Image from "next/image";

import { Button } from "@/components/ui/button";
import { sampleGarments } from "@/lib/mock/sample-images";
import { cn } from "@/lib/utils";

type GarmentPickerProps = {
  selectedId: string | null;
  onPick: (file: File, id: string) => void;
};

async function dataUrlToFile(dataUrl: string, name: string): Promise<File> {
  const response = await fetch(dataUrl);
  const blob = await response.blob();
  return new File([blob], `${name}.svg`, { type: "image/svg+xml" });
}

export function GarmentPicker({ selectedId, onPick }: GarmentPickerProps) {
  return (
    <div className="grid gap-3">
      <div>
        <p className="text-sm font-medium">Pick a sample garment</p>
        <p className="text-xs text-muted-foreground">Useful for mock demos when you do not have a file.</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {sampleGarments.map((garment) => (
          <Button
            key={garment.id}
            type="button"
            variant="outline"
            className={cn(
              "h-auto flex-col items-stretch gap-2 p-2",
              selectedId === garment.id && "border-primary ring-2 ring-ring",
            )}
            onClick={async () => onPick(await dataUrlToFile(garment.imageUrl, garment.id), garment.id)}
          >
            <Image
              src={garment.imageUrl}
              alt={garment.name}
              width={200}
              height={260}
              className="aspect-[4/5] w-full rounded object-cover"
            />
            <span className="text-left text-xs font-medium">{garment.name}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
