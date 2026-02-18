import { CalendarDays, MessageSquare, FileText, Package, AlertTriangle, CheckCircle2, XCircle, Clock, Loader2, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useDashboard } from "@/hooks/useDashboard";
import { useBookings } from "@/hooks/useBookings";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
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

  const unconfirmedBookings = todayBookings.filter((b: any) => b.status === "pending");

  // Build actionable alerts
  const alerts = [
    ...(stats.leads.unanswered_messages > 0 ? [{
      id: 'unanswered-messages',
      type: 'critical' as const,
      icon: MessageSquare,
      title: 'Unanswered Messages',
      count: stats.leads.unanswered_messages,
      description: `${stats.leads.unanswered_messages} message${stats.leads.unanswered_messages > 1 ? 's' : ''} waiting for response`,
      action: 'View Inbox',
      link: '/inbox'
    }] : []),
    ...(unconfirmedBookings.length > 0 ? [{
      id: 'unconfirmed-bookings',
      type: 'warning' as const,
      icon: Clock,
      title: 'Unconfirmed Bookings',
      count: unconfirmedBookings.length,
      description: `${unconfirmedBookings.length} booking${unconfirmedBookings.length > 1 ? 's' : ''} need confirmation`,
      action: 'View Bookings',
      link: '/bookings'
    }] : []),
    ...(stats.forms.overdue_count > 0 ? [{
      id: 'overdue-forms',
      type: 'warning' as const,
      icon: FileText,
      title: 'Overdue Forms',
      count: stats.forms.overdue_count,
      description: `${stats.forms.overdue_count} form${stats.forms.overdue_count > 1 ? 's' : ''} past due date`,
      action: 'View Forms',
      link: '/forms'
    }] : []),
    ...(stats.inventory.critical_items > 0 ? [{
      id: 'critical-inventory',
      type: 'critical' as const,
      icon: AlertTriangle,
      title: 'Critical Inventory',
      count: stats.inventory.critical_items,
      description: `${stats.inventory.critical_items} item${stats.inventory.critical_items > 1 ? 's' : ''} out of stock`,
      action: 'View Inventory',
      link: '/inventory'
    }] : []),
    ...(stats.inventory.low_stock_items > 0 && stats.inventory.critical_items === 0 ? [{
      id: 'low-stock',
      type: 'info' as const,
      icon: Package,
      title: 'Low Stock Items',
      count: stats.inventory.low_stock_items,
      description: `${stats.inventory.low_stock_items} item${stats.inventory.low_stock_items > 1 ? 's' : ''} running low`,
      action: 'View Inventory',
      link: '/inventory'
    }] : []),
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">What's Happening Right Now</h1>
        <p className="text-sm text-muted-foreground mt-1">Your business at a glance</p>
      </div>

      {/* Critical Alerts Section */}
      {alerts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-destructive/5 border-2 border-destructive/20 rounded-xl p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-destructive" />
            <h2 className="text-lg font-semibold text-destructive">Action Required</h2>
            <span className="ml-auto text-sm font-medium text-destructive">{alerts.length} alert{alerts.length > 1 ? 's' : ''}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {alerts.map((alert) => (
              <button
                key={alert.id}
                onClick={() => navigate(alert.link)}
                className={`flex items-start gap-3 p-4 rounded-lg text-left transition-all hover:scale-[1.02] ${
                  alert.type === 'critical' 
                    ? 'bg-destructive/10 hover:bg-destructive/20 border border-destructive/30' 
                    : alert.type === 'warning'
                    ? 'bg-warning/10 hover:bg-warning/20 border border-warning/30'
                    : 'bg-info/10 hover:bg-info/20 border border-info/30'
                }`}
              >
                <alert.icon className={`w-5 h-5 mt-0.5 shrink-0 ${
                  alert.type === 'critical' ? 'text-destructive' : alert.type === 'warning' ? 'text-warning' : 'text-info'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-sm text-foreground">{alert.title}</h3>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      alert.type === 'critical' ? 'bg-destructive text-destructive-foreground' : 
                      alert.type === 'warning' ? 'bg-warning text-warning-foreground' : 
                      'bg-info text-info-foreground'
                    }`}>
                      {alert.count}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">{alert.description}</p>
                  <div className="flex items-center gap-1 text-xs font-medium text-primary">
                    {alert.action} <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Booking Overview */}
        <motion.button
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onClick={() => navigate('/bookings')}
          className="bg-card rounded-xl border border-border p-5 text-left hover:border-primary/50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <CalendarDays className="w-5 h-5 text-primary" />
            <span className="text-2xl font-bold text-foreground">{stats.bookings.today_count}</span>
          </div>
          <h3 className="text-sm font-semibold text-foreground mb-2">Today's Bookings</h3>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Upcoming</span>
              <span className="font-medium">{stats.bookings.upcoming_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Completed</span>
              <span className="font-medium text-success">{stats.bookings.completed_count}</span>
            </div>
            <div className="flex justify-between">
              <span>No-shows</span>
              <span className="font-medium text-destructive">{stats.bookings.no_show_count}</span>
            </div>
          </div>
        </motion.button>

        {/* Leads & Conversations */}
        <motion.button
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          onClick={() => navigate('/inbox')}
          className="bg-card rounded-xl border border-border p-5 text-left hover:border-primary/50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <MessageSquare className="w-5 h-5 text-info" />
            <span className="text-2xl font-bold text-foreground">{stats.leads.new_inquiries}</span>
          </div>
          <h3 className="text-sm font-semibold text-foreground mb-2">Leads & Conversations</h3>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>New inquiries</span>
              <span className="font-medium">{stats.leads.new_inquiries}</span>
            </div>
            <div className="flex justify-between">
              <span>Ongoing</span>
              <span className="font-medium">{stats.leads.ongoing_conversations}</span>
            </div>
            <div className="flex justify-between">
              <span>Unanswered</span>
              <span className={`font-medium ${stats.leads.unanswered_messages > 0 ? 'text-destructive' : ''}`}>
                {stats.leads.unanswered_messages}
              </span>
            </div>
          </div>
        </motion.button>

        {/* Forms Status */}
        <motion.button
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          onClick={() => navigate('/forms')}
          className="bg-card rounded-xl border border-border p-5 text-left hover:border-primary/50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <FileText className="w-5 h-5 text-warning" />
            <span className="text-2xl font-bold text-foreground">{stats.forms.pending_count}</span>
          </div>
          <h3 className="text-sm font-semibold text-foreground mb-2">Forms Status</h3>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Pending</span>
              <span className="font-medium">{stats.forms.pending_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Overdue</span>
              <span className={`font-medium ${stats.forms.overdue_count > 0 ? 'text-destructive' : ''}`}>
                {stats.forms.overdue_count}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Completed</span>
              <span className="font-medium text-success">{stats.forms.completed_count}</span>
            </div>
          </div>
        </motion.button>

        {/* Inventory Alerts */}
        <motion.button
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          onClick={() => navigate('/inventory')}
          className="bg-card rounded-xl border border-border p-5 text-left hover:border-primary/50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <Package className="w-5 h-5 text-warning" />
            <span className="text-2xl font-bold text-foreground">{stats.inventory.low_stock_items}</span>
          </div>
          <h3 className="text-sm font-semibold text-foreground mb-2">Inventory Alerts</h3>
          <div className="space-y-1 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>Low stock</span>
              <span className="font-medium text-warning">{stats.inventory.low_stock_items}</span>
            </div>
            <div className="flex justify-between">
              <span>Critical</span>
              <span className={`font-medium ${stats.inventory.critical_items > 0 ? 'text-destructive' : ''}`}>
                {stats.inventory.critical_items}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Action needed</span>
              <span className="font-medium">{stats.inventory.low_stock_items + stats.inventory.critical_items}</span>
            </div>
          </div>
        </motion.button>
      </div>

      {/* Today's Schedule */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-card rounded-xl border border-border p-5"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-card-foreground">Today's Schedule</h2>
          <span className="text-xs text-muted-foreground">{todayBookings.length} appointment{todayBookings.length !== 1 ? 's' : ''}</span>
        </div>
        <div className="space-y-2">
          {todayBookings.length > 0 ? (
            todayBookings.slice(0, 5).map((booking: any, i: number) => {
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
                  {booking.status === "confirmed" && <CheckCircle2 className="w-4 h-4 text-success" />}
                  {booking.status === "pending" && <Clock className="w-4 h-4 text-warning" />}
                  {booking.status === "completed" && <CheckCircle2 className="w-4 h-4 text-muted-foreground" />}
                  {booking.status === "no_show" && <XCircle className="w-4 h-4 text-destructive" />}
                </div>
              );
            })
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">No appointments scheduled for today</p>
          )}
          {todayBookings.length > 5 && (
            <button
              onClick={() => navigate('/bookings')}
              className="w-full text-sm text-primary hover:underline py-2"
            >
              View all {todayBookings.length} bookings
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}
