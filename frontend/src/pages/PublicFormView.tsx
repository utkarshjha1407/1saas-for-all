import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import { FileText, Download, CheckCircle, ExternalLink } from 'lucide-react';
import { formService } from '../lib/api/services/form.service';

export default function PublicFormView() {
  const { submissionId } = useParams<{ submissionId: string }>();
  const [formData, setFormData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState(false);

  useEffect(() => {
    loadForm();
  }, [submissionId]);

  const loadForm = async () => {
    if (!submissionId) return;

    try {
      const data = await formService.getPublicFormSubmission(submissionId);
      setFormData(data);
    } catch (error: any) {
      toast.error('Failed to load form');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!submissionId || !formData?.file_url) return;

    try {
      // Track download
      await formService.trackDownload(submissionId);
      
      // Open file in new tab
      window.open(formData.file_url, '_blank');
      
      toast.success('Form opened in new tab');
    } catch (error: any) {
      toast.error('Failed to open form');
    }
  };

  const handleMarkComplete = async () => {
    if (!submissionId) return;

    setMarking(true);
    try {
      await formService.markComplete(submissionId);
      toast.success('Form marked as complete!');
      
      // Reload form data
      await loadForm();
    } catch (error: any) {
      toast.error('Failed to mark form as complete');
    } finally {
      setMarking(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-muted-foreground">Loading form...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="pt-6">
            <Alert variant="destructive">
              <AlertDescription>Form not found or access denied.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isCompleted = formData.status === 'completed';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">{formData.form_name}</CardTitle>
          {formData.form_description && (
            <CardDescription className="text-base mt-2">
              {formData.form_description}
            </CardDescription>
          )}
        </CardHeader>

        <CardContent className="space-y-6">
          {isCompleted && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                This form has been marked as complete. Thank you!
              </AlertDescription>
            </Alert>
          )}

          {formData.booking && (
            <div className="bg-muted/50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Appointment Details</h3>
              <div className="space-y-1 text-sm">
                <p>
                  <span className="text-muted-foreground">Service:</span>{' '}
                  {formData.booking.booking_types?.name}
                </p>
                <p>
                  <span className="text-muted-foreground">Date:</span>{' '}
                  {new Date(formData.booking.scheduled_at).toLocaleDateString()}
                </p>
                <p>
                  <span className="text-muted-foreground">Time:</span>{' '}
                  {new Date(formData.booking.scheduled_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          )}

          <div className="space-y-3">
            <Button
              onClick={handleDownload}
              className="w-full"
              size="lg"
            >
              <Download className="h-5 w-5 mr-2" />
              Download Form
            </Button>

            <a
              href={formData.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <Button variant="outline" className="w-full" size="lg">
                <ExternalLink className="h-5 w-5 mr-2" />
                View in Browser
              </Button>
            </a>

            {!isCompleted && (
              <Button
                onClick={handleMarkComplete}
                variant="secondary"
                className="w-full"
                size="lg"
                disabled={marking}
              >
                <CheckCircle className="h-5 w-5 mr-2" />
                {marking ? 'Marking Complete...' : 'Mark as Complete'}
              </Button>
            )}
          </div>

          <div className="text-center text-sm text-muted-foreground">
            <p>Please complete this form before your appointment.</p>
            {formData.contact?.email && (
              <p className="mt-1">
                Questions? Contact us at {formData.contact.email}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
