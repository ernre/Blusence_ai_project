"use client";

import { useQuery } from "@tanstack/react-query";

import { getTryOnJob } from "@/lib/api";

export function useJobStatus(jobId: string) {
  return useQuery({
    queryKey: ["tryon-job", jobId],
    queryFn: () => getTryOnJob(jobId),
    refetchInterval: ({ state }) => {
      const status = state.data?.status;
      if (status === "done" || status === "error") {
        return false;
      }
      const failures = state.failureCount;
      return Math.min(5000, 700 * 2 ** failures);
    },
  });
}
