import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Zap, ArrowRight, CheckCircle2, CalendarDays, MessageSquare, FileText, Package, Users, BarChart3 } from "lucide-react";

const features = [
  { icon: CalendarDays, title: "Smart Bookings", description: "Manage appointments with automated confirmations and reminders" },
  { icon: MessageSquare, title: "Unified Inbox", description: "All customer communication in one place — email and SMS" },
  { icon: FileText, title: "Automated Forms", description: "Auto-send intake forms and track completion status" },
  { icon: Package, title: "Inventory Tracking", description: "Monitor stock levels with automated low-stock alerts" },
  { icon: Users, title: "Team Management", description: "Invite staff with role-based access and permissions" },
  { icon: BarChart3, title: "Live Dashboard", description: "Real-time visibility into every aspect of your operations" },
];

export default function Index() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <div className="bg-gradient-hero min-h-[80vh] flex flex-col">
        <header className="flex items-center justify-between px-8 py-5">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
              <Zap className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold text-primary-foreground">CareOps</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/login")}
              className="text-sm font-medium text-primary-foreground/70 hover:text-primary-foreground transition-colors px-4 py-2"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate("/onboarding")}
              className="text-sm font-medium bg-gradient-primary text-primary-foreground px-5 py-2.5 rounded-lg hover:opacity-90 transition-opacity shadow-glow"
            >
              Get Started
            </button>
          </div>
        </header>

        <div className="flex-1 flex items-center justify-center px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-1.5 mb-6">
              <Zap className="w-3.5 h-3.5 text-primary" />
              <span className="text-xs font-medium text-primary">Unified Operations Platform</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-extrabold text-primary-foreground leading-tight tracking-tight">
              One platform to run
              <br />
              <span className="text-gradient">your entire business</span>
            </h1>
            <p className="text-lg text-primary-foreground/60 mt-6 max-w-xl mx-auto leading-relaxed">
              Replace the chaos of disconnected tools. Manage leads, bookings, communications, forms, and inventory — all from one dashboard.
            </p>
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => navigate("/onboarding")}
                className="flex items-center gap-2 bg-gradient-primary text-primary-foreground px-6 py-3 rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity shadow-glow"
              >
                Start Free Setup
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigate("/login")}
                className="flex items-center gap-2 text-primary-foreground/70 hover:text-primary-foreground px-6 py-3 rounded-lg text-sm font-medium border border-primary-foreground/10 hover:border-primary-foreground/20 transition-colors"
              >
                Sign In
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features */}
      <div className="py-24 px-8 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-foreground">Everything you need, nothing you don't</h2>
          <p className="text-muted-foreground mt-3 max-w-lg mx-auto">One system where your business can see, act, and operate clearly.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="bg-card rounded-xl border border-border p-6 hover:shadow-lg hover:border-primary/20 transition-all group"
            >
              <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
                <feature.icon className="w-5 h-5 text-accent-foreground group-hover:text-primary transition-colors" />
              </div>
              <h3 className="text-base font-semibold text-card-foreground">{feature.title}</h3>
              <p className="text-sm text-muted-foreground mt-1.5">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-8">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">CareOps</span>
          </div>
          <p className="text-xs text-muted-foreground">© 2026 CareOps. Unified operations for service businesses.</p>
        </div>
      </footer>
    </div>
  );
}
