import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { integrationService } from '@/lib/api/services/integration.service';

export function useIntegrations() {
  const queryClient = useQueryClient();

  const { data: integrations, isLoading } = useQuery({
    queryKey: ['integrations'],
    queryFn: integrationService.getIntegrations,
  });

  const verifyMutation = useMutation({
    mutationFn: integrationService.verifyIntegration,
  });

  const createMutation = useMutation({
    mutationFn: integrationService.createIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: integrationService.deleteIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  return {
    integrations,
    isLoading,
    verifyIntegration: verifyMutation.mutateAsync,
    isVerifying: verifyMutation.isPending,
    createIntegration: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    deleteIntegration: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
