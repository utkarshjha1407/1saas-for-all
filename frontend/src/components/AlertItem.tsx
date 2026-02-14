import { AlertTriangle, Clock, MessageSquareWarning, Package } from "lucide-react";
import { Link } from "react-router-dom";

type AlertType = "missed_message" | "unconfirmed_booking" | "overdue_form" | "low_inventory";

interface AlertItemProps {
  type: AlertType;
  title: string;
  description: string;
  time: string;
  link: string;
}

const alertConfig: Record<AlertType, { icon: typeof AlertTriangle; color: string }> = {
  missed_message: { icon: MessageSquareWarning, color: "text-destructive bg-destructive/10" },
  unconfirmed_booking: { icon: Clock, color: "text-warning bg-warning/10" },
  overdue_form: { icon: AlertTriangle, color: "text-warning bg-warning/10" },
  low_inventory: { icon: Package, color: "text-info bg-info/10" },
};

export default function AlertItem({ type, title, description, time, link }: AlertItemProps) {
  const config = alertConfig[type];
  const Icon = config.icon;

  return (
    <Link to={link} className="flex items-start gap-3 p-3 rounded-lg hover:bg-secondary/50 transition-colors group">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${config.color}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-card-foreground group-hover:text-primary transition-colors">{title}</p>
        <p className="text-xs text-muted-foreground mt-0.5 truncate">{description}</p>
      </div>
      <span className="text-xs text-muted-foreground shrink-0">{time}</span>
    </Link>
  );
}
