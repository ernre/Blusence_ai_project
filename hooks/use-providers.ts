"use client";

import { useQuery } from "@tanstack/react-query";

import { getProviders } from "@/lib/api";

export function useProviders() {
  return useQuery({ queryKey: ["tryon-providers"], queryFn: getProviders });
}
