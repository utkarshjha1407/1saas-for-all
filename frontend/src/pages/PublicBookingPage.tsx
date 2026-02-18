import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { bookingTypeService } from '../lib/api/services/bookingType.service';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';
import { Video, Phone, MapPin, User, Calendar, Clock, CheckCircle2, Loader2 } from 'lucide-react';
import type { BookingType } from '../lib/api/types';

const LOCATION_ICONS = {
  video: Video,
  phone: Phone,
  'in-person': MapPin,
  'client-location': User,
};

export default function PublicBookingPage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [bookingTypes, setBookingTypes] = useState<BookingType[]>([]);
  const [selectedType, setSelectedType] = useState<BookingType | null>(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (workspaceId) {
      loadBookingTypes();
    }
  }, [workspaceId]);

  const loadBookingTypes = async () => {
    try {
      const types = await bookingTypeService.getPublic(workspaceId!);
      setBookingTypes(types);
    } catch (error) {
      toast.error('Failed to load booking types');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedType || !selectedDate || !selectedTime) {
      toast.error('Please select a service, date, and time');
      return;
    }

    if (!contactEmail && !contactPhone) {
      toast.error('Please provide either email or phone number');
      return;
    }

    setSubmitting(true);

    try {
      await bookingTypeService.createPublicBooking({
        workspace_id: workspaceId!,
        booking_type_id: selectedType.id,
        booking_date: selectedDate,
        start_time: selectedTime,
        contact_name: contactName,
        contact_email: contactEmail || undefined,
        contact_phone: contactPhone || undefined,
        notes: notes || undefined,
      });

      setSuccess(true);
      toast.success('Booking confirmed!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create booking');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Booking Confirmed!</h2>
            <p className="text-muted-foreground mb-4">
              Your appointment is scheduled for:
            </p>
            <div className="bg-muted p-4 rounded-lg mb-4">
              <p className="font-semibold">{selectedType?.name}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {new Date(selectedDate).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
              <p className="text-sm text-muted-foreground">{selectedTime}</p>
              <p className="text-sm text-muted-foreground mt-2">
                {selectedType?.duration_minutes} minutes • {selectedType?.location_type.replace('-', ' ')}
              </p>
            </div>
            {contactEmail && (
              <p className="text-sm text-muted-foreground">
                A confirmation email has been sent to {contactEmail}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Book an Appointment</h1>
          <p className="text-muted-foreground">Choose a service and time that works for you</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Select Service */}
          <Card>
            <CardHeader>
              <CardTitle>Select Service</CardTitle>
              <CardDescription>Choose the type of appointment you need</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {bookingTypes.map((type) => {
                  const Icon = LOCATION_ICONS[type.location_type as keyof typeof LOCATION_ICONS] || Video;
                  return (
                    <Card
                      key={type.id}
                      className={`cursor-pointer transition-all ${
                        selectedType?.id === type.id
                          ? 'border-primary ring-2 ring-primary'
                          : 'hover:border-primary/50'
                      }`}
                      onClick={() => setSelectedType(type)}
                    >
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                          <Icon className="h-5 w-5 text-primary mt-1" />
                          <div className="flex-1">
                            <h3 className="font-semibold">{type.name}</h3>
                            {type.description && (
                              <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                            )}
                            <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {type.duration_minutes} min
                              </span>
                              <span className="capitalize">{type.location_type.replace('-', ' ')}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Select Date & Time */}
          {selectedType && (
            <Card>
              <CardHeader>
                <CardTitle>Select Date & Time</CardTitle>
                <CardDescription>Choose when you'd like to meet</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="date">Date *</Label>
                    <Input
                      id="date"
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="time">Time *</Label>
                    <Input
                      id="time"
                      type="time"
                      value={selectedTime}
                      onChange={(e) => setSelectedTime(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Contact Information */}
          {selectedType && selectedDate && selectedTime && (
            <Card>
              <CardHeader>
                <CardTitle>Your Information</CardTitle>
                <CardDescription>How should we contact you?</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      value={contactName}
                      onChange={(e) => setContactName(e.target.value)}
                      placeholder="Your full name"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={contactEmail}
                      onChange={(e) => setContactEmail(e.target.value)}
                      placeholder="your@email.com"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={contactPhone}
                      onChange={(e) => setContactPhone(e.target.value)}
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  <div>
                    <Label htmlFor="notes">Notes (Optional)</Label>
                    <Textarea
                      id="notes"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Any additional information..."
                      rows={3}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Submit Button */}
          {selectedType && selectedDate && selectedTime && (
            <div className="flex justify-center">
              <Button type="submit" size="lg" disabled={submitting}>
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Booking...
                  </>
                ) : (
                  <>
                    <Calendar className="h-4 w-4 mr-2" />
                    Confirm Booking
                  </>
                )}
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
