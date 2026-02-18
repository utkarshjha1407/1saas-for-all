/**
 * Inventory Service
 * Handles inventory items, usage tracking, and forecasting
 */

import apiClient from '../client';
import {
  InventoryItem,
  InventoryItemCreate,
  InventoryItemUpdate,
  InventoryAdjustment,
  InventoryUsage,
  InventoryForecast,
} from '../types';

export const inventoryService = {
  // Items
  async getItems(lowStockOnly?: boolean): Promise<InventoryItem[]> {
    const params = lowStockOnly ? { low_stock_only: true } : {};
    const response = await apiClient.get<InventoryItem[]>('/inventory/items', { params });
    return response.data;
  },

  async getItem(id: string): Promise<InventoryItem> {
    const response = await apiClient.get<InventoryItem>(`/inventory/items/${id}`);
    return response.data;
  },

  async createItem(data: InventoryItemCreate): Promise<InventoryItem> {
    const response = await apiClient.post<InventoryItem>('/inventory/items', data);
    return response.data;
  },

  async updateItem(id: string, data: InventoryItemUpdate): Promise<InventoryItem> {
    const response = await apiClient.put<InventoryItem>(`/inventory/items/${id}`, data);
    return response.data;
  },

  async deleteItem(id: string): Promise<void> {
    await apiClient.delete(`/inventory/items/${id}`);
  },

  async adjustQuantity(id: string, data: InventoryAdjustment): Promise<InventoryItem> {
    const response = await apiClient.post<InventoryItem>(`/inventory/items/${id}/adjust`, data);
    return response.data;
  },

  // Usage
  async getUsageHistory(itemId: string, limit?: number): Promise<InventoryUsage[]> {
    const params = limit ? { limit } : {};
    const response = await apiClient.get<InventoryUsage[]>(`/inventory/items/${itemId}/usage`, { params });
    return response.data;
  },

  // Forecast
  async getForecast(daysAhead?: number): Promise<InventoryForecast[]> {
    const params = daysAhead ? { days_ahead: daysAhead } : {};
    const response = await apiClient.get<InventoryForecast[]>('/inventory/forecast', { params });
    return response.data;
  },
};

export default inventoryService;
