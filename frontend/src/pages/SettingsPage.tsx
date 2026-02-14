import { useState } from "react";
import { Building2, Mail, Phone, Clock, Users, Bell, Link2, Shield } from "lucide-react";

const tabs = [
  { id: "business", label: "Business", icon: Building2 },
  { id: "integrations", label: "Integrations", icon: Link2 },
  { id: "team", label: "Team", icon: Users },
  { id: "notifications", label: "Notifications", icon: Bell },
];

const teamMembers = [
  { name: "John Doe", email: "john@careops.com", role: "Owner", status: "active" },
  { name: "Jane Smith", email: "jane@careops.com", role: "Staff", status: "active" },
  { name: "Mike Johnson", email: "mike@careops.com", role: "Staff", status: "invited" },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("business");

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your workspace configuration</p>
      </div>

      <div className="flex gap-6">
        {/* Tab nav */}
        <nav className="w-48 shrink-0 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2.5 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Content */}
        <div className="flex-1">
          {activeTab === "business" && (
            <div className="bg-card rounded-xl border border-border p-6 space-y-5">
              <h2 className="text-lg font-semibold text-card-foreground">Business Information</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-card-foreground">Business Name</label>
                  <input type="text" defaultValue="CareOps Demo" className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-card-foreground">Contact Email</label>
                  <input type="email" defaultValue="hello@careops.com" className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-card-foreground">Address</label>
                  <input type="text" defaultValue="123 Main St, Suite 100" className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-card-foreground">Time Zone</label>
                  <select className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
                    <option>America/New_York (EST)</option>
                    <option>America/Chicago (CST)</option>
                    <option>America/Los_Angeles (PST)</option>
                  </select>
                </div>
              </div>
              <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity">
                Save Changes
              </button>
            </div>
          )}

          {activeTab === "integrations" && (
            <div className="space-y-4">
              {[
                { name: "Email (SendGrid)", status: "connected", icon: Mail },
                { name: "SMS (Twilio)", status: "connected", icon: Phone },
                { name: "Calendar (Google)", status: "not connected", icon: Clock },
              ].map((integration) => (
                <div key={integration.name} className="bg-card rounded-xl border border-border p-5 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center">
                      <integration.icon className="w-5 h-5 text-accent-foreground" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-card-foreground">{integration.name}</p>
                      <p className={`text-xs font-medium ${integration.status === "connected" ? "text-success" : "text-muted-foreground"}`}>
                        {integration.status === "connected" ? "✓ Connected" : "Not connected"}
                      </p>
                    </div>
                  </div>
                  <button className={`text-sm font-medium px-4 py-2 rounded-lg transition-colors ${
                    integration.status === "connected"
                      ? "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                      : "bg-primary text-primary-foreground hover:opacity-90"
                  }`}>
                    {integration.status === "connected" ? "Configure" : "Connect"}
                  </button>
                </div>
              ))}
            </div>
          )}

          {activeTab === "team" && (
            <div className="bg-card rounded-xl border border-border p-6 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-card-foreground">Team Members</h2>
                <button className="text-sm font-medium px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity">
                  Invite Member
                </button>
              </div>
              <div className="space-y-3">
                {teamMembers.map((member) => (
                  <div key={member.email} className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
                        {member.name.split(" ").map(n => n[0]).join("")}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-card-foreground">{member.name}</p>
                        <p className="text-xs text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        member.role === "Owner" ? "bg-primary/10 text-primary" : "bg-secondary text-secondary-foreground"
                      }`}>
                        {member.role}
                      </span>
                      <span className={`text-xs ${member.status === "active" ? "text-success" : "text-warning"}`}>
                        {member.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="bg-card rounded-xl border border-border p-6 space-y-5">
              <h2 className="text-lg font-semibold text-card-foreground">Notification Preferences</h2>
              {[
                { label: "New lead inquiry", description: "When a customer submits the contact form", enabled: true },
                { label: "Booking confirmation", description: "When a booking is created or confirmed", enabled: true },
                { label: "Form overdue", description: "When a required form passes its deadline", enabled: true },
                { label: "Low inventory alert", description: "When stock drops below threshold", enabled: false },
                { label: "Missed message", description: "When a message goes unanswered for 30min", enabled: true },
              ].map((pref) => (
                <div key={pref.label} className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-card-foreground">{pref.label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{pref.description}</p>
                  </div>
                  <button className={`w-11 h-6 rounded-full transition-colors relative ${pref.enabled ? "bg-primary" : "bg-muted"}`}>
                    <span className={`w-5 h-5 rounded-full bg-card absolute top-0.5 transition-transform ${pref.enabled ? "translate-x-5" : "translate-x-0.5"}`} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
