import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useStaff } from '../hooks/useStaff';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  UserPlus,
  Mail,
  Shield,
  Trash2,
  Clock,
  CheckCircle,
  XCircle,
  Info,
} from 'lucide-react';

export default function StaffManagement() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    invitations,
    staffMembers,
    inviteStaff,
    revokeInvitation,
    updatePermissions,
    removeStaff,
    isInviting,
    fetchInvitations,
    fetchStaffMembers,
  } = useStaff();

  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [showPermissionsDialog, setShowPermissionsDialog] = useState(false);
  const [selectedMember, setSelectedMember] = useState<any>(null);

  const [inviteEmail, setInviteEmail] = useState('');
  const [permissions, setPermissions] = useState({
    can_access_inbox: true,
    can_manage_bookings: true,
    can_view_forms: true,
    can_view_inventory: true,
  });

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    if (isOwner) {
      fetchInvitations();
      fetchStaffMembers();
    }
  }, [isOwner, fetchInvitations, fetchStaffMembers]);

  const handleInvite = async () => {
    if (!inviteEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    try {
      await inviteStaff({
        email: inviteEmail,
        permissions,
      });
      toast.success('Invitation sent successfully');
      setShowInviteDialog(false);
      setInviteEmail('');
      setPermissions({
        can_access_inbox: true,
        can_manage_bookings: true,
        can_view_forms: true,
        can_view_inventory: true,
      });
      fetchInvitations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleRevoke = async (invitationId: string) => {
    if (!confirm('Are you sure you want to revoke this invitation?')) {
      return;
    }

    try {
      await revokeInvitation(invitationId);
      toast.success('Invitation revoked');
      fetchInvitations();
    } catch (error: any) {
      toast.error('Failed to revoke invitation');
    }
  };

  const handleUpdatePermissions = async () => {
    if (!selectedMember) return;

    try {
      await updatePermissions({
        userId: selectedMember.id,
        permissions,
      });
      toast.success('Permissions updated');
      setShowPermissionsDialog(false);
      setSelectedMember(null);
      fetchStaffMembers();
    } catch (error: any) {
      toast.error('Failed to update permissions');
    }
  };

  const handleRemove = async (userId: string, name: string) => {
    if (!confirm(`Are you sure you want to remove ${name}?`)) {
      return;
    }

    try {
      await removeStaff(userId);
      toast.success('Staff member removed');
      fetchStaffMembers();
    } catch (error: any) {
      toast.error('Failed to remove staff member');
    }
  };

  const openPermissionsDialog = (member: any) => {
    setSelectedMember(member);
    setPermissions(member.permissions || {
      can_access_inbox: true,
      can_manage_bookings: true,
      can_view_forms: true,
      can_view_inventory: true,
    });
    setShowPermissionsDialog(true);
  };

  const handleSkip = () => {
    navigate('/workspace-activation');
  };

  const handleContinue = () => {
    navigate('/workspace-activation');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Staff Management (Owner Only)</CardTitle>
            <CardDescription>
              Only workspace owners can manage staff members.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Contact your workspace owner for staff management.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  const pendingInvitations = invitations.filter((inv) => inv.status === 'pending');

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Step 7: Add Staff & Permissions</h1>
        <p className="text-muted-foreground mt-2">
          Invite staff members and assign permissions
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Staff Members */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Staff Members</CardTitle>
                <CardDescription>
                  Manage your team members
                </CardDescription>
              </div>
              <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Invite Staff
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Invite Staff Member</DialogTitle>
                    <DialogDescription>
                      Send an invitation email with permissions
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="email">Email Address *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                        placeholder="staff@example.com"
                      />
                    </div>

                    <div>
                      <Label>Permissions</Label>
                      <div className="space-y-2 mt-2">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="inbox"
                            checked={permissions.can_access_inbox}
                            onCheckedChange={(checked) =>
                              setPermissions({ ...permissions, can_access_inbox: !!checked })
                            }
                          />
                          <label htmlFor="inbox" className="text-sm">
                            Access Inbox
                          </label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="bookings"
                            checked={permissions.can_manage_bookings}
                            onCheckedChange={(checked) =>
                              setPermissions({ ...permissions, can_manage_bookings: !!checked })
                            }
                          />
                          <label htmlFor="bookings" className="text-sm">
                            Manage Bookings
                          </label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="forms"
                            checked={permissions.can_view_forms}
                            onCheckedChange={(checked) =>
                              setPermissions({ ...permissions, can_view_forms: !!checked })
                            }
                          />
                          <label htmlFor="forms" className="text-sm">
                            View Forms
                          </label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="inventory"
                            checked={permissions.can_view_inventory}
                            onCheckedChange={(checked) =>
                              setPermissions({ ...permissions, can_view_inventory: !!checked })
                            }
                          />
                          <label htmlFor="inventory" className="text-sm">
                            View Inventory
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        onClick={() => setShowInviteDialog(false)}
                      >
                        Cancel
                      </Button>
                      <Button onClick={handleInvite} disabled={isInviting}>
                        {isInviting ? 'Sending...' : 'Send Invitation'}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {staffMembers.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <UserPlus className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No staff members yet</p>
                <p className="text-sm mt-1">Invite your first team member</p>
              </div>
            ) : (
              <div className="space-y-3">
                {staffMembers.map((member) => (
                  <Card key={member.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold">{member.full_name}</h4>
                            {!member.is_active && (
                              <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                                Inactive
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">{member.email}</p>
                          {member.permissions && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {member.permissions.can_access_inbox && (
                                <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                                  Inbox
                                </span>
                              )}
                              {member.permissions.can_manage_bookings && (
                                <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">
                                  Bookings
                                </span>
                              )}
                              {member.permissions.can_view_forms && (
                                <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">
                                  Forms
                                </span>
                              )}
                              {member.permissions.can_view_inventory && (
                                <span className="text-xs px-2 py-0.5 rounded bg-orange-100 text-orange-700">
                                  Inventory
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openPermissionsDialog(member)}
                          >
                            <Shield className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemove(member.id, member.full_name)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pending Invitations */}
        <Card>
          <CardHeader>
            <CardTitle>Pending Invitations</CardTitle>
            <CardDescription>
              Invitations waiting to be accepted
            </CardDescription>
          </CardHeader>
          <CardContent>
            {pendingInvitations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No pending invitations</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingInvitations.map((invitation) => (
                  <Card key={invitation.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <p className="font-medium">{invitation.email}</p>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            Expires: {new Date(invitation.expires_at).toLocaleDateString()}
                          </p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {invitation.permissions.can_access_inbox && (
                              <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                                Inbox
                              </span>
                            )}
                            {invitation.permissions.can_manage_bookings && (
                              <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">
                                Bookings
                              </span>
                            )}
                            {invitation.permissions.can_view_forms && (
                              <span className="text-xs px-2 py-0.5 rounded bg-purple-100 text-purple-700">
                                Forms
                              </span>
                            )}
                            {invitation.permissions.can_view_inventory && (
                              <span className="text-xs px-2 py-0.5 rounded bg-orange-100 text-orange-700">
                                Inventory
                              </span>
                            )}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRevoke(invitation.id)}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Permissions Dialog */}
      <Dialog open={showPermissionsDialog} onOpenChange={setShowPermissionsDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Permissions</DialogTitle>
            <DialogDescription>
              Manage permissions for {selectedMember?.full_name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="perm-inbox"
                  checked={permissions.can_access_inbox}
                  onCheckedChange={(checked) =>
                    setPermissions({ ...permissions, can_access_inbox: !!checked })
                  }
                />
                <label htmlFor="perm-inbox" className="text-sm">
                  Access Inbox
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="perm-bookings"
                  checked={permissions.can_manage_bookings}
                  onCheckedChange={(checked) =>
                    setPermissions({ ...permissions, can_manage_bookings: !!checked })
                  }
                />
                <label htmlFor="perm-bookings" className="text-sm">
                  Manage Bookings
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="perm-forms"
                  checked={permissions.can_view_forms}
                  onCheckedChange={(checked) =>
                    setPermissions({ ...permissions, can_view_forms: !!checked })
                  }
                />
                <label htmlFor="perm-forms" className="text-sm">
                  View Forms
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="perm-inventory"
                  checked={permissions.can_view_inventory}
                  onCheckedChange={(checked) =>
                    setPermissions({ ...permissions, can_view_inventory: !!checked })
                  }
                />
                <label htmlFor="perm-inventory" className="text-sm">
                  View Inventory
                </label>
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowPermissionsDialog(false);
                  setSelectedMember(null);
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleUpdatePermissions}>
                Update Permissions
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Actions */}
      <div className="flex justify-between mt-6">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button onClick={handleContinue}>
          Continue to Activation
        </Button>
      </div>
    </div>
  );
}
