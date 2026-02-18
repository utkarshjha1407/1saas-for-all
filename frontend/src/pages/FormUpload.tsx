import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useForms } from '../hooks/useForms';
import { useBookingTypes } from '../hooks/useBookingTypes';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  Upload,
  FileText,
  Trash2,
  Info,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';

export default function FormUpload() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { templates, createTemplate, isCreatingTemplate, fetchTemplates, deleteTemplate } = useForms();
  const { bookingTypes, fetchBookingTypes } = useBookingTypes();

  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState('');
  const [selectedBookingTypes, setSelectedBookingTypes] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    fetchBookingTypes();
    fetchTemplates();
  }, [fetchBookingTypes, fetchTemplates]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Please upload a PDF or Word document');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!formName.trim()) {
      toast.error('Please enter a form name');
      return;
    }

    if (!selectedFile && !fileUrl) {
      toast.error('Please select a file or enter a file URL');
      return;
    }

    if (selectedBookingTypes.length === 0) {
      toast.error('Please select at least one booking type');
      return;
    }

    setIsUploading(true);

    try {
      let uploadedFileUrl = fileUrl;

      // If file is selected, upload it
      if (selectedFile) {
        // In a real implementation, you would upload to a storage service (S3, Supabase Storage, etc.)
        // For now, we'll use a placeholder URL
        // TODO: Implement actual file upload to storage
        uploadedFileUrl = `https://storage.example.com/forms/${Date.now()}_${selectedFile.name}`;
        toast.info('Note: File upload to storage not yet implemented. Using placeholder URL.');
      }

      const fileType = selectedFile?.type.includes('pdf') ? 'pdf' : 
                      selectedFile?.type.includes('word') ? 'docx' : 'doc';

      await createTemplate({
        name: formName,
        description: formDescription,
        file_url: uploadedFileUrl,
        file_type: fileType,
        file_size: selectedFile?.size,
        booking_type_ids: selectedBookingTypes,
      });

      toast.success('Form uploaded successfully');
      
      // Reset form
      setFormName('');
      setFormDescription('');
      setSelectedFile(null);
      setFileUrl('');
      setSelectedBookingTypes([]);
      
      // Refresh templates
      fetchTemplates();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to upload form');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this form?')) {
      return;
    }

    try {
      await deleteTemplate(templateId);
      toast.success('Form deleted successfully');
      fetchTemplates();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete form');
    }
  };

  const handleSkip = () => {
    navigate('/inventory-setup');
  };

  const handleContinue = () => {
    navigate('/inventory-setup');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Form Management (View Only)</CardTitle>
            <CardDescription>
              Only workspace owners can upload and manage forms.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Contact your workspace owner to upload forms.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Step 5: Upload Forms</h1>
        <p className="text-muted-foreground mt-2">
          Upload forms (PDFs, documents) that will be sent to clients after booking
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Form */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload New Form</CardTitle>
              <CardDescription>
                Upload intake forms, agreements, or supporting documents
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">Form Name *</Label>
                <Input
                  id="name"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="e.g., Patient Intake Form"
                  maxLength={100}
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Brief description of this form"
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="file">Upload File *</Label>
                <div className="mt-2">
                  <input
                    id="file"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-500
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-md file:border-0
                      file:text-sm file:font-semibold
                      file:bg-primary file:text-primary-foreground
                      hover:file:bg-primary/90
                      cursor-pointer"
                  />
                  {selectedFile && (
                    <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>{selectedFile.name}</span>
                      <span>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Accepted formats: PDF, DOC, DOCX (max 10MB)
                </p>
              </div>

              <div className="text-center text-sm text-muted-foreground">OR</div>

              <div>
                <Label htmlFor="fileUrl">File URL</Label>
                <Input
                  id="fileUrl"
                  value={fileUrl}
                  onChange={(e) => setFileUrl(e.target.value)}
                  placeholder="https://example.com/form.pdf"
                  disabled={!!selectedFile}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Enter a URL if the file is already hosted elsewhere
                </p>
              </div>

              <div>
                <Label>Link to Booking Types *</Label>
                <p className="text-sm text-muted-foreground mb-2">
                  Select which services should send this form
                </p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {bookingTypes.map((type) => (
                    <div key={type.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={type.id}
                        checked={selectedBookingTypes.includes(type.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedBookingTypes([...selectedBookingTypes, type.id]);
                          } else {
                            setSelectedBookingTypes(selectedBookingTypes.filter((id) => id !== type.id));
                          }
                        }}
                      />
                      <label
                        htmlFor={type.id}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {type.name}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleUpload}
                disabled={isUploading || isCreatingTemplate}
                className="w-full"
              >
                <Upload className="h-4 w-4 mr-2" />
                {isUploading || isCreatingTemplate ? 'Uploading...' : 'Upload Form'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Uploaded Forms List */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Forms</CardTitle>
              <CardDescription>
                Forms that will be sent automatically after booking
              </CardDescription>
            </CardHeader>
            <CardContent>
              {templates.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No forms uploaded yet</p>
                  <p className="text-sm mt-1">Upload your first form to get started</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {templates.map((template) => (
                    <Card key={template.id}>
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <FileText className="h-4 w-4 text-primary" />
                              <h4 className="font-semibold">{template.name}</h4>
                            </div>
                            {template.description && (
                              <p className="text-sm text-muted-foreground mt-1">
                                {template.description}
                              </p>
                            )}
                            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                              <span className="uppercase">{template.file_type}</span>
                              {template.file_size && (
                                <span>{(template.file_size / 1024).toFixed(1)} KB</span>
                              )}
                            </div>
                            <div className="mt-2">
                              <p className="text-xs text-muted-foreground">Linked to:</p>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {template.booking_type_ids.map((btId) => {
                                  const bt = bookingTypes.find((t) => t.id === btId);
                                  return bt ? (
                                    <span
                                      key={btId}
                                      className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-primary/10 text-primary"
                                    >
                                      {bt.name}
                                    </span>
                                  ) : null;
                                })}
                              </div>
                            </div>
                            <a
                              href={template.file_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-2"
                            >
                              <ExternalLink className="h-3 w-3" />
                              View File
                            </a>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(template.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {templates.length > 0 && (
            <Alert className="mt-4">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                These forms will be automatically sent to clients after they book an appointment
                for the linked services.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between mt-6">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button onClick={handleContinue}>
          Continue to Inventory Setup
        </Button>
      </div>
    </div>
  );
}
