/**
 * Workspace Hook
 * Manages workspace data and operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workspaceService, Workspace, WorkspaceCreate, OnboardingStatus } from '@/lib/api';
import { toast } from 'sonner';

export const useWorkspace = (workspaceId?: string) => {
  const queryClient = useQueryClient();

  // Get workspace
  const { data: workspace, isLoading } = useQuery<Workspace>({
    queryKey: ['workspace', workspaceId],
    queryFn: () => workspaceService.getById(workspaceId!),
    enabled: !!workspaceId,
  });

  // Get onboarding status
  const { data: onboardingStatus } = useQuery<OnboardingStatus>({
    queryKey: ['workspace', workspaceId, 'onboarding'],
    queryFn: () => workspaceService.getOnboardingStatus(workspaceId!),
    enabled: !!workspaceId,
  });

  // Create workspace mutation
  const createMutation = useMutation({
    mutationFn: (data: WorkspaceCreate) => workspaceService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace'] });
      toast.success('Workspace created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create workspace');
    },
  });

  // Activate workspace mutation
  const activateMutation = useMutation({
    mutationFn: (id: string) => workspaceService.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace'] });
      toast.success('Workspace activated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to activate workspace');
    },
  });

  return {
    workspace,
    onboardingStatus,
    isLoading,
    createWorkspace: createMutation.mutate,
    activateWorkspace: activateMutation.mutate,
    isCreating: createMutation.isPending,
    isActivating: activateMutation.isPending,
  };
};
