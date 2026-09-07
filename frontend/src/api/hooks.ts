import { useMutation, useQuery } from '@tanstack/react-query';
import { fetchHealth, inspectFoodItem } from './client';
import type { HealthResponse, InspectionResponse, InspectRequestOptions } from './types';

/**
 * Poll service health status every 5 seconds.
 */
export function useHealthQuery() {
  return useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 5000,
    retry: 2,
    staleTime: 4000,
  });
}

/**
 * Mutation hook for executing food defect inspection.
 */
export function useInspectMutation() {
  return useMutation<InspectionResponse, Error, InspectRequestOptions>({
    mutationFn: inspectFoodItem,
  });
}
