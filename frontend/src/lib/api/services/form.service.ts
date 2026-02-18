/**
 * Form Service
 * Handles form templates (file uploads) and submissions
 */

import apiClient from '../client';
import { FormTemplate, FormSubmission, FormTemplateCreate, FormSubmissionUpdate } from '../types';

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
  async getSubmissions(status?: string): Promise<FormSubmission[]> {
    const params = status ? { status } : {};
    const response = await apiClient.get<FormSubmission[]>('/forms/submissions', { params });
    return response.data;
  },

  async getSubmission(id: string): Promise<FormSubmission> {
    const response = await apiClient.get<FormSubmission>(`/forms/submissions/${id}`);
    return response.data;
  },

  async updateSubmission(id: string, data: FormSubmissionUpdate): Promise<FormSubmission> {
    const response = await apiClient.put<FormSubmission>(`/forms/submissions/${id}`, data);
    return response.data;
  },

  // Public endpoints
  async getPublicFormSubmission(submissionId: string): Promise<any> {
    const response = await apiClient.get(`/public/forms/view/${submissionId}`);
    return response.data;
  },

  async trackDownload(submissionId: string): Promise<void> {
    await apiClient.post(`/public/forms/track-download/${submissionId}`);
  },

  async markComplete(submissionId: string): Promise<void> {
    await apiClient.post(`/public/forms/mark-complete/${submissionId}`);
  },
};
