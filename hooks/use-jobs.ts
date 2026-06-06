"use client";

import { useQuery } from "@tanstack/react-query";

import { getJobs } from "@/lib/api";

export function useJobs() {
  return useQuery({ queryKey: ["tryon-jobs"], queryFn: getJobs });
}
