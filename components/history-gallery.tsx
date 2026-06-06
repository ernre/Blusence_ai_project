"use client";

import Link from "next/link";
import { History, RotateCcw } from "lucide-react";

import { ResultCard } from "@/components/result-card";
import { Button } from "@/components/ui/button";
import { useJobs } from "@/hooks/use-jobs";

export function HistoryGallery() {
  const { data, isLoading, isError, error } = useJobs();

  if (isLoading) {
    return (
      <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground" aria-live="polite">
        Loading recent jobs...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="grid gap-4 rounded-lg border border-destructive/40 bg-destructive/10 p-6">
        <p className="text-sm font-medium text-destructive">
          {error instanceof Error ? error.message : "Unable to load job history."}
        </p>
        <Button asChild variant="outline">
          <Link href="/">
            <RotateCcw className="h-4 w-4" />
            Start a new try-on
          </Link>
        </Button>
      </div>
    );
  }

  if (!data || data.jobs.length === 0) {
    return (
      <div className="grid justify-items-start gap-4 rounded-lg border bg-card p-6">
        <History className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
        <div>
          <p className="font-medium">No try-on jobs yet</p>
          <p className="mt-1 text-sm text-muted-foreground">Completed mock jobs will appear here during this session.</p>
        </div>
        <Button asChild>
          <Link href="/">Open Studio</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {data.jobs.map((job) => (
        <ResultCard key={job.id} job={job} />
      ))}
    </div>
  );
}
