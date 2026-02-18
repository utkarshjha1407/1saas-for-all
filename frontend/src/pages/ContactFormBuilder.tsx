import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useContactForm } from '@/hooks/useContactForm';
import { CheckCircle2, Copy, ExternalLink, Loader2, Plus, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface FormField {
  name: string;
  type: string;
  label: string;
  placeholder: string;
  required: boolean;
  order: number;
}

export default function ContactFormBuilder() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { contactForm, isLoading, createOrUpdateForm, isSaving } = useContactForm();

  const [formName, setFormName] = useState('Contact Us');
  const [formDescription, setFormDescription] = useState('Get in touch with us');
  const [submitButtonText, setSubmitButtonText] = useState('Submit');
  const [successMessage, setSuccessMessage] = useState("Thank you! We'll be in touch soon.");
  const [welcomeMessage, setWelcomeMessage] = useState("Thank you for contacting us! We'll get back to you shortly.");
  const [fields, setFields] = useState<FormField[]>([
    { name: 'name', type: 'text', label: 'Name', placeholder: 'Your name', required: true, order: 1 },
    { name: 'email', type: 'email', label: 'Email', placeholder: 'your@email.com', required: true, order: 2 },
    { name: 'phone', type: 'tel', label: 'Phone', placeholder: '+1234567890', required: false, order: 3 },
    { name: 'message', type: 'textarea', label: 'Message', placeholder: 'How can we help you?', required: false, order: 4 },
  ]);

  // Load existing form
  useEffect(() => {
    if (contactForm) {
      setFormName(contactForm.name);
      setFormDescription(contactForm.description);
      setSubmitButtonText(contactForm.submit_button_text);
      setSuccessMessage(contactForm.success_message);
      setWelcomeMessage(contactForm.welcome_message);
      setFields(contactForm.fields);
    }
  }, [contactForm]);

  const handleSaveForm = async () => {
    // Validate at least one contact method is required
    const hasRequiredContact = fields.some(
      f => (f.name === 'email' || f.name === 'phone') && f.required
    );

    if (!hasRequiredContact) {
      toast({
        title: 'Validation Error',
        description: 'At least one contact method (email or phone) must be required',
        variant: 'destructive',
      });
      return;
    }

    try {
      await createOrUpdateForm({
        name: formName,
        description: formDescription,
        fields: fields,
        submit_button_text: submitButtonText,
        success_message: successMessage,
        welcome_message: welcomeMessage,
      });

      toast({
        title: 'Form Saved',
        description: 'Your contact form has been saved successfully',
      });
    } catch (error: any) {
      toast({
        title: 'Save Failed',
        description: error.message || 'Failed to save contact form',
        variant: 'destructive',
      });
    }
  };

  const handleCopyUrl = () => {
    if (contactForm?.public_url) {
      const fullUrl = `${window.location.origin}${contactForm.public_url}`;
      navigator.clipboard.writeText(fullUrl);
      toast({
        title: 'URL Copied',
        description: 'Public form URL copied to clipboard',
      });
    }
  };

  const handlePreview = () => {
    if (contactForm?.public_url) {
      window.open(contactForm.public_url, '_blank');
    }
  };

  const handleContinue = () => {
    if (!contactForm) {
      toast({
        title: 'Save Required',
        description: 'Please save your contact form before continuing',
        variant: 'destructive',
      });
      return;
    }
    navigate('/booking-setup');
  };

  const toggleFieldRequired = (index: number) => {
    const newFields = [...fields];
    newFields[index].required = !newFields[index].required;
    setFields(newFields);
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
        <h1 className="text-3xl font-bold mb-2">Step 3: Create Contact Form</h1>
        <p className="text-muted-foreground">
          Set up your public contact form to receive inquiries from customers
        </p>
      </div>

      {/* Form Configuration */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Form Settings</CardTitle>
          <CardDescription>Configure your contact form details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="formName">Form Name</Label>
            <Input
              id="formName"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Contact Us"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="formDescription">Description</Label>
            <Input
              id="formDescription"
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder="Get in touch with us"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="submitButtonText">Submit Button Text</Label>
            <Input
              id="submitButtonText"
              value={submitButtonText}
              onChange={(e) => setSubmitButtonText(e.target.value)}
              placeholder="Submit"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="successMessage">Success Message</Label>
            <Textarea
              id="successMessage"
              value={successMessage}
              onChange={(e) => setSuccessMessage(e.target.value)}
              placeholder="Thank you! We'll be in touch soon."
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="welcomeMessage">Welcome Email Message</Label>
            <Textarea
              id="welcomeMessage"
              value={welcomeMessage}
              onChange={(e) => setWelcomeMessage(e.target.value)}
              placeholder="Thank you for contacting us! We'll get back to you shortly."
              rows={3}
            />
            <p className="text-sm text-muted-foreground">
              This message will be sent automatically when someone submits the form
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Form Fields */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Form Fields</CardTitle>
          <CardDescription>Configure the fields in your contact form</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {fields.map((field, index) => (
            <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{field.label}</span>
                  <span className="text-sm text-muted-foreground">({field.type})</span>
                  {field.required && (
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                      Required
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  Placeholder: {field.placeholder}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => toggleFieldRequired(index)}
              >
                {field.required ? 'Make Optional' : 'Make Required'}
              </Button>
            </div>
          ))}

          <Alert>
            <AlertDescription>
              At least one contact method (email or phone) must be required
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Public URL */}
      {contactForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Public Form URL</CardTitle>
            <CardDescription>Share this URL to receive contact form submissions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <Input
                value={`${window.location.origin}${contactForm.public_url}`}
                readOnly
                className="flex-1"
              />
              <Button variant="outline" size="icon" onClick={handleCopyUrl}>
                <Copy className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={handlePreview}>
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>

            <Alert>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>
                Your contact form is live and ready to receive submissions!
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => navigate('/integration-setup')}>
          Back
        </Button>
        <div className="flex gap-2">
          <Button onClick={handleSaveForm} disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Form'
            )}
          </Button>
          <Button onClick={handleContinue} disabled={!contactForm}>
            Continue to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
