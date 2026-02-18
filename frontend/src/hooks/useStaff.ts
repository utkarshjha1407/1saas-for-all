/**
 * Staff Management Hook
 * Manages staff invitations, permissions, and workspace activation
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { staffService } from '@/lib/api/services/staff.service';
import type {
  StaffInvitation,
  StaffInvitationCreate,
  StaffMember,
  StaffPermissions,
  WorkspaceActivation,
} from '@/lib/api/types';

export const useStaff = () => {
  const queryClient = useQueryClient();

  // Get invitations
  const { data: invitations = [], refetch: fetchInvitations } = useQuery<StaffInvitation[]>({
    queryKey: ['staff', 'invitations'],
    queryFn: () => staffService.getInvitations(),
  });

  // Get staff members
  const { data: staffMembers = [], refetch: fetchStaffMembers } = useQuery<StaffMember[]>({
    queryKey: ['staff', 'members'],
    queryFn: () => staffService.getStaffMembers(),
  });

  // Get activation status
  const { data: activation, refetch: fetchActivation } = useQuery<WorkspaceActivation>({
    queryKey: ['staff', 'activation'],
    queryFn: () => staffService.checkActivation(),
  });

  // Invite staff
  const inviteStaffMutation = useMutation({
    mutationFn: (data: StaffInvitationCreate) => staffService.inviteStaff(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff', 'invitations'] });
    },
  });

  // Revoke invitation
  const revokeInvitationMutation = useMutation({
    mutationFn: (invitationId: string) => staffService.revokeInvitation(invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff', 'invitations'] });
    },
  });

  // Update permissions
  const updatePermissionsMutation = useMutation({
    mutationFn: ({ userId, permissions }: { userId: string; permissions: Partial<StaffPermissions> }) =>
      staffService.updateStaffPermissions(userId, permissions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff', 'members'] });
    },
  });

  // Remove staff member
  const removeStaffMutation = useMutation({
    mutationFn: (userId: string) => staffService.removeStaffMember(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff', 'members'] });
    },
  });

  // Activate workspace
  const activateWorkspaceMutation = useMutation({
    mutationFn: () => staffService.activateWorkspace(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff', 'activation'] });
    },
  });

  return {
    invitations,
    staffMembers,
    activation,
    fetchInvitations,
    fetchStaffMembers,
    fetchActivation,
    inviteStaff: inviteStaffMutation.mutateAsync,
    revokeInvitation: revokeInvitationMutation.mutateAsync,
    updatePermissions: updatePermissionsMutation.mutateAsync,
    removeStaff: removeStaffMutation.mutateAsync,
    activateWorkspace: activateWorkspaceMutation.mutateAsync,
    isInviting: inviteStaffMutation.isPending,
    isActivating: activateWorkspaceMutation.isPending,
  };
};
