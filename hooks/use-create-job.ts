"use client";

import { useMutation } from "@tanstack/react-query";

import { createTryOnJob } from "@/lib/api";

export function useCreateJob() {
  return useMutation({ mutationFn: createTryOnJob });
}
