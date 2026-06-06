"use client";

import Image from "next/image";
import { useState } from "react";

import { Slider } from "@/components/ui/slider";

type BeforeAfterSliderProps = {
  beforeImage: string;
  afterImage: string;
  label: string;
};

export function BeforeAfterSlider({ beforeImage, afterImage, label }: BeforeAfterSliderProps) {
  const [position, setPosition] = useState(50);

  return (
    <div className="grid gap-3">
      <div className="relative aspect-[4/5] overflow-hidden rounded-lg border bg-secondary">
        <Image
          src={beforeImage}
          alt={`${label} before`}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, 720px"
        />
        <div className="absolute inset-y-0 left-0 overflow-hidden" style={{ width: `${position}%` }}>
          <Image src={afterImage} alt={`${label} after`} fill className="object-cover" sizes="(max-width: 768px) 100vw, 720px" />
        </div>
        <div className="absolute inset-y-0 w-0.5 bg-background shadow" style={{ left: `${position}%` }} />
        <div className="absolute left-3 top-3 rounded bg-background/90 px-2 py-1 text-xs font-medium">After</div>
        <div className="absolute right-3 top-3 rounded bg-background/90 px-2 py-1 text-xs font-medium">Before</div>
      </div>
      <Slider
        min={0}
        max={100}
        step={1}
        value={[position]}
        onValueChange={(value) => setPosition(value[0] ?? 50)}
        aria-label={`Compare ${label}`}
      />
    </div>
  );
}
