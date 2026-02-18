import apiClient from '../client';

export interface FormField {
  name: string;
  type: string;
  label: string;
  placeholder: string;
  required: boolean;
  order: number;
}

export interface ContactFormConfig {
  name: string;
  description: string;
  fields: FormField[];
  submit_button_text: string;
  success_message: string;
  welcome_message: string;
}

export interface ContactForm extends ContactFormConfig {
  id: string;
  workspace_id: string;
  is_active: boolean;
  public_url?: string;
}

export interface FormStats {
  total_submissions: number;
  recent_submissions: any[];
}

export const contactFormService = {
  async getContactForm(): Promise<ContactForm | null> {
    const response = await apiClient.get('/contact-forms');
    return response.data;
  },

  async createOrUpdateForm(config: ContactFormConfig): Promise<ContactForm> {
    const response = await apiClient.post('/contact-forms', config);
    return response.data;
  },

  async getFormStats(): Promise<FormStats> {
    const response = await apiClient.get('/contact-forms/stats');
    return response.data;
  },
};
