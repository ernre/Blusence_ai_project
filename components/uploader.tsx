"use client";

import Image from "next/image";
import { ImagePlus, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type UploadItem = {
  file: File;
  previewUrl: string;
};

type UploaderProps = {
  label: string;
  description: string;
  value: File[];
  onChange: (files: File[]) => void;
  multiple?: boolean;
  maxFiles?: number;
  error?: string;
};

const maxBytes = 8 * 1024 * 1024;

async function compressImage(file: File): Promise<File> {
  if (!file.type.startsWith("image/")) {
    throw new Error("Only image files are supported.");
  }
  if (file.size > maxBytes) {
    throw new Error("Image must be 8 MB or smaller.");
  }
  const bitmap = await createImageBitmap(file);
  const maxEdge = 1600;
  const scale = Math.min(1, maxEdge / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(bitmap.width * scale));
  canvas.height = Math.max(1, Math.round(bitmap.height * scale));
  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Unable to process image.");
  }
  context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (candidate) => (candidate ? resolve(candidate) : reject(new Error("Image compression failed."))),
      "image/jpeg",
      0.88,
    );
  });
  return new File([blob], file.name.replace(/\.[^.]+$/, ".jpg"), { type: "image/jpeg" });
}

export function Uploader({
  label,
  description,
  value,
  onChange,
  multiple = false,
  maxFiles = 1,
  error,
}: UploaderProps) {
  const [localError, setLocalError] = useState<string | null>(null);
  const [items, setItems] = useState<UploadItem[]>([]);

  useEffect(() => {
    const nextItems = value.map((file) => ({ file, previewUrl: URL.createObjectURL(file) }));
    setItems(nextItems);
    return () => nextItems.forEach((item) => URL.revokeObjectURL(item.previewUrl));
  }, [value]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setLocalError(null);
      try {
        const compressed = await Promise.all(acceptedFiles.slice(0, maxFiles).map(compressImage));
        onChange(multiple ? [...value, ...compressed].slice(0, maxFiles) : compressed.slice(0, 1));
      } catch (caught) {
        setLocalError(caught instanceof Error ? caught.message : "Unable to load image.");
      }
    },
    [maxFiles, multiple, onChange, value],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    multiple,
    maxFiles,
  });

  const message = localError ?? error;
  const helper = useMemo(() => `${description} ${multiple ? `Up to ${maxFiles} views.` : ""}`, [
    description,
    maxFiles,
    multiple,
  ]);

  return (
    <div className="grid gap-3">
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{helper}</p>
      </div>
      <div
        {...getRootProps()}
        className={cn(
          "flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed bg-secondary/30 p-4 text-center transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          isDragActive && "border-primary bg-primary/10",
        )}
      >
        <input {...getInputProps()} aria-label={label} />
        <ImagePlus className="mb-2 h-8 w-8 text-muted-foreground" aria-hidden="true" />
        <p className="text-sm font-medium">{isDragActive ? "Drop image here" : "Drag image here"}</p>
        <p className="mt-1 text-xs text-muted-foreground">or click to browse</p>
      </div>
      {items.length > 0 ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {items.map((item, index) => (
            <div key={`${item.file.name}-${index}`} className="relative overflow-hidden rounded-md border">
              <Image
                src={item.previewUrl}
                alt={`${label} preview ${index + 1}`}
                width={180}
                height={180}
                className="aspect-square w-full object-cover"
              />
              <Button
                aria-label={`Remove ${label} ${index + 1}`}
                type="button"
                variant="secondary"
                size="icon"
                className="absolute right-2 top-2 h-8 w-8"
                onClick={() => onChange(value.filter((_, fileIndex) => fileIndex !== index))}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      ) : null}
      {message ? <p className="text-sm text-destructive">{message}</p> : null}
    </div>
  );
}
