/**
 * Bookings Hook
 * Manages booking data and operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bookingService, Booking, BookingCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useBookings = () => {
  const queryClient = useQueryClient();

  // Get all bookings
  const { data: bookings, isLoading } = useQuery<Booking[]>({
    queryKey: ['bookings'],
    queryFn: () => bookingService.getAll(),
  });

  // Get today's bookings
  const { data: todayBookings } = useQuery<Booking[]>({
    queryKey: ['bookings', 'today'],
    queryFn: () => bookingService.getToday(),
  });

  // Get upcoming bookings
  const { data: upcomingBookings } = useQuery<Booking[]>({
    queryKey: ['bookings', 'upcoming'],
    queryFn: () => bookingService.getUpcoming(7),
  });

  // Create booking mutation
  const createMutation = useMutation({
    mutationFn: ({ data, workspaceId }: { data: BookingCreate; workspaceId: string }) =>
      bookingService.create(data, workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      toast.success('Booking created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create booking');
    },
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Booking['status'] }) =>
      bookingService.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
      toast.success('Booking status updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update booking');
    },
  });

  return {
    bookings,
    todayBookings,
    upcomingBookings,
    isLoading,
    createBooking: createMutation.mutate,
    updateStatus: updateStatusMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateStatusMutation.isPending,
  };
};
