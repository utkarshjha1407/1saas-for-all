import { FileText, CheckCircle2, Clock, AlertTriangle, Send, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useForms } from "@/hooks/useForms";
import { useToast } from "@/hooks/use-toast";

const statusConfig = {
  completed: { icon: CheckCircle2, label: "Completed", className: "bg-success/10 text-success" },
  pending: { icon: Clock, label: "Pending", className: "bg-warning/10 text-warning" },
  in_progress: { icon: Clock, label: "In Progress", className: "bg-blue-500/10 text-blue-500" },
  overdue: { icon: AlertTriangle, label: "Overdue", className: "bg-destructive/10 text-destructive" },
};

export default function Forms() {
  const { submissions, isLoading } = useForms();
  const { toast } = useToast();

  const summaryStats = [
    { label: "Completed", value: submissions?.filter(s => s.status === 'completed').length || 0, color: "bg-success" },
    { label: "Pending", value: submissions?.filter(s => s.status === 'pending').length || 0, color: "bg-warning" },
    { label: "Overdue", value: submissions?.filter(s => s.status === 'overdue').length || 0, color: "bg-destructive" },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Forms</h1>
        <p className="text-sm text-muted-foreground mt-1">Track form submissions and completion status</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        {summaryStats.map((stat) => (
          <div key={stat.label} className="bg-card rounded-xl border border-border p-4 text-center">
            <p className="text-2xl font-bold text-card-foreground">{stat.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Forms list */}
      {!submissions || submissions.length === 0 ? (
        <div className="bg-card rounded-xl border border-border p-12 text-center">
          <p className="text-muted-foreground">No form submissions yet. Forms will appear here when bookings are created.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {submissions.map((submission, i) => {
            const status = statusConfig[submission.status as keyof typeof statusConfig];
            const StatusIcon = status.icon;
            return (
              <motion.div
                key={submission.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="bg-card rounded-xl border border-border p-4 hover:shadow-md transition-shadow flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center">
                    <FileText className="w-5 h-5 text-accent-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-card-foreground">Form Submission</p>
                    <p className="text-xs text-muted-foreground">
                      Created {new Date(submission.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {submission.submitted_at && (
                    <span className="text-xs text-muted-foreground hidden sm:inline">
                      Completed {new Date(submission.submitted_at).toLocaleDateString()}
                    </span>
                  )}
                  <div className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${status.className}`}>
                    <StatusIcon className="w-3 h-3" />
                    {status.label}
                  </div>
                  {submission.public_url && submission.status !== "completed" && (
                    <a
                      href={submission.public_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-lg hover:bg-secondary transition-colors"
                      title="Open form"
                    >
                      <Send className="w-3.5 h-3.5 text-muted-foreground" />
                    </a>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
