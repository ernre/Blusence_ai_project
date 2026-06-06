"use client";

import { useQuery } from "@tanstack/react-query";

import { getTryOnJob } from "@/lib/api";

export function useJobStatus(jobId: string) {
  return useQuery({
    queryKey: ["tryon-job", jobId],
    queryFn: () => getTryOnJob(jobId),
    refetchInterval: (query) => {
      const { state } = query;
      const status = state.data?.status;
      if (status === "done" || status === "error") {
        return false;
      }
      const polls = Math.max(0, state.dataUpdateCount - 1);
      return Math.min(5000, 700 * 2 ** polls);
    },
  });
}
