/**
 * Booking Service
 * Handles booking management
 */

import apiClient from '../client';
import { BookingCreate, Booking } from '../types';

export const bookingService = {
  /**
   * Create a new booking (public endpoint)
   */
  async create(data: BookingCreate, workspaceId: string): Promise<Booking> {
    const response = await apiClient.post<Booking>(`/bookings?workspace_id=${workspaceId}`, data);
    return response.data;
  },

  /**
   * Get all bookings
   */
  async getAll(params?: { start_date?: string; end_date?: string }): Promise<Booking[]> {
    const response = await apiClient.get<Booking[]>('/bookings', { params });
    return response.data;
  },

  /**
   * Get today's bookings
   */
  async getToday(): Promise<Booking[]> {
    const response = await apiClient.get<Booking[]>('/bookings/today');
    return response.data;
  },

  /**
   * Get upcoming bookings
   */
  async getUpcoming(days: number = 7): Promise<Booking[]> {
    const response = await apiClient.get<Booking[]>(`/bookings/upcoming?days=${days}`);
    return response.data;
  },

  /**
   * Update booking
   */
  async update(id: string, data: Partial<BookingCreate>): Promise<Booking> {
    const response = await apiClient.patch<Booking>(`/bookings/${id}`, data);
    return response.data;
  },

  /**
   * Update booking status
   */
  async updateStatus(id: string, status: Booking['status']): Promise<Booking> {
    const response = await apiClient.post<Booking>(`/bookings/${id}/status?status=${status}`);
    return response.data;
  },
};
