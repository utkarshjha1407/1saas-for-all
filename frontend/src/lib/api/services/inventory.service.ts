/**
 * Inventory Service
 * Handles inventory items and usage tracking
 */

import apiClient from '../client';
import { InventoryItem, InventoryItemCreate, InventoryUsage } from '../types';

export const inventoryService = {
  // Items
  async getAll(): Promise<InventoryItem[]> {
    const response = await apiClient.get<InventoryItem[]>('/inventory');
    return response.data;
  },

  async getById(id: string): Promise<InventoryItem> {
    const response = await apiClient.get<InventoryItem>(`/inventory/${id}`);
    return response.data;
  },

  async create(data: InventoryItemCreate): Promise<InventoryItem> {
    const response = await apiClient.post<InventoryItem>('/inventory', data);
    return response.data;
  },

  async update(id: string, data: Partial<InventoryItemCreate>): Promise<InventoryItem> {
    const response = await apiClient.put<InventoryItem>(`/inventory/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/inventory/${id}`);
  },

  async updateQuantity(id: string, quantity: number): Promise<InventoryItem> {
    const response = await apiClient.patch<InventoryItem>(`/inventory/${id}/quantity`, { quantity });
    return response.data;
  },

  // Usage
  async getUsage(itemId?: string): Promise<InventoryUsage[]> {
    const url = itemId ? `/inventory/usage?item_id=${itemId}` : '/inventory/usage';
    const response = await apiClient.get<InventoryUsage[]>(url);
    return response.data;
  },

  async getLowStock(): Promise<InventoryItem[]> {
    const response = await apiClient.get<InventoryItem[]>('/inventory/low-stock');
    return response.data;
  },
};
