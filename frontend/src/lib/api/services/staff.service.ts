/**
 * Staff Management Service
 * Handles staff invitations, permissions, and workspace activation
 */

import apiClient from '../client';
import {
  StaffInvitation,
  StaffInvitationCreate,
  StaffInvitationAccept,
  StaffMember,
  StaffPermissions,
  WorkspaceActivation,
} from '../types';

export const staffService = {
  // Invitations
  async inviteStaff(data: StaffInvitationCreate): Promise<StaffInvitation> {
    const response = await apiClient.post<StaffInvitation>('/staff/invitations', data);
    return response.data;
  },

  async getInvitations(status?: string): Promise<StaffInvitation[]> {
    const params = status ? { status } : {};
    const response = await apiClient.get<StaffInvitation[]>('/staff/invitations', { params });
    return response.data;
  },

  async revokeInvitation(invitationId: string): Promise<void> {
    await apiClient.post(`/staff/invitations/${invitationId}/revoke`);
  },

  async verifyInvitationToken(token: string): Promise<any> {
    const response = await apiClient.get(`/staff/invitations/verify/${token}`);
    return response.data;
  },

  async acceptInvitation(data: StaffInvitationAccept): Promise<any> {
    const response = await apiClient.post('/staff/invitations/accept', data);
    return response.data;
  },

  // Staff Members
  async getStaffMembers(): Promise<StaffMember[]> {
    const response = await apiClient.get<StaffMember[]>('/staff/members');
    return response.data;
  },

  async updateStaffPermissions(userId: string, permissions: Partial<StaffPermissions>): Promise<void> {
    await apiClient.put(`/staff/members/${userId}/permissions`, permissions);
  },

  async removeStaffMember(userId: string): Promise<void> {
    await apiClient.delete(`/staff/members/${userId}`);
  },

  // Workspace Activation
  async checkActivation(): Promise<WorkspaceActivation> {
    const response = await apiClient.get<WorkspaceActivation>('/staff/activation');
    return response.data;
  },

  async activateWorkspace(): Promise<any> {
    const response = await apiClient.post('/staff/activation/activate');
    return response.data;
  },
};

export default staffService;
