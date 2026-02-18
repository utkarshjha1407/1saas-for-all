import apiClient from '../client';
import type {
  BookingType,
  BookingTypeCreate,
  BookingTypeUpdate,
  AvailabilitySlot,
  TimeSlot,
} from '../types';

export const bookingTypeService = {
  // Create booking type
  create: async (data: BookingTypeCreate): Promise<BookingType> => {
    const response = await apiClient.post('/booking-types', data);
    return response.data;
  },

  // List all booking types
  list: async (): Promise<BookingType[]> => {
    const response = await apiClient.get('/booking-types');
    return response.data;
  },

  // Get single booking type
  get: async (id: string): Promise<BookingType> => {
    const response = await apiClient.get(`/booking-types/${id}`);
    return response.data;
  },

  // Update booking type
  update: async (id: string, data: BookingTypeUpdate): Promise<BookingType> => {
    const response = await apiClient.put(`/booking-types/${id}`, data);
    return response.data;
  },

  // Delete booking type
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/booking-types/${id}`);
  },

  // Set availability
  setAvailability: async (id: string, slots: AvailabilitySlot[]): Promise<AvailabilitySlot[]> => {
    const response = await apiClient.post(`/booking-types/${id}/availability`, slots);
    return response.data;
  },

  // Get availability
  getAvailability: async (id: string): Promise<AvailabilitySlot[]> => {
    const response = await apiClient.get(`/booking-types/${id}/availability`);
    return response.data;
  },

  // Get available slots
  getAvailableSlots: async (
    id: string,
    startDate: string,
    endDate: string
  ): Promise<TimeSlot[]> => {
    const response = await apiClient.get(`/booking-types/${id}/available-slots`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get public booking types
  getPublic: async (workspaceId: string): Promise<BookingType[]> => {
    const response = await apiClient.get(`/public/booking-types/${workspaceId}`);
    return response.data;
  },

  // Create public booking
  createPublicBooking: async (data: {
    workspace_id: string;
    booking_type_id: string;
    booking_date: string;
    start_time: string;
    contact_name: string;
    contact_email?: string;
    contact_phone?: string;
    notes?: string;
  }): Promise<{ success: boolean; booking: any; message: string }> => {
    const response = await apiClient.post('/public/bookings', data);
    return response.data;
  },
};

export default bookingTypeService;
