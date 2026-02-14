import { CalendarDays, MessageSquare, FileText, Package, Users, Loader2 } from "lucide-react";
import StatCard from "@/components/StatCard";
import { motion } from "framer-motion";
import { useDashboard } from "@/hooks/useDashboard";
import { useBookings } from "@/hooks/useBookings";

export default function Dashboard() {
  const { stats: dashboardData, isLoading: dashboardLoading } = useDashboard();
  const { bookings: bookingsData, isLoading: bookingsLoading } = useBookings();

  if (dashboardLoading || bookingsLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const stats = dashboardData || {
    bookings: { today_count: 0, upcoming_count: 0, completed_count: 0, no_show_count: 0 },
    leads: { new_inquiries: 0, ongoing_conversations: 0, unanswered_messages: 0 },
    forms: { pending_count: 0, overdue_count: 0, completed_count: 0 },
    inventory: { low_stock_items: 0, critical_items: 0 },
    total_alerts: 0,
    critical_alerts: 0,
    generated_at: new Date().toISOString()
  };
  
  const todayBookings = bookingsData?.filter((b: any) => {
    try {
      const bookingDate = new Date(b.start_time);
      const today = new Date();
      return bookingDate.toDateString() === today.toDateString();
    } catch {
      return false;
    }
  }) || [];

  const statsCards = [
    {
      title: "Today's Bookings",
      value: stats.bookings.today_count || 0,
      change: `${stats.bookings.upcoming_count || 0} upcoming`,
      changeType: "positive" as const,
      icon: CalendarDays,
      iconColor: "bg-primary/10 text-primary"
    },
    {
      title: "New Inquiries",
      value: stats.leads.new_inquiries || 0,
      change: "This week",
      changeType: "positive" as const,
      icon: Users,
      iconColor: "bg-info/10 text-info"
    },
    {
      title: "Pending Forms",
      value: stats.forms.pending_count || 0,
      change: `${stats.forms.overdue_count || 0} overdue`,
      changeType: stats.forms.overdue_count > 0 ? "negative" as const : "positive" as const,
      icon: FileText,
      iconColor: "bg-warning/10 text-warning"
    },
    {
      title: "Unread Messages",
      value: stats.leads.unanswered_messages || 0,
      change: "Needs response",
      changeType: stats.leads.unanswered_messages > 0 ? "negative" as const : "positive" as const,
      icon: MessageSquare,
      iconColor: "bg-destructive/10 text-destructive"
    },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Here's what's happening in your business today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsCards.map((stat, i) => (
          <motion.div key={stat.title} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <StatCard {...stat} />
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1 bg-card rounded-xl border border-border p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-card-foreground">Alerts</h2>
            <span className="text-xs font-medium bg-destructive/10 text-destructive px-2 py-0.5 rounded-full">
              {stats.total_alerts} active
            </span>
          </div>
          <div className="space-y-1">
            {stats.total_alerts > 0 ? (
              <div className="text-sm text-muted-foreground space-y-2">
                {stats.forms.overdue_count > 0 && (
                  <div className="p-2 bg-warning/10 rounded">
                    {stats.forms.overdue_count} overdue forms
                  </div>
                )}
                {stats.inventory.low_stock_items > 0 && (
                  <div className="p-2 bg-warning/10 rounded">
                    {stats.inventory.low_stock_items} low stock items
                  </div>
                )}
                {stats.leads.unanswered_messages > 0 && (
                  <div className="p-2 bg-destructive/10 rounded">
                    {stats.leads.unanswered_messages} unanswered messages
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">No alerts at the moment</p>
            )}
          </div>
        </motion.div>

        {/* Today's Schedule */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="lg:col-span-2 bg-card rounded-xl border border-border p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-card-foreground">Today's Schedule</h2>
            <span className="text-xs text-muted-foreground">{todayBookings.length} appointments</span>
          </div>
          <div className="space-y-2">
            {todayBookings.length > 0 ? (
              todayBookings.map((booking: any, i: number) => {
                const startTime = new Date(booking.start_time);
                const timeStr = startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
                
                return (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors">
                    <span className="text-sm font-mono text-muted-foreground w-20 shrink-0">
                      {timeStr}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-card-foreground">{booking.contact_name || "Unknown"}</p>
                      <p className="text-xs text-muted-foreground">{booking.booking_type_name || "Appointment"}</p>
                    </div>
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                      booking.status === "confirmed"
                        ? "bg-success/10 text-success"
                        : booking.status === "completed"
                        ? "bg-muted text-muted-foreground"
                        : "bg-warning/10 text-warning"
                    }`}>
                      {booking.status}
                    </span>
                  </div>
                );
              })
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">No appointments scheduled for today</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Forms overview */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-card rounded-xl border border-border p-5"
        >
          <h2 className="text-base font-semibold text-card-foreground mb-4">Forms Status</h2>
          <div className="space-y-3">
            {[
              { label: "Completed", count: stats.forms.completed_count || 0, total: (stats.forms.completed_count + stats.forms.pending_count + stats.forms.overdue_count) || 1, color: "bg-success" },
              { label: "Pending", count: stats.forms.pending_count || 0, total: (stats.forms.completed_count + stats.forms.pending_count + stats.forms.overdue_count) || 1, color: "bg-warning" },
              { label: "Overdue", count: stats.forms.overdue_count || 0, total: (stats.forms.completed_count + stats.forms.pending_count + stats.forms.overdue_count) || 1, color: "bg-destructive" },
            ].map((item) => (
              <div key={item.label} className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="text-sm font-medium text-card-foreground">{item.count}</span>
                </div>
                <div className="h-2 rounded-full bg-secondary">
                  <div
                    className={`h-full rounded-full ${item.color} transition-all duration-500`}
                    style={{ width: `${(item.count / item.total) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="bg-card rounded-xl border border-border p-5"
        >
          <h2 className="text-base font-semibold text-card-foreground mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {[
              { label: "New Booking", icon: CalendarDays, link: "/bookings" },
              { label: "View Messages", icon: MessageSquare, link: "/inbox" },
              { label: "Add Contact", icon: Users, link: "/contacts" },
              { label: "Check Inventory", icon: Package, link: "/inventory" },
            ].map((action) => (
              <button
                key={action.label}
                onClick={() => window.location.href = action.link}
                className="w-full flex items-center gap-3 p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors text-left"
              >
                <action.icon className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-medium text-card-foreground">{action.label}</span>
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
