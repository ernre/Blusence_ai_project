"use client";

import { useQuery } from "@tanstack/react-query";

import { getCatalogGarments } from "@/lib/api";

export function useCatalogGarments() {
  return useQuery({ queryKey: ["catalog-garments"], queryFn: getCatalogGarments });
}
