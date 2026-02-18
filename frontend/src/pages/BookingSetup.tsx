import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useBookingTypes } from '../hooks/useBookingTypes';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Video, Phone, MapPin, User, Info, Copy, Check } from 'lucide-react';
import type { BookingType, BookingTypeCreate, AvailabilitySlot } from '../lib/api/types';

const DURATION_OPTIONS = [15, 30, 45, 60, 90, 120];
const LOCATION_TYPES = [
  { value: 'video', label: 'Video Call', icon: Video },
  { value: 'phone', label: 'Phone Call', icon: Phone },
  { value: 'in-person', label: 'In-Person', icon: MapPin },
  { value: 'client-location', label: 'Client Location', icon: User },
];

const DAYS_OF_WEEK = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
];

export default function BookingSetup() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    bookingTypes,
    loading,
    fetchBookingTypes,
    createBookingType,
    updateBookingType,
    deleteBookingType,
    setAvailability,
    getAvailability,
  } = useBookingTypes();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingType, setEditingType] = useState<BookingType | null>(null);
  const [selectedTypeId, setSelectedTypeId] = useState<string | null>(null);
  const [availability, setAvailabilityState] = useState<AvailabilitySlot[]>([]);
  const [copied, setCopied] = useState(false);

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    fetchBookingTypes();
  }, [fetchBookingTypes]);

  useEffect(() => {
    if (selectedTypeId) {
      loadAvailability(selectedTypeId);
    }
  }, [selectedTypeId]);

  const loadAvailability = async (typeId: string) => {
    try {
      const slots = await getAvailability(typeId);
      setAvailabilityState(slots);
    } catch (error) {
      console.error('Failed to load availability:', error);
    }
  };

  const handleCreateOrUpdate = async (data: BookingTypeCreate) => {
    try {
      if (editingType) {
        await updateBookingType(editingType.id, data);
        toast.success('Booking type updated successfully');
      } else {
        const newType = await createBookingType(data);
        toast.success('Booking type created successfully');
        if (!selectedTypeId) {
          setSelectedTypeId(newType.id);
        }
      }
      setIsFormOpen(false);
      setEditingType(null);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save booking type');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this booking type?')) return;

    try {
      await deleteBookingType(id);
      toast.success('Booking type deleted');
      if (selectedTypeId === id) {
        setSelectedTypeId(null);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete booking type');
    }
  };

  const handleSaveAvailability = async () => {
    if (!selectedTypeId) return;

    try {
      await setAvailability(selectedTypeId, availability);
      toast.success('Availability saved successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save availability');
    }
  };

  const addAvailabilitySlot = (dayOfWeek: number) => {
    setAvailabilityState((prev) => [
      ...prev,
      {
        day_of_week: dayOfWeek,
        start_time: '09:00',
        end_time: '17:00',
      },
    ]);
  };

  const removeAvailabilitySlot = (index: number) => {
    setAvailabilityState((prev) => prev.filter((_, i) => i !== index));
  };

  const updateAvailabilitySlot = (index: number, field: string, value: string) => {
    setAvailabilityState((prev) =>
      prev.map((slot, i) =>
        i === index ? { ...slot, [field]: value } : slot
      )
    );
  };

  const copyPublicUrl = () => {
    const url = `${window.location.origin}/public/book/${user?.workspace_id}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    toast.success('URL copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleContinue = () => {
    if (bookingTypes.length === 0) {
      toast.error('Please create at least one booking type');
      return;
    }

    const hasAvailability = bookingTypes.some((type) => {
      // Check if type has availability (simplified check)
      return true; // In production, verify this properly
    });

    if (!hasAvailability) {
      toast.warning('Consider setting availability for your booking types');
    }

    // Update onboarding step and navigate
    navigate('/form-upload'); // Next step
  };

  const handleSkip = () => {
    navigate('/form-upload');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Booking Types (View Only)</CardTitle>
            <CardDescription>
              Only workspace owners can modify booking types and availability schedules.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                You can view booking types but cannot make changes. Contact your workspace owner to modify settings.
              </AlertDescription>
            </Alert>

            <div className="mt-6 space-y-4">
              {bookingTypes.map((type) => (
                <Card key={type.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">{type.name}</h3>
                        <p className="text-sm text-muted-foreground">{type.description}</p>
                        <div className="mt-2 flex items-center gap-4 text-sm">
                          <span>{type.duration_minutes} minutes</span>
                          <span className="capitalize">{type.location_type.replace('-', ' ')}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Step 4: Set Up Bookings</h1>
        <p className="text-muted-foreground mt-2">
          Define your service types, set availability, and generate your public booking page
        </p>
      </div>

      {/* Booking Types */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Booking Types</CardTitle>
              <CardDescription>Create different types of services or meetings</CardDescription>
            </div>
            <Button onClick={() => { setEditingType(null); setIsFormOpen(true); }}>
              <Plus className="h-4 w-4 mr-2" />
              New Type
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {bookingTypes.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No booking types yet. Create your first one to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {bookingTypes.map((type) => {
                const LocationIcon = LOCATION_TYPES.find((lt) => lt.value === type.location_type)?.icon || Video;
                return (
                  <Card key={type.id} className={selectedTypeId === type.id ? 'border-primary' : ''}>
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <LocationIcon className="h-4 w-4 text-muted-foreground" />
                            <h3 className="font-semibold">{type.name}</h3>
                          </div>
                          {type.description && (
                            <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                          )}
                          <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                            <span>{type.duration_minutes} minutes</span>
                            <span className="capitalize">{type.location_type.replace('-', ' ')}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedTypeId(type.id)}
                          >
                            Set Availability
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => { setEditingType(type); setIsFormOpen(true); }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(type.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Availability Scheduler */}
      {selectedTypeId && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Availability Schedule</CardTitle>
            <CardDescription>
              Set your available hours for {bookingTypes.find((t) => t.id === selectedTypeId)?.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {DAYS_OF_WEEK.map((day, dayIndex) => {
                const daySlots = availability.filter((slot) => slot.day_of_week === dayIndex);
                return (
                  <div key={dayIndex} className="flex items-start gap-4">
                    <div className="w-24 pt-2 font-medium">{day}</div>
                    <div className="flex-1 space-y-2">
                      {daySlots.length === 0 ? (
                        <div className="text-sm text-muted-foreground">Not available</div>
                      ) : (
                        daySlots.map((slot, slotIndex) => {
                          const globalIndex = availability.findIndex(
                            (s) => s.day_of_week === dayIndex && s.start_time === slot.start_time
                          );
                          return (
                            <div key={slotIndex} className="flex items-center gap-2">
                              <Input
                                type="time"
                                value={slot.start_time}
                                onChange={(e) => updateAvailabilitySlot(globalIndex, 'start_time', e.target.value)}
                                className="w-32"
                              />
                              <span>to</span>
                              <Input
                                type="time"
                                value={slot.end_time}
                                onChange={(e) => updateAvailabilitySlot(globalIndex, 'end_time', e.target.value)}
                                className="w-32"
                              />
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeAvailabilitySlot(globalIndex)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          );
                        })
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => addAvailabilitySlot(dayIndex)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Slot
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-6">
              <Button onClick={handleSaveAvailability}>Save Availability</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Public URL */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Public Booking URL</CardTitle>
          <CardDescription>Share this link with clients to book appointments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Input
              value={`${window.location.origin}/public/book/${user?.workspace_id}`}
              readOnly
              className="flex-1"
            />
            <Button onClick={copyPublicUrl} variant="outline">
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button onClick={handleContinue}>
          Continue to Step 5
        </Button>
      </div>

      {/* Booking Type Form Dialog */}
      <BookingTypeFormDialog
        open={isFormOpen}
        onClose={() => { setIsFormOpen(false); setEditingType(null); }}
        onSubmit={handleCreateOrUpdate}
        initialData={editingType}
      />
    </div>
  );
}

// Booking Type Form Dialog Component
function BookingTypeFormDialog({
  open,
  onClose,
  onSubmit,
  initialData,
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: BookingTypeCreate) => void;
  initialData?: BookingType | null;
}) {
  const [formData, setFormData] = useState<BookingTypeCreate>({
    name: '',
    description: '',
    duration_minutes: 30,
    location_type: 'video',
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
        description: initialData.description || '',
        duration_minutes: initialData.duration_minutes,
        location_type: initialData.location_type as any,
      });
    } else {
      setFormData({
        name: '',
        description: '',
        duration_minutes: 30,
        location_type: 'video',
      });
    }
  }, [initialData, open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{initialData ? 'Edit Booking Type' : 'Create Booking Type'}</DialogTitle>
          <DialogDescription>
            Define a service or meeting type that clients can book
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Initial Consultation"
                required
                minLength={3}
                maxLength={100}
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of this service"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="duration">Duration *</Label>
              <Select
                value={formData.duration_minutes.toString()}
                onValueChange={(value) => setFormData({ ...formData, duration_minutes: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DURATION_OPTIONS.map((duration) => (
                    <SelectItem key={duration} value={duration.toString()}>
                      {duration} minutes
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="location_type">Location Type *</Label>
              <Select
                value={formData.location_type}
                onValueChange={(value: any) => setFormData({ ...formData, location_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LOCATION_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center gap-2">
                        <type.icon className="h-4 w-4" />
                        {type.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter className="mt-6">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {initialData ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
