import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useStaff } from '../hooks/useStaff';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  CheckCircle,
  XCircle,
  Rocket,
  AlertTriangle,
  Info,
  Loader2,
} from 'lucide-react';

export default function WorkspaceActivation() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { activation, activateWorkspace, isActivating, fetchActivation } = useStaff();

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    if (isOwner) {
      fetchActivation();
    }
  }, [isOwner, fetchActivation]);

  const handleActivate = async () => {
    if (!activation?.can_activate) {
      toast.error('Please complete all requirements before activating');
      return;
    }

    if (!confirm('Are you sure you want to activate your workspace? This will make your booking links and forms live.')) {
      return;
    }

    try {
      await activateWorkspace();
      toast.success('Workspace activated successfully! 🎉');
      fetchActivation();
      
      // Navigate to dashboard after short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to activate workspace');
    }
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Workspace Activation (Owner Only)</CardTitle>
            <CardDescription>
              Only workspace owners can activate the workspace.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Contact your workspace owner for activation.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!activation) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const checklist = activation.checklist;
  const isActivated = activation.is_activated;

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Step 8: Activate Workspace</h1>
        <p className="text-muted-foreground mt-2">
          {isActivated
            ? 'Your workspace is live and ready to accept bookings!'
            : 'Complete the requirements below to activate your workspace'}
        </p>
      </div>

      {isActivated ? (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <CardTitle className="text-green-900">Workspace Activated!</CardTitle>
                <CardDescription className="text-green-700">
                  Activated on {new Date(activation.activated_at!).toLocaleDateString()}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Alert className="bg-white border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-900">
                  Your booking links are now live and accepting appointments
                </AlertDescription>
              </Alert>
              <Alert className="bg-white border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-900">
                  Forms are being sent automatically after bookings
                </AlertDescription>
              </Alert>
              <Alert className="bg-white border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-900">
                  Automation is running (reminders, alerts, inventory tracking)
                </AlertDescription>
              </Alert>
            </div>

            <div className="mt-6">
              <Button onClick={handleGoToDashboard} className="w-full" size="lg">
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Activation Requirements</CardTitle>
              <CardDescription>
                Complete these steps to activate your workspace
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Communication Channel */}
                <div className="flex items-start gap-3">
                  {checklist.communication_connected ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold">Communication Channel Connected</h4>
                    <p className="text-sm text-muted-foreground">
                      At least one email or SMS integration must be active
                    </p>
                    {!checklist.communication_connected && (
                      <Button
                        variant="link"
                        className="h-auto p-0 mt-1"
                        onClick={() => navigate('/integration-setup')}
                      >
                        Set up integrations →
                      </Button>
                    )}
                  </div>
                </div>

                {/* Booking Type */}
                <div className="flex items-start gap-3">
                  {checklist.booking_type_exists ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold">At Least One Booking Type</h4>
                    <p className="text-sm text-muted-foreground">
                      Create at least one service that clients can book
                    </p>
                    {!checklist.booking_type_exists && (
                      <Button
                        variant="link"
                        className="h-auto p-0 mt-1"
                        onClick={() => navigate('/booking-setup')}
                      >
                        Create booking types →
                      </Button>
                    )}
                  </div>
                </div>

                {/* Availability */}
                <div className="flex items-start gap-3">
                  {checklist.availability_defined ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold">Availability Defined</h4>
                    <p className="text-sm text-muted-foreground">
                      Set your available hours for bookings
                    </p>
                    {!checklist.availability_defined && (
                      <Button
                        variant="link"
                        className="h-auto p-0 mt-1"
                        onClick={() => navigate('/booking-setup')}
                      >
                        Define availability →
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {activation.missing_requirements.length > 0 && (
            <Alert className="mb-6 border-orange-200 bg-orange-50">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-800">
                <strong>Missing Requirements:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  {activation.missing_requirements.map((req, index) => (
                    <li key={index}>{req}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Ready to Go Live?</CardTitle>
              <CardDescription>
                Once activated, your workspace will be fully operational
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    <strong>What happens when you activate:</strong>
                    <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
                      <li>Public booking links become active</li>
                      <li>Contact forms start accepting submissions</li>
                      <li>Automated emails and SMS are sent</li>
                      <li>Forms are sent automatically after bookings</li>
                      <li>Inventory tracking begins</li>
                      <li>Reminders and alerts are enabled</li>
                    </ul>
                  </AlertDescription>
                </Alert>

                <Button
                  onClick={handleActivate}
                  disabled={!activation.can_activate || isActivating}
                  className="w-full"
                  size="lg"
                >
                  {isActivating ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Activating...
                    </>
                  ) : (
                    <>
                      <Rocket className="h-5 w-5 mr-2" />
                      Activate Workspace
                    </>
                  )}
                </Button>

                {!activation.can_activate && (
                  <p className="text-sm text-center text-muted-foreground">
                    Complete all requirements above to activate
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
