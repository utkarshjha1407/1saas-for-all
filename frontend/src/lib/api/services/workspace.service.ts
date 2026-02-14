/**
 * Workspace Service
 * Handles workspace management and onboarding
 */

import apiClient from '../client';
import { WorkspaceCreate, Workspace, OnboardingStatus } from '../types';

export const workspaceService = {
  /**
   * Create a new workspace
   */
  async create(data: WorkspaceCreate): Promise<Workspace> {
    const response = await apiClient.post<Workspace>('/workspaces', data);
    return response.data;
  },

  /**
   * Get workspace by ID
   */
  async getById(id: string): Promise<Workspace> {
    const response = await apiClient.get<Workspace>(`/workspaces/${id}`);
    return response.data;
  },

  /**
   * Update workspace
   */
  async update(id: string, data: Partial<WorkspaceCreate>): Promise<Workspace> {
    const response = await apiClient.patch<Workspace>(`/workspaces/${id}`, data);
    return response.data;
  },

  /**
   * Get onboarding status
   */
  async getOnboardingStatus(id: string): Promise<OnboardingStatus> {
    const response = await apiClient.get<OnboardingStatus>(`/workspaces/${id}/onboarding`);
    return response.data;
  },

  /**
   * Activate workspace
   */
  async activate(id: string): Promise<Workspace> {
    const response = await apiClient.post<Workspace>(`/workspaces/${id}/activate`);
    return response.data;
  },
};
