/**
 * Form Service
 * Handles form templates and submissions
 */

import apiClient from '../client';
import { FormTemplate, FormSubmission, FormTemplateCreate, FormSubmissionCreate } from '../types';

export const formService = {
  // Templates
  async getTemplates(): Promise<FormTemplate[]> {
    const response = await apiClient.get<FormTemplate[]>('/forms/templates');
    return response.data;
  },

  async getTemplate(id: string): Promise<FormTemplate> {
    const response = await apiClient.get<FormTemplate>(`/forms/templates/${id}`);
    return response.data;
  },

  async createTemplate(data: FormTemplateCreate): Promise<FormTemplate> {
    const response = await apiClient.post<FormTemplate>('/forms/templates', data);
    return response.data;
  },

  async updateTemplate(id: string, data: Partial<FormTemplateCreate>): Promise<FormTemplate> {
    const response = await apiClient.put<FormTemplate>(`/forms/templates/${id}`, data);
    return response.data;
  },

  async deleteTemplate(id: string): Promise<void> {
    await apiClient.delete(`/forms/templates/${id}`);
  },

  // Submissions
  async getSubmissions(): Promise<FormSubmission[]> {
    const response = await apiClient.get<FormSubmission[]>('/forms/submissions');
    return response.data;
  },

  async getSubmission(id: string): Promise<FormSubmission> {
    const response = await apiClient.get<FormSubmission>(`/forms/submissions/${id}`);
    return response.data;
  },

  async createSubmission(data: FormSubmissionCreate): Promise<FormSubmission> {
    const response = await apiClient.post<FormSubmission>('/forms/submissions', data);
    return response.data;
  },

  async updateSubmissionStatus(id: string, status: FormSubmission['status']): Promise<FormSubmission> {
    const response = await apiClient.patch<FormSubmission>(`/forms/submissions/${id}/status`, { status });
    return response.data;
  },
};
