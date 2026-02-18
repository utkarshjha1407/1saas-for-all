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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import {
  Plus,
  Trash2,
  GripVertical,
  Type,
  Mail,
  Phone,
  AlignLeft,
  List,
  CheckSquare,
  Circle,
  Calendar,
  Hash,
  Info,
  Eye,
} from 'lucide-react';

const FIELD_TYPES = [
  { value: 'text', label: 'Text', icon: Type },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'phone', label: 'Phone', icon: Phone },
  { value: 'textarea', label: 'Long Text', icon: AlignLeft },
  { value: 'select', label: 'Dropdown', icon: List },
  { value: 'checkbox', label: 'Checkboxes', icon: CheckSquare },
  { value: 'radio', label: 'Radio Buttons', icon: Circle },
  { value: 'date', label: 'Date', icon: Calendar },
  { value: 'number', label: 'Number', icon: Hash },
];

interface FormField {
  id: string;
  type: string;
  label: string;
  required: boolean;
  options?: string[];
  placeholder?: string;
}

export default function FormBuilder() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { createTemplate, isCreatingTemplate } = useForms();
  const { bookingTypes, fetchBookingTypes } = useBookingTypes();

  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [fields, setFields] = useState<FormField[]>([]);
  const [selectedBookingTypes, setSelectedBookingTypes] = useState<string[]>([]);
  const [showPreview, setShowPreview] = useState(false);

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    fetchBookingTypes();
  }, [fetchBookingTypes]);

  const addField = (type: string) => {
    const newField: FormField = {
      id: `field_${Date.now()}`,
      type,
      label: '',
      required: false,
      placeholder: '',
    };

    if (['select', 'checkbox', 'radio'].includes(type)) {
      newField.options = ['Option 1', 'Option 2'];
    }

    setFields([...fields, newField]);
  };

  const updateField = (id: string, updates: Partial<FormField>) => {
    setFields(fields.map((f) => (f.id === id ? { ...f, ...updates } : f)));
  };

  const removeField = (id: string) => {
    setFields(fields.filter((f) => f.id !== id));
  };

  const moveField = (index: number, direction: 'up' | 'down') => {
    const newFields = [...fields];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= fields.length) return;
    [newFields[index], newFields[newIndex]] = [newFields[newIndex], newFields[index]];
    setFields(newFields);
  };

  const handleSave = async () => {
    if (!formName.trim()) {
      toast.error('Please enter a form name');
      return;
    }

    if (fields.length === 0) {
      toast.error('Please add at least one field');
      return;
    }

    // Validate all fields have labels
    const invalidFields = fields.filter((f) => !f.label.trim());
    if (invalidFields.length > 0) {
      toast.error('All fields must have labels');
      return;
    }

    setSaving(true);

    setSaving(true);

    try {
      // Convert fields to API format
      const formFields = fields.map((f) => ({
        name: f.id,
        type: f.type,
        label: f.label,
        required: f.required,
        options: f.options,
        placeholder: f.placeholder,
      }));

      await createTemplate({
        name: formName,
        description: formDescription,
        fields: formFields,
        booking_type_ids: selectedBookingTypes,
      });

      toast.success('Form template created successfully');
      navigate('/inventory-setup'); // Next step
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create form template');
    }
  };

  const handleSkip = () => {
    navigate('/inventory-setup');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Form Templates (View Only)</CardTitle>
            <CardDescription>
              Only workspace owners can create and modify form templates.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Contact your workspace owner to create form templates.
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
        <h1 className="text-3xl font-bold">Step 5: Create Forms</h1>
        <p className="text-muted-foreground mt-2">
          Create custom forms to collect information from clients after booking
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Form Builder */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Form Details</CardTitle>
              <CardDescription>Basic information about your form</CardDescription>
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
                <Label>Link to Booking Types</Label>
                <p className="text-sm text-muted-foreground mb-2">
                  Select which services should send this form
                </p>
                <div className="space-y-2">
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
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Form Fields</CardTitle>
              <CardDescription>Add fields to collect information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-4">
                {fields.map((field, index) => (
                  <FieldEditor
                    key={field.id}
                    field={field}
                    index={index}
                    totalFields={fields.length}
                    onUpdate={(updates) => updateField(field.id, updates)}
                    onRemove={() => removeField(field.id)}
                    onMove={(direction) => moveField(index, direction)}
                  />
                ))}

                {fields.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No fields yet. Add your first field below.</p>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                {FIELD_TYPES.map((type) => {
                  const Icon = type.icon;
                  return (
                    <Button
                      key={type.value}
                      variant="outline"
                      size="sm"
                      onClick={() => addField(type.value)}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {type.label}
                    </Button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        <div className="lg:sticky lg:top-6 lg:self-start">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Preview</CardTitle>
                  <CardDescription>How clients will see your form</CardDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowPreview(!showPreview)}>
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {fields.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p>Add fields to see preview</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg">{formName || 'Form Name'}</h3>
                    {formDescription && (
                      <p className="text-sm text-muted-foreground mt-1">{formDescription}</p>
                    )}
                  </div>

                  <div className="space-y-4">
                    {fields.map((field) => (
                      <FormFieldPreview key={field.id} field={field} />
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between mt-6">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button onClick={handleSave} disabled={isCreatingTemplate}>
          {isCreatingTemplate ? 'Saving...' : 'Save & Continue'}
        </Button>
      </div>
    </div>
  );
}

// Field Editor Component
function FieldEditor({
  field,
  index,
  totalFields,
  onUpdate,
  onRemove,
  onMove,
}: {
  field: FormField;
  index: number;
  totalFields: number;
  onUpdate: (updates: Partial<FormField>) => void;
  onRemove: () => void;
  onMove: (direction: 'up' | 'down') => void;
}) {
  const fieldType = FIELD_TYPES.find((t) => t.value === field.type);
  const Icon = fieldType?.icon || Type;

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          <div className="flex flex-col gap-1 mt-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => onMove('up')}
              disabled={index === 0}
            >
              ↑
            </Button>
            <GripVertical className="h-4 w-4 text-muted-foreground" />
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => onMove('down')}
              disabled={index === totalFields - 1}
            >
              ↓
            </Button>
          </div>

          <div className="flex-1 space-y-3">
            <div className="flex items-center gap-2">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">{fieldType?.label}</span>
            </div>

            <div>
              <Label>Field Label *</Label>
              <Input
                value={field.label}
                onChange={(e) => onUpdate({ label: e.target.value })}
                placeholder="e.g., Full Name"
              />
            </div>

            {!['checkbox', 'radio'].includes(field.type) && (
              <div>
                <Label>Placeholder</Label>
                <Input
                  value={field.placeholder || ''}
                  onChange={(e) => onUpdate({ placeholder: e.target.value })}
                  placeholder="Hint text for the field"
                />
              </div>
            )}

            {['select', 'checkbox', 'radio'].includes(field.type) && (
              <div>
                <Label>Options (one per line)</Label>
                <Textarea
                  value={field.options?.join('\n') || ''}
                  onChange={(e) => onUpdate({ options: e.target.value.split('\n').filter((o) => o.trim()) })}
                  rows={3}
                  placeholder="Option 1&#10;Option 2&#10;Option 3"
                />
              </div>
            )}

            <div className="flex items-center space-x-2">
              <Checkbox
                id={`required-${field.id}`}
                checked={field.required}
                onCheckedChange={(checked) => onUpdate({ required: !!checked })}
              />
              <label
                htmlFor={`required-${field.id}`}
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Required field
              </label>
            </div>
          </div>

          <Button variant="ghost" size="sm" onClick={onRemove}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Form Field Preview Component
function FormFieldPreview({ field }: { field: FormField }) {
  return (
    <div>
      <Label>
        {field.label || 'Field Label'}
        {field.required && <span className="text-destructive ml-1">*</span>}
      </Label>
      {field.type === 'textarea' && (
        <Textarea placeholder={field.placeholder} disabled rows={3} />
      )}
      {field.type === 'select' && (
        <Select disabled>
          <SelectTrigger>
            <SelectValue placeholder="Select an option" />
          </SelectTrigger>
          <SelectContent>
            {field.options?.map((option, i) => (
              <SelectItem key={i} value={option}>
                {option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
      {['text', 'email', 'phone', 'date', 'number'].includes(field.type) && (
        <Input type={field.type} placeholder={field.placeholder} disabled />
      )}
      {field.type === 'checkbox' && (
        <div className="space-y-2">
          {field.options?.map((option, i) => (
            <div key={i} className="flex items-center space-x-2">
              <Checkbox disabled />
              <label className="text-sm">{option}</label>
            </div>
          ))}
        </div>
      )}
      {field.type === 'radio' && (
        <div className="space-y-2">
          {field.options?.map((option, i) => (
            <div key={i} className="flex items-center space-x-2">
              <input type="radio" disabled />
              <label className="text-sm">{option}</label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
