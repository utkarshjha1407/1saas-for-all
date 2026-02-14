import { useState } from "react";
import { CalendarDays, Clock, MapPin, Plus, CheckCircle2, XCircle, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useBookings } from "@/hooks/useBookings";

const statusConfig = {
  confirmed: { icon: CheckCircle2, label: "Confirmed", className: "bg-success/10 text-success" },
  pending: { icon: AlertCircle, label: "Pending", className: "bg-warning/10 text-warning" },
  completed: { icon: CheckCircle2, label: "Completed", className: "bg-muted text-muted-foreground" },
  cancelled: { icon: XCircle, label: "Cancelled", className: "bg-destructive/10 text-destructive" },
  "no-show": { icon: XCircle, label: "No Show", className: "bg-destructive/10 text-destructive" },
};

type TabType = "upcoming" | "past" | "all";

export default function Bookings() {
  const [tab, setTab] = useState<TabType>("upcoming");
  const { bookings, isLoading } = useBookings();

  const now = new Date();
  const filteredBookings = bookings?.filter((booking: any) => {
    try {
      const bookingDate = new Date(booking.start_time);
      if (tab === "upcoming") return bookingDate >= now;
      if (tab === "past") return bookingDate < now;
      return true;
    } catch {
      return true;
    }
  }) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Bookings</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage appointments and schedule</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity">
          <Plus className="w-4 h-4" />
          New Booking
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-secondary rounded-lg p-1 w-fit">
        {(["upcoming", "past", "all"] as TabType[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors capitalize ${
              tab === t ? "bg-card text-card-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Bookings list */}
      <div className="space-y-3">
        {filteredBookings.length > 0 ? (
          filteredBookings.map((booking: any, i: number) => {
            const status = statusConfig[booking.status as keyof typeof statusConfig] || statusConfig.pending;
            const StatusIcon = status.icon;
            
            let dateStr = "Unknown date";
            let timeStr = "Unknown time";
            let duration = 0;
            
            try {
              const startTime = new Date(booking.start_time);
              const endTime = new Date(booking.end_time);
              dateStr = startTime.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
              timeStr = startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
              duration = Math.round((endTime.getTime() - startTime.getTime()) / (1000 * 60));
            } catch (e) {
              // Use defaults
            }

            return (
              <motion.div
                key={booking.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="bg-card rounded-xl border border-border p-5 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
                      {booking.contact_name?.split(" ").map((n: string) => n[0]).join("") || "?"}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-card-foreground">{booking.contact_name || "Unknown Contact"}</p>
                      <p className="text-xs text-muted-foreground">{booking.booking_type_name || "Appointment"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right hidden sm:block">
                      <p className="text-sm font-medium text-card-foreground flex items-center gap-1.5">
                        <CalendarDays className="w-3.5 h-3.5 text-muted-foreground" />
                        {dateStr}
                      </p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {timeStr} · {duration} min
                      </p>
                    </div>
                    {booking.location && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground hidden md:flex">
                        <MapPin className="w-3 h-3" />
                        {booking.location}
                      </div>
                    )}
                    <div className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${status.className}`}>
                      <StatusIcon className="w-3 h-3" />
                      {status.label}
                    </div>
                    {booking.notes && (
                      <span className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-0.5 rounded-full hidden lg:inline">
                        Has notes
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })
        ) : (
          <div className="text-center py-12">
            <CalendarDays className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm text-muted-foreground">No bookings found</p>
          </div>
        )}
      </div>
    </div>
  );
}
