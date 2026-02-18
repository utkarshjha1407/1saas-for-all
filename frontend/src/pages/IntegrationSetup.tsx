import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useIntegrations } from '@/hooks/useIntegrations';
import { CheckCircle2, XCircle, Loader2, Mail, MessageSquare } from 'lucide-react';

export default function IntegrationSetup() {
  const navigate = useNavigate();
  const { integrations, isLoading, verifyIntegration, createIntegration, isVerifying, isCreating } = useIntegrations();

  // Email provider state
  const [emailProvider, setEmailProvider] = useState<'resend' | 'sendgrid'>('resend');
  const [emailApiKey, setEmailApiKey] = useState('');
  const [emailVerified, setEmailVerified] = useState(false);
  const [emailError, setEmailError] = useState('');

  // SMS provider state
  const [smsAccountSid, setSmsAccountSid] = useState('');
  const [smsAuthToken, setSmsAuthToken] = useState('');
  const [smsPhoneNumber, setSmsPhoneNumber] = useState('');
  const [smsVerified, setSmsVerified] = useState(false);
  const [smsError, setSmsError] = useState('');

  // Check existing integrations
  useEffect(() => {
    if (integrations) {
      setEmailVerified(integrations.has_email);
      setSmsVerified(integrations.has_sms);
    }
  }, [integrations]);

  const handleVerifyEmail = async () => {
    setEmailError('');
    
    if (!emailApiKey.trim()) {
      setEmailError('API key is required');
      return;
    }

    try {
      const result = await verifyIntegration({
        provider: emailProvider,
        config: { api_key: emailApiKey }
      });

      if (result.success) {
        setEmailVerified(true);
      } else {
        setEmailError(result.message || 'Verification failed');
        setEmailVerified(false);
      }
    } catch (error: any) {
      setEmailError(error.message || 'Failed to verify email provider');
      setEmailVerified(false);
    }
  };

  const handleVerifySMS = async () => {
    setSmsError('');
    
    if (!smsAccountSid.trim() || !smsAuthToken.trim() || !smsPhoneNumber.trim()) {
      setSmsError('All fields are required');
      return;
    }

    if (!smsPhoneNumber.startsWith('+')) {
      setSmsError('Phone number must be in E.164 format (e.g., +1234567890)');
      return;
    }

    try {
      const result = await verifyIntegration({
        provider: 'twilio',
        config: {
          account_sid: smsAccountSid,
          auth_token: smsAuthToken,
          phone_number: smsPhoneNumber
        }
      });

      if (result.success) {
        setSmsVerified(true);
      } else {
        setSmsError(result.message || 'Verification failed');
        setSmsVerified(false);
      }
    } catch (error: any) {
      setSmsError(error.message || 'Failed to verify SMS provider');
      setSmsVerified(false);
    }
  };

  const handleSaveEmail = async () => {
    if (!emailVerified) {
      setEmailError('Please verify the connection first');
      return;
    }

    try {
      await createIntegration({
        provider: emailProvider,
        config: { api_key: emailApiKey }
      });
    } catch (error: any) {
      setEmailError(error.message || 'Failed to save email integration');
    }
  };

  const handleSaveSMS = async () => {
    if (!smsVerified) {
      setSmsError('Please verify the connection first');
      return;
    }

    try {
      await createIntegration({
        provider: 'twilio',
        config: {
          account_sid: smsAccountSid,
          auth_token: smsAuthToken,
          phone_number: smsPhoneNumber
        }
      });
    } catch (error: any) {
      setSmsError(error.message || 'Failed to save SMS integration');
    }
  };

  const handleContinue = () => {
    if (!integrations?.has_any) {
      alert('Please set up at least one communication channel (Email or SMS)');
      return;
    }
    navigate('/contact-form-builder');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Step 2: Set Up Communication</h1>
        <p className="text-muted-foreground">
          Connect your email and SMS services. At least one channel is required.
        </p>
      </div>

      {/* Email Integration */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            <CardTitle>Email Service</CardTitle>
            {integrations?.has_email && (
              <CheckCircle2 className="h-5 w-5 text-green-600 ml-auto" />
            )}
          </div>
          <CardDescription>
            Connect Resend or SendGrid for sending confirmations and alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Email Provider</Label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="resend"
                  checked={emailProvider === 'resend'}
                  onChange={(e) => setEmailProvider(e.target.value as 'resend')}
                  disabled={integrations?.has_email}
                />
                Resend
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  value="sendgrid"
                  checked={emailProvider === 'sendgrid'}
                  onChange={(e) => setEmailProvider(e.target.value as 'sendgrid')}
                  disabled={integrations?.has_email}
                />
                SendGrid
              </label>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="emailApiKey">API Key</Label>
            <Input
              id="emailApiKey"
              type="password"
              placeholder={emailProvider === 'resend' ? 're_...' : 'SG...'}
              value={emailApiKey}
              onChange={(e) => setEmailApiKey(e.target.value)}
              disabled={integrations?.has_email}
            />
          </div>

          {emailError && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{emailError}</AlertDescription>
            </Alert>
          )}

          {emailVerified && !integrations?.has_email && (
            <Alert>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>Connection verified successfully!</AlertDescription>
            </Alert>
          )}

          {!integrations?.has_email && (
            <div className="flex gap-2">
              <Button
                onClick={handleVerifyEmail}
                disabled={isVerifying || !emailApiKey.trim()}
                variant="outline"
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Test Connection'
                )}
              </Button>
              <Button
                onClick={handleSaveEmail}
                disabled={!emailVerified || isCreating}
              >
                {isCreating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Email Integration'
                )}
              </Button>
            </div>
          )}

          {integrations?.has_email && (
            <Alert>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>Email integration is active</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* SMS Integration */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            <CardTitle>SMS Service (Twilio)</CardTitle>
            {integrations?.has_sms && (
              <CheckCircle2 className="h-5 w-5 text-green-600 ml-auto" />
            )}
          </div>
          <CardDescription>
            Connect Twilio for sending reminders and short updates
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="smsAccountSid">Account SID</Label>
            <Input
              id="smsAccountSid"
              type="text"
              placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              value={smsAccountSid}
              onChange={(e) => setSmsAccountSid(e.target.value)}
              disabled={integrations?.has_sms}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="smsAuthToken">Auth Token</Label>
            <Input
              id="smsAuthToken"
              type="password"
              placeholder="Your Twilio Auth Token"
              value={smsAuthToken}
              onChange={(e) => setSmsAuthToken(e.target.value)}
              disabled={integrations?.has_sms}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="smsPhoneNumber">Phone Number</Label>
            <Input
              id="smsPhoneNumber"
              type="tel"
              placeholder="+1234567890"
              value={smsPhoneNumber}
              onChange={(e) => setSmsPhoneNumber(e.target.value)}
              disabled={integrations?.has_sms}
            />
            <p className="text-sm text-muted-foreground">
              Must be in E.164 format (e.g., +1234567890)
            </p>
          </div>

          {smsError && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{smsError}</AlertDescription>
            </Alert>
          )}

          {smsVerified && !integrations?.has_sms && (
            <Alert>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>Connection verified successfully!</AlertDescription>
            </Alert>
          )}

          {!integrations?.has_sms && (
            <div className="flex gap-2">
              <Button
                onClick={handleVerifySMS}
                disabled={isVerifying || !smsAccountSid.trim() || !smsAuthToken.trim() || !smsPhoneNumber.trim()}
                variant="outline"
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Test Connection'
                )}
              </Button>
              <Button
                onClick={handleSaveSMS}
                disabled={!smsVerified || isCreating}
              >
                {isCreating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save SMS Integration'
                )}
              </Button>
            </div>
          )}

          {integrations?.has_sms && (
            <Alert>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>SMS integration is active</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Validation Alert */}
      {!integrations?.has_any && (
        <Alert variant="destructive" className="mb-6">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            At least one communication channel (Email or SMS) is required to continue
          </AlertDescription>
        </Alert>
      )}

      {/* Continue Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleContinue}
          disabled={!integrations?.has_any}
          size="lg"
        >
          Continue to Contact Form
        </Button>
      </div>
    </div>
  );
}
