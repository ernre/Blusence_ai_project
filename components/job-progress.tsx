"use client";

import { CheckCircle2, CircleDashed, Loader2, TriangleAlert } from "lucide-react";

import type { JobStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

type JobProgressProps = {
  status: JobStatus;
  error?: string;
};

const steps: JobStatus[] = ["queued", "running", "done"];

export function JobProgress({ status, error }: JobProgressProps) {
  if (status === "error") {
    return (
      <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
        <div className="flex items-center gap-2 font-medium">
          <TriangleAlert className="h-4 w-4" aria-hidden="true" />
          Try-on failed
        </div>
        <p className="mt-2">{error ?? "The job ended with an error. Please try another image."}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4" aria-live="polite">
      <div className="flex items-center gap-2 text-sm font-medium">
        {status === "done" ? (
          <CheckCircle2 className="h-4 w-4 text-primary" aria-hidden="true" />
        ) : (
          <Loader2 className="h-4 w-4 animate-spin text-primary" aria-hidden="true" />
        )}
        {status === "done" ? "Result ready" : status === "running" ? "Rendering try-on" : "Queued"}
      </div>
      <div className="mt-4 grid grid-cols-3 gap-2">
        {steps.map((step) => {
          const activeIndex = steps.indexOf(status === "error" ? "queued" : status);
          const stepIndex = steps.indexOf(step);
          const complete = stepIndex <= activeIndex;
          return (
            <div key={step} className="flex items-center gap-2 text-xs">
              <CircleDashed
                className={cn("h-4 w-4", complete ? "text-primary" : "text-muted-foreground")}
                aria-hidden="true"
              />
              <span className={cn(complete ? "text-foreground" : "text-muted-foreground")}>{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
