/**
 * Contacts Hook
 * Manages contact data and operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contactService, Contact, ContactCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useContacts = () => {
  const queryClient = useQueryClient();

  // Get all contacts
  const { data: contacts, isLoading } = useQuery<Contact[]>({
    queryKey: ['contacts'],
    queryFn: () => contactService.getAll(),
  });

  // Create contact
  const createMutation = useMutation({
    mutationFn: ({ data, workspaceId }: { data: ContactCreate; workspaceId: string }) => 
      contactService.create(data, workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      toast.success('Contact added successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to add contact');
    },
  });

  // Update contact
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ContactCreate> }) =>
      contactService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      toast.success('Contact updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update contact');
    },
  });

  return {
    contacts: contacts || [],
    isLoading,
    createContact: createMutation.mutate,
    updateContact: updateMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
  };
};
