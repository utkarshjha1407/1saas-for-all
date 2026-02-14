import { useState } from "react";
import { Package, Plus, AlertTriangle, TrendingDown, Edit, Trash2, Loader2, X } from "lucide-react";
import { motion } from "framer-motion";
import { useInventory } from "@/hooks/useInventory";
import { useToast } from "@/hooks/use-toast";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { inventoryService } from "@/lib/api";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function getStockStatus(stock: number, threshold: number) {
  if (stock <= threshold * 0.5) return { label: "Critical", className: "bg-destructive/10 text-destructive" };
  if (stock <= threshold) return { label: "Low", className: "bg-warning/10 text-warning" };
  return { label: "OK", className: "bg-success/10 text-success" };
}

export default function Inventory() {
  const { items, isLoading } = useInventory();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    quantity: 0,
    low_stock_threshold: 5,
    unit: "unit",
  });

  // Use mutations directly
  const { mutateAsync: createMutation } = useMutation({
    mutationFn: (data: any) => inventoryService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast({ title: "Item created", description: "New inventory item has been added." });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to create item",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    },
  });

  const { mutateAsync: updateMutation } = useMutation({
    mutationFn: ({ id, ...data }: any) => inventoryService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast({ title: "Item updated", description: "Inventory item has been updated." });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to update item",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    },
  });

  const { mutateAsync: deleteMutation } = useMutation({
    mutationFn: (id: string) => inventoryService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast({ title: "Item deleted", description: "Inventory item has been removed." });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to delete item",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await updateMutation.mutateAsync({ id: editingItem.id, ...formData });
      } else {
        await createMutation.mutateAsync(formData);
      }
      setIsDialogOpen(false);
      setEditingItem(null);
      setFormData({ name: "", description: "", quantity: 0, low_stock_threshold: 5, unit: "unit" });
    } catch (error: any) {
      // Error already handled by mutation
      console.error('Submit error:', error);
    }
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description || "",
      quantity: item.quantity,
      low_stock_threshold: item.low_stock_threshold,
      unit: item.unit,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      await deleteMutation.mutateAsync(id);
    } catch (error: any) {
      // Error already handled by mutation
      console.error('Delete error:', error);
    }
  };

  const criticalCount = items?.filter(i => i.quantity <= i.low_stock_threshold * 0.5).length || 0;
  const lowCount = items?.filter(i => i.quantity > i.low_stock_threshold * 0.5 && i.quantity <= i.low_stock_threshold).length || 0;

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
          <h1 className="text-2xl font-bold text-foreground">Inventory</h1>
          <p className="text-sm text-muted-foreground mt-1">Track resources and stock levels</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={(open) => {
          setIsDialogOpen(open);
          if (!open) {
            setEditingItem(null);
            setFormData({ name: "", description: "", quantity: 0, low_stock_threshold: 5, unit: "unit" });
          }
        }}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Item
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingItem ? 'Edit Item' : 'Add New Item'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="name">Item Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Cleaning Supplies"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    min="0"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit">Unit</Label>
                  <Input
                    id="unit"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    placeholder="unit, box, bottle"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="threshold">Low Stock Threshold *</Label>
                <Input
                  id="threshold"
                  type="number"
                  min="0"
                  value={formData.low_stock_threshold}
                  onChange={(e) => setFormData({ ...formData, low_stock_threshold: parseInt(e.target.value) || 0 })}
                  required
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">{editingItem ? 'Update' : 'Create'} Item</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-sm text-muted-foreground">Total Items</p>
          <p className="text-2xl font-bold text-card-foreground mt-1">{items?.length || 0}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-destructive" /> Critical
          </p>
          <p className="text-2xl font-bold text-destructive mt-1">{criticalCount}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            <TrendingDown className="w-3.5 h-3.5 text-warning" /> Low Stock
          </p>
          <p className="text-2xl font-bold text-warning mt-1">{lowCount}</p>
        </div>
      </div>

      {/* Inventory table */}
      {!items || items.length === 0 ? (
        <div className="bg-card rounded-xl border border-border p-12 text-center">
          <p className="text-muted-foreground">No inventory items yet. Add your first item to get started.</p>
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3">Item</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3">Stock</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3 hidden md:table-cell">Threshold</th>
                <th className="text-left text-xs font-medium text-muted-foreground px-5 py-3">Status</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => {
                const status = getStockStatus(item.quantity, item.low_stock_threshold);
                return (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.03 }}
                    className="border-b border-border/50 hover:bg-secondary/30 transition-colors"
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <Package className="w-4 h-4 text-muted-foreground" />
                        <div>
                          <span className="text-sm font-medium text-card-foreground">{item.name}</span>
                          {item.description && (
                            <p className="text-xs text-muted-foreground">{item.description}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-sm font-mono font-medium text-card-foreground">
                        {item.quantity} <span className="text-muted-foreground font-normal">{item.unit}</span>
                      </span>
                    </td>
                    <td className="px-5 py-4 hidden md:table-cell">
                      <span className="text-sm text-muted-foreground">{item.low_stock_threshold}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${status.className}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleEdit(item)}
                          className="p-1.5 rounded hover:bg-secondary transition-colors"
                          title="Edit item"
                        >
                          <Edit className="w-3.5 h-3.5 text-muted-foreground" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id, item.name)}
                          className="p-1.5 rounded hover:bg-destructive/10 hover:text-destructive transition-colors"
                          title="Delete item"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
