"use client";

import { Activity, Cpu, Server } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiConfig, getHealth } from "@/lib/api";
import { useProviders } from "@/hooks/use-providers";

export function HealthWidget() {
  const health = useQuery({ queryKey: ["healthz"], queryFn: getHealth });
  const providers = useProviders();
  const activeProvider = providers.data?.providers.find((provider) => provider.active);

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
      <div className="rounded-lg border bg-card p-4 lg:col-span-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Cpu className="h-4 w-4 text-primary" aria-hidden="true" />
          Try-on provider
        </div>
        {providers.isLoading ? (
          <p className="mt-3 text-sm text-muted-foreground">Checking /v1/providers...</p>
        ) : providers.isError ? (
          <div className="mt-3 grid gap-3">
            <p className="text-sm text-destructive">
              {providers.error instanceof Error ? providers.error.message : "Provider check failed."}
            </p>
            <Button type="button" variant="outline" onClick={() => void providers.refetch()}>
              Retry
            </Button>
          </div>
        ) : (
          <div className="mt-3 grid gap-3">
            <div>
              <p className="text-xl font-semibold">{activeProvider?.label ?? providers.data?.activeProvider}</p>
              <p className="text-sm text-muted-foreground">{activeProvider?.role}</p>
            </div>
            <div className="grid gap-2 md:grid-cols-3">
              {providers.data?.providers.map((provider) => (
                <div
                  key={provider.id}
                  className="rounded-md border p-3 data-[active=true]:border-primary"
                  data-active={provider.active}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium">{provider.label}</p>
                    <span className="rounded-sm bg-muted px-2 py-1 text-xs text-muted-foreground">
                      {provider.status}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-muted-foreground">{provider.notes}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
