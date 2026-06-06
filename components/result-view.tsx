"use client";

import Link from "next/link";
import { Copy, Download, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";

import { JobProgress } from "@/components/job-progress";
import { MultiViewTabs } from "@/components/multi-view-tabs";
import { Button } from "@/components/ui/button";
import { useJobStatus } from "@/hooks/use-job-status";

type ResultViewProps = {
  jobId: string;
};

export function ResultView({ jobId }: ResultViewProps) {
  const { data, error, isLoading, isError } = useJobStatus(jobId);
  const [copied, setCopied] = useState(false);
  const firstImage = data?.images?.[0];
  const sourceImages = useMemo(() => data?.sourceImages ?? data?.images ?? [], [data]);

  if (isLoading) {
    return <JobProgress status="queued" />;
  }

  if (isError) {
    return (
      <div className="grid gap-4">
        <JobProgress status="error" error={error instanceof Error ? error.message : "Unable to load job."} />
        <Button asChild variant="outline">
          <Link href="/">
            <RotateCcw className="h-4 w-4" />
            Start over
          </Link>
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
        No job data was returned. Start a new try-on from the studio.
      </div>
    );
  }

  if (data.status !== "done") {
    return <JobProgress status={data.status} error={data.error} />;
  }

  if (!firstImage || !data.images) {
    return <JobProgress status="error" error="The job completed but did not return any images." />;
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
      <MultiViewTabs sourceImages={sourceImages} resultImages={data.images} />
      <aside className="grid content-start gap-4 rounded-lg border bg-card p-4">
        <JobProgress status="done" />
        <div className="rounded-md bg-secondary p-3 text-sm">
          <p className="text-muted-foreground">Latency</p>
          <p className="mt-1 text-lg font-semibold">{data.latencyMs ? `${data.latencyMs} ms` : "Not reported"}</p>
        </div>
        <Button asChild>
          <a href={firstImage} download={`vpe-${jobId}.png`}>
            <Download className="h-4 w-4" />
            Download
          </a>
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={async () => {
            await navigator.clipboard.writeText(window.location.href);
            setCopied(true);
          }}
        >
          <Copy className="h-4 w-4" />
          {copied ? "Copied" : "Copy link"}
        </Button>
        <Button asChild variant="ghost">
          <Link href="/">Run another try-on</Link>
        </Button>
      </aside>
    </div>
  );
}
