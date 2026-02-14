/**
 * Dashboard Hook
 * Manages dashboard data and statistics
 */

import { useQuery } from '@tanstack/react-query';
import { dashboardService, DashboardStats } from '@/lib/api';

export const useDashboard = () => {
  const { data, isLoading, error, refetch } = useQuery<DashboardStats>({
    queryKey: ['dashboardStats'],
    queryFn: () => dashboardService.getStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  return {
    stats: data,
    isLoading,
    error,
    refetch,
  };
};
