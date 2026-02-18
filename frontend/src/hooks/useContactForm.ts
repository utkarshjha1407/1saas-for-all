import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contactFormService } from '@/lib/api/services/contactForm.service';

export function useContactForm() {
  const queryClient = useQueryClient();

  const { data: contactForm, isLoading } = useQuery({
    queryKey: ['contactForm'],
    queryFn: contactFormService.getContactForm,
  });

  const createOrUpdateMutation = useMutation({
    mutationFn: contactFormService.createOrUpdateForm,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contactForm'] });
    },
  });

  const { data: stats, isLoading: isLoadingStats } = useQuery({
    queryKey: ['contactFormStats'],
    queryFn: contactFormService.getFormStats,
  });

  return {
    contactForm,
    isLoading,
    stats,
    isLoadingStats,
    createOrUpdateForm: createOrUpdateMutation.mutateAsync,
    isSaving: createOrUpdateMutation.isPending,
  };
}
