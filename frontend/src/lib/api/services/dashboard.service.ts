/**
 * Dashboard Service
 * Handles dashboard statistics and analytics
 */

import apiClient from '../client';
import { DashboardStats } from '../types';

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },
};
