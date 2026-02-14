/**
 * Contact Service
 * Handles contact management
 */

import apiClient from '../client';
import { ContactCreate, Contact } from '../types';

export const contactService = {
  /**
   * Create a new contact (public endpoint)
   */
  async create(data: ContactCreate, workspaceId: string): Promise<Contact> {
    const response = await apiClient.post<Contact>(`/contacts?workspace_id=${workspaceId}`, data);
    return response.data;
  },

  /**
   * Get all contacts
   */
  async getAll(): Promise<Contact[]> {
    const response = await apiClient.get<Contact[]>('/contacts');
    return response.data;
  },

  /**
   * Get contact by ID
   */
  async getById(id: string): Promise<Contact> {
    const response = await apiClient.get<Contact>(`/contacts/${id}`);
    return response.data;
  },

  /**
   * Update contact
   */
  async update(id: string, data: Partial<ContactCreate>): Promise<Contact> {
    const response = await apiClient.patch<Contact>(`/contacts/${id}`, data);
    return response.data;
  },
};
