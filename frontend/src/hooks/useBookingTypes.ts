import { useState, useCallback } from 'react';
import { bookingTypeService } from '../lib/api/services/bookingType.service';
import type {
  BookingType,
  BookingTypeCreate,
  BookingTypeUpdate,
  AvailabilitySlot,
  TimeSlot,
} from '../lib/api/types';

export const useBookingTypes = () => {
  const [bookingTypes, setBookingTypes] = useState<BookingType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBookingTypes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await bookingTypeService.list();
      setBookingTypes(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch booking types');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createBookingType = useCallback(async (data: BookingTypeCreate) => {
    setLoading(true);
    setError(null);
    try {
      const newBookingType = await bookingTypeService.create(data);
      setBookingTypes((prev) => [...prev, newBookingType]);
      return newBookingType;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create booking type');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateBookingType = useCallback(async (id: string, data: BookingTypeUpdate) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await bookingTypeService.update(id, data);
      setBookingTypes((prev) =>
        prev.map((bt) => (bt.id === id ? updated : bt))
      );
      return updated;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update booking type');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteBookingType = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await bookingTypeService.delete(id);
      setBookingTypes((prev) => prev.filter((bt) => bt.id !== id));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete booking type');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const setAvailability = useCallback(async (id: string, slots: AvailabilitySlot[]) => {
    setLoading(true);
    setError(null);
    try {
      const availability = await bookingTypeService.setAvailability(id, slots);
      return availability;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to set availability');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAvailability = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const availability = await bookingTypeService.getAvailability(id);
      return availability;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get availability');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAvailableSlots = useCallback(
    async (id: string, startDate: string, endDate: string) => {
      setLoading(true);
      setError(null);
      try {
        const slots = await bookingTypeService.getAvailableSlots(id, startDate, endDate);
        return slots;
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to get available slots');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    bookingTypes,
    loading,
    error,
    fetchBookingTypes,
    createBookingType,
    updateBookingType,
    deleteBookingType,
    setAvailability,
    getAvailability,
    getAvailableSlots,
  };
};

export default useBookingTypes;
