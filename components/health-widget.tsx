"use client";

import { Activity, Server } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiConfig, getHealth } from "@/lib/api";

export function HealthWidget() {
  const health = useQuery({ queryKey: ["healthz"], queryFn: getHealth });

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Server className="h-4 w-4 text-primary" aria-hidden="true" />
          Mode
        </div>
        <p className="mt-3 text-2xl font-semibold uppercase">{apiConfig.mode}</p>
        <p className="mt-1 break-all text-sm text-muted-foreground">{apiConfig.baseUrl}</p>
      </div>
      <div className="rounded-lg border bg-card p-4 lg:col-span-2">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Activity className="h-4 w-4 text-primary" aria-hidden="true" />
          Backend reachability
        </div>
        {health.isLoading ? (
          <p className="mt-3 text-sm text-muted-foreground">Checking /healthz...</p>
        ) : health.isError ? (
          <div className="mt-3 grid gap-3">
            <p className="text-sm text-destructive">
              {health.error instanceof Error ? health.error.message : "Health check failed."}
            </p>
            <Button type="button" variant="outline" onClick={() => void health.refetch()}>
              Retry
            </Button>
          </div>
        ) : (
          <p className="mt-3 text-sm">{health.data?.ok ? "Reachable and ready." : "Health check returned not ready."}</p>
        )}
      </div>
    </div>
  );
}
