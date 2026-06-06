"use client";

import Image from "next/image";
import Link from "next/link";

import type { TryOnJobSummary } from "@/lib/types";

type ResultCardProps = {
  job: TryOnJobSummary;
};

export function ResultCard({ job }: ResultCardProps) {
  return (
    <Link
      href={`/results/${job.id}`}
      className="group overflow-hidden rounded-lg border bg-card transition hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <Image
        src={job.thumbnailUrl}
        alt={`Try-on job ${job.id}`}
        width={360}
        height={450}
        className="aspect-[4/5] w-full object-cover"
      />
      <div className="grid gap-1 p-3 text-sm">
        <div className="flex items-center justify-between gap-3">
          <span className="truncate font-medium">{job.id}</span>
          <span className="rounded bg-secondary px-2 py-1 text-xs capitalize">{job.status}</span>
        </div>
        <p className="text-xs text-muted-foreground">
          {job.latencyMs ? `${job.latencyMs} ms` : "Latency pending"} ·{" "}
          {new Date(job.createdAt).toLocaleString()}
        </p>
      </div>
    </Link>
  );
}
