import apiClient from '../client';

export interface IntegrationVerifyRequest {
  provider: 'resend' | 'sendgrid' | 'twilio';
  config: Record<string, any>;
}

export interface IntegrationCreateRequest {
  provider: 'resend' | 'sendgrid' | 'twilio';
  config: Record<string, any>;
}

export interface IntegrationVerifyResponse {
  success: boolean;
  message: string;
  error?: string;
}

export interface Integration {
  id: string;
  workspace_id: string;
  provider: string;
  config: Record<string, any>;
  status: string;
  created_at: string;
}

export interface IntegrationsResponse {
  email: Integration | null;
  sms: Integration | null;
  has_email: boolean;
  has_sms: boolean;
  has_any: boolean;
}

export const integrationService = {
  async verifyIntegration(request: IntegrationVerifyRequest): Promise<IntegrationVerifyResponse> {
    const response = await apiClient.post('/integrations/verify', request);
    return response.data;
  },

  async createIntegration(request: IntegrationCreateRequest): Promise<Integration> {
    const response = await apiClient.post('/integrations', request);
    return response.data;
  },

  async getIntegrations(): Promise<IntegrationsResponse> {
    const response = await apiClient.get('/integrations');
    return response.data;
  },

  async deleteIntegration(integrationId: string): Promise<{ success: boolean }> {
    const response = await apiClient.delete(`/integrations/${integrationId}`);
    return response.data;
  },
};
