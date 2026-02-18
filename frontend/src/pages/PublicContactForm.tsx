import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, Loader2, Mail } from 'lucide-react';
import apiClient from '@/lib/api/client';

interface FormField {
  name: string;
  type: string;
  label: string;
  placeholder: string;
  required: boolean;
  order: number;
}

interface FormConfig {
  name: string;
  description: string;
  fields: FormField[];
  submit_button_text: string;
  success_message: string;
}

interface WorkspaceInfo {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color?: string;
}

export default function PublicContactForm() {
  const { slug } = useParams<{ slug: string }>();
  const [workspace, setWorkspace] = useState<WorkspaceInfo | null>(null);
  const [formConfig, setFormConfig] = useState<FormConfig | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFormConfig();
  }, [slug]);

  const loadFormConfig = async () => {
    try {
      setIsLoading(true);
      
      // Get workspace info
      const workspaceResponse = await apiClient.get(`/public/${slug}`);
      setWorkspace(workspaceResponse.data);

      // Get form config
      const formResponse = await apiClient.get(`/public/${slug}/public-form`);
      setFormConfig(formResponse.data);

      // Initialize form data
      const initialData: Record<string, string> = {};
      formResponse.data.fields.forEach((field: FormField) => {
        initialData[field.name] = '';
      });
      setFormData(initialData);
    } catch (err: any) {
      setError('Failed to load contact form');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate required fields
    if (formConfig) {
      for (const field of formConfig.fields) {
        if (field.required && !formData[field.name]?.trim()) {
          setError(`${field.label} is required`);
          return;
        }
      }
    }

    try {
      setIsSubmitting(true);

      await apiClient.post(`/public/${slug}/contact`, {
        name: formData.name,
        email: formData.email || null,
        phone: formData.phone || null,
        message: formData.message || null,
      });

      setIsSubmitted(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit form');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error && !formConfig) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-12 px-4">
      <div className="container max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          {workspace?.logo_url && (
            <img
              src={workspace.logo_url}
              alt={workspace.name}
              className="h-16 mx-auto mb-4"
            />
          )}
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {workspace?.name || 'Contact Us'}
          </h1>
        </div>

        {/* Form Card */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl">{formConfig?.name}</CardTitle>
            <CardDescription className="text-base">
              {formConfig?.description}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isSubmitted ? (
              <Alert className="bg-green-50 border-green-200">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <AlertDescription className="text-green-800 text-base">
                  {formConfig?.success_message}
                </AlertDescription>
              </Alert>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {formConfig?.fields
                  .sort((a, b) => a.order - b.order)
                  .map((field) => (
                    <div key={field.name} className="space-y-2">
                      <Label htmlFor={field.name} className="text-base">
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </Label>
                      {field.type === 'textarea' ? (
                        <Textarea
                          id={field.name}
                          placeholder={field.placeholder}
                          value={formData[field.name] || ''}
                          onChange={(e) => handleChange(field.name, e.target.value)}
                          required={field.required}
                          rows={4}
                          className="text-base"
                        />
                      ) : (
                        <Input
                          id={field.name}
                          type={field.type}
                          placeholder={field.placeholder}
                          value={formData[field.name] || ''}
                          onChange={(e) => handleChange(field.name, e.target.value)}
                          required={field.required}
                          className="text-base"
                        />
                      )}
                    </div>
                  ))}

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full text-base py-6"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-5 w-5" />
                      {formConfig?.submit_button_text}
                    </>
                  )}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-600">
          <p>Powered by CareOps</p>
        </div>
      </div>
    </div>
  );
}
