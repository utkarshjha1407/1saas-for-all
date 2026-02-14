import { useState } from "react";
import { Search, Plus, Mail, Phone, MoreHorizontal, Loader2, X } from "lucide-react";
import { motion } from "framer-motion";
import { useContacts } from "@/hooks/useContacts";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Contacts() {
  const { contacts, isLoading, createContact, deleteContact } = useContacts();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
  });

  const handleCreateContact = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createContact(formData);
      toast({
        title: "Contact created",
        description: "New contact has been added successfully.",
      });
      setIsDialogOpen(false);
      setFormData({ name: "", email: "", phone: "" });
    } catch (error: any) {
      toast({
        title: "Failed to create contact",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    }
  };

  const handleDeleteContact = async (id: string, name: string) => {
    if (!confirm(`Delete contact "${name}"?`)) return;
    try {
      await deleteContact(id);
      toast({
        title: "Contact deleted",
        description: "Contact has been removed.",
      });
    } catch (error: any) {
      toast({
        title: "Failed to delete contact",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    }
  };

  const filteredContacts = contacts?.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.phone?.includes(searchQuery)
  ) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Contacts</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {filteredContacts.length} {filteredContacts.length === 1 ? 'contact' : 'contacts'}
          </p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Contact
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Contact</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateContact} className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+1 555-0100"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">Create Contact</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-2 bg-secondary rounded-lg px-3 py-2 max-w-sm">
        <Search className="w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search contacts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground w-full"
        />
        {searchQuery && (
          <button onClick={() => setSearchQuery("")} className="p-1 hover:bg-background rounded">
            <X className="w-3 h-3 text-muted-foreground" />
          </button>
        )}
      </div>

      {filteredContacts.length === 0 ? (
        <div className="bg-card rounded-xl border border-border p-12 text-center">
          <p className="text-muted-foreground">
            {searchQuery ? "No contacts found matching your search." : "No contacts yet. Add your first contact to get started."}
          </p>
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3">Name</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3 hidden md:table-cell">Contact</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3 hidden lg:table-cell">Source</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3 hidden sm:table-cell">Created</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {filteredContacts.map((contact, i) => (
                <motion.tr
                  key={contact.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.03 }}
                  className="border-b border-border/50 hover:bg-secondary/30 transition-colors cursor-pointer"
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
                        {contact.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
                      </div>
                      <span className="text-sm font-medium text-card-foreground">{contact.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 hidden md:table-cell">
                    <div className="space-y-0.5">
                      {contact.email && (
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Mail className="w-3 h-3" />{contact.email}
                        </p>
                      )}
                      {contact.phone && (
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Phone className="w-3 h-3" />{contact.phone}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-4 hidden lg:table-cell">
                    <span className="text-xs font-medium bg-secondary text-secondary-foreground px-2 py-0.5 rounded-full">
                      {contact.source || 'Manual'}
                    </span>
                  </td>
                  <td className="px-5 py-4 hidden sm:table-cell">
                    <span className="text-sm text-muted-foreground">
                      {new Date(contact.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      onClick={() => handleDeleteContact(contact.id, contact.name)}
                      className="p-1 rounded hover:bg-destructive/10 hover:text-destructive transition-colors"
                      title="Delete contact"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
