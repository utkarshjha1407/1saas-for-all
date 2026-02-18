import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useInventory } from '../hooks/useInventory';
import { useBookingTypes } from '../hooks/useBookingTypes';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  Package,
  Plus,
  Trash2,
  Edit,
  AlertTriangle,
  TrendingUp,
  Info,
  Minus,
  CheckCircle,
} from 'lucide-react';
import type { InventoryItem } from '../lib/api/types';

export default function InventorySetup() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { items, forecast, createItem, updateItem, deleteItem, adjustQuantity, isCreatingItem, fetchItems, fetchForecast } = useInventory();
  const { bookingTypes, fetchBookingTypes } = useBookingTypes();

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showAdjustDialog, setShowAdjustDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [showForecast, setShowForecast] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    quantity: 0,
    low_stock_threshold: 0,
    unit: 'unit',
    booking_type_ids: [] as string[],
    quantity_per_booking: 1,
  });

  const [adjustmentData, setAdjustmentData] = useState({
    adjustment: 0,
    reason: '',
  });

  const isOwner = user?.role === 'owner';

  useEffect(() => {
    fetchBookingTypes();
    fetchItems();
    fetchForecast();
  }, [fetchBookingTypes, fetchItems, fetchForecast]);

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      quantity: 0,
      low_stock_threshold: 0,
      unit: 'unit',
      booking_type_ids: [],
      quantity_per_booking: 1,
    });
  };

  const handleAdd = async () => {
    if (!formData.name.trim()) {
      toast.error('Please enter an item name');
      return;
    }

    try {
      await createItem(formData);
      toast.success('Item added successfully');
      setShowAddDialog(false);
      resetForm();
      fetchItems();
      fetchForecast();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add item');
    }
  };

  const handleEdit = async () => {
    if (!selectedItem) return;

    try {
      await updateItem({ id: selectedItem.id, data: formData });
      toast.success('Item updated successfully');
      setShowEditDialog(false);
      setSelectedItem(null);
      resetForm();
      fetchItems();
      fetchForecast();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update item');
    }
  };

  const handleDelete = async (item: InventoryItem) => {
    if (!confirm(`Are you sure you want to delete "${item.name}"?`)) {
      return;
    }

    try {
      await deleteItem(item.id);
      toast.success('Item deleted successfully');
      fetchItems();
      fetchForecast();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete item');
    }
  };

  const openEditDialog = (item: InventoryItem) => {
    setSelectedItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
      quantity: item.quantity,
      low_stock_threshold: item.low_stock_threshold,
      unit: item.unit,
      booking_type_ids: item.booking_type_ids || [],
      quantity_per_booking: item.quantity_per_booking || 1,
    });
    setShowEditDialog(true);
  };

  const openAdjustDialog = (item: InventoryItem) => {
    setSelectedItem(item);
    setAdjustmentData({ adjustment: 0, reason: '' });
    setShowAdjustDialog(true);
  };

  const handleAdjust = async () => {
    if (!selectedItem) return;

    if (adjustmentData.adjustment === 0) {
      toast.error('Please enter an adjustment amount');
      return;
    }

    try {
      await adjustQuantity({ id: selectedItem.id, data: adjustmentData });
      toast.success('Quantity adjusted successfully');
      setShowAdjustDialog(false);
      setSelectedItem(null);
      setAdjustmentData({ adjustment: 0, reason: '' });
      fetchItems();
      fetchForecast();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to adjust quantity');
    }
  };

  const handleSkip = () => {
    navigate('/staff-management');
  };

  const handleContinue = () => {
    navigate('/staff-management');
  };

  if (!isOwner) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Inventory Management (View Only)</CardTitle>
            <CardDescription>
              Only workspace owners can manage inventory items.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Contact your workspace owner to manage inventory.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  const lowStockItems = items.filter((item) => item.is_low_stock);

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Step 6: Set Up Inventory</h1>
        <p className="text-muted-foreground mt-2">
          Track items and resources used per booking with automated alerts
        </p>
      </div>

      {lowStockItems.length > 0 && (
        <Alert className="mb-6 border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-800">
            {lowStockItems.length} item{lowStockItems.length > 1 ? 's' : ''} running low on stock
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Inventory List */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Inventory Items</CardTitle>
                  <CardDescription>
                    Items automatically tracked per booking
                  </CardDescription>
                </div>
                <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
                  <DialogTrigger asChild>
                    <Button onClick={() => resetForm()}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Item
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>Add Inventory Item</DialogTitle>
                      <DialogDescription>
                        Define items used per booking with automatic tracking
                      </DialogDescription>
                    </DialogHeader>
                    <ItemForm
                      formData={formData}
                      setFormData={setFormData}
                      bookingTypes={bookingTypes}
                      onSubmit={handleAdd}
                      onCancel={() => setShowAddDialog(false)}
                      isSubmitting={isCreatingItem}
                    />
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {items.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No inventory items yet</p>
                  <p className="text-sm mt-1">Add your first item to start tracking</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {items.map((item) => (
                    <Card key={item.id} className={item.is_low_stock ? 'border-orange-300' : ''}>
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <Package className="h-4 w-4 text-primary" />
                              <h4 className="font-semibold">{item.name}</h4>
                              {item.is_low_stock && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-orange-100 text-orange-800">
                                  <AlertTriangle className="h-3 w-3 mr-1" />
                                  Low Stock
                                </span>
                              )}
                            </div>
                            {item.description && (
                              <p className="text-sm text-muted-foreground mt-1">
                                {item.description}
                              </p>
                            )}
                            <div className="flex items-center gap-4 mt-2 text-sm">
                              <span className="font-medium">
                                {item.quantity} {item.unit}
                              </span>
                              <span className="text-muted-foreground">
                                Alert at: {item.low_stock_threshold}
                              </span>
                              <span className="text-muted-foreground">
                                Per booking: {item.quantity_per_booking}
                              </span>
                            </div>
                            {item.booking_type_ids && item.booking_type_ids.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs text-muted-foreground">Linked to:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {item.booking_type_ids.map((btId) => {
                                    const bt = bookingTypes.find((t) => t.id === btId);
                                    return bt ? (
                                      <span
                                        key={btId}
                                        className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-primary/10 text-primary"
                                      >
                                        {bt.name}
                                      </span>
                                    ) : null;
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openAdjustDialog(item)}
                            >
                              <Plus className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openEditDialog(item)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(item)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Forecast Panel */}
        <div>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Usage Forecast</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowForecast(!showForecast)}
                >
                  <TrendingUp className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription>Next 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              {forecast.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No forecast data available
                </p>
              ) : (
                <div className="space-y-3">
                  {forecast.map((f) => (
                    <div
                      key={f.item_id}
                      className={`p-3 rounded-lg border ${
                        f.reorder_recommended ? 'border-orange-300 bg-orange-50' : 'border-border'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{f.item_name}</p>
                          <div className="mt-1 space-y-1 text-xs text-muted-foreground">
                            <p>Current: {f.current_quantity}</p>
                            <p>Upcoming bookings: {f.upcoming_bookings}</p>
                            <p>Estimated usage: {f.estimated_usage}</p>
                            {f.days_until_depleted && (
                              <p className="text-orange-600 font-medium">
                                Depletes in ~{f.days_until_depleted} days
                              </p>
                            )}
                          </div>
                        </div>
                        {f.reorder_recommended && (
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {items.length > 0 && (
            <Alert className="mt-4">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Inventory will be automatically tracked when bookings are created for linked services.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Inventory Item</DialogTitle>
            <DialogDescription>
              Update item details and settings
            </DialogDescription>
          </DialogHeader>
          <ItemForm
            formData={formData}
            setFormData={setFormData}
            bookingTypes={bookingTypes}
            onSubmit={handleEdit}
            onCancel={() => {
              setShowEditDialog(false);
              setSelectedItem(null);
            }}
            isSubmitting={false}
          />
        </DialogContent>
      </Dialog>

      {/* Adjust Quantity Dialog */}
      <Dialog open={showAdjustDialog} onOpenChange={setShowAdjustDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adjust Quantity</DialogTitle>
            <DialogDescription>
              Add or subtract from current stock
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Current Quantity</Label>
              <p className="text-2xl font-bold">
                {selectedItem?.quantity} {selectedItem?.unit}
              </p>
            </div>
            <div>
              <Label htmlFor="adjustment">Adjustment</Label>
              <Input
                id="adjustment"
                type="number"
                value={adjustmentData.adjustment}
                onChange={(e) =>
                  setAdjustmentData({ ...adjustmentData, adjustment: parseInt(e.target.value) || 0 })
                }
                placeholder="Enter positive to add, negative to subtract"
              />
              <p className="text-xs text-muted-foreground mt-1">
                New quantity: {(selectedItem?.quantity || 0) + adjustmentData.adjustment}
              </p>
            </div>
            <div>
              <Label htmlFor="reason">Reason (optional)</Label>
              <Input
                id="reason"
                value={adjustmentData.reason}
                onChange={(e) =>
                  setAdjustmentData({ ...adjustmentData, reason: e.target.value })
                }
                placeholder="e.g., Received shipment, Manual count"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAdjustDialog(false);
                  setSelectedItem(null);
                }}
              >
                Cancel
              </Button>
              <Button onClick={handleAdjust}>Adjust Quantity</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Actions */}
      <div className="flex justify-between mt-6">
        <Button variant="outline" onClick={handleSkip}>
          Skip for Now
        </Button>
        <Button onClick={handleContinue}>
          Continue to Dashboard
        </Button>
      </div>
    </div>
  );
}

// Item Form Component
function ItemForm({
  formData,
  setFormData,
  bookingTypes,
  onSubmit,
  onCancel,
  isSubmitting,
}: {
  formData: any;
  setFormData: (data: any) => void;
  bookingTypes: any[];
  onSubmit: () => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) {
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="name">Item Name *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g., Gloves, Syringes, Bandages"
          maxLength={255}
        />
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Brief description of the item"
          rows={2}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="quantity">Current Quantity *</Label>
          <Input
            id="quantity"
            type="number"
            min="0"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
          />
        </div>

        <div>
          <Label htmlFor="unit">Unit</Label>
          <Input
            id="unit"
            value={formData.unit}
            onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
            placeholder="e.g., box, bottle, unit"
            maxLength={50}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="threshold">Low Stock Alert *</Label>
          <Input
            id="threshold"
            type="number"
            min="0"
            value={formData.low_stock_threshold}
            onChange={(e) =>
              setFormData({ ...formData, low_stock_threshold: parseInt(e.target.value) || 0 })
            }
          />
          <p className="text-xs text-muted-foreground mt-1">
            Alert when quantity falls below this
          </p>
        </div>

        <div>
          <Label htmlFor="per_booking">Quantity Per Booking *</Label>
          <Input
            id="per_booking"
            type="number"
            min="1"
            value={formData.quantity_per_booking}
            onChange={(e) =>
              setFormData({ ...formData, quantity_per_booking: parseInt(e.target.value) || 1 })
            }
          />
          <p className="text-xs text-muted-foreground mt-1">
            Amount used per booking
          </p>
        </div>
      </div>

      <div>
        <Label>Link to Booking Types</Label>
        <p className="text-sm text-muted-foreground mb-2">
          Select which services use this item
        </p>
        <div className="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3">
          {bookingTypes.map((type) => (
            <div key={type.id} className="flex items-center space-x-2">
              <Checkbox
                id={type.id}
                checked={formData.booking_type_ids.includes(type.id)}
                onCheckedChange={(checked) => {
                  if (checked) {
                    setFormData({
                      ...formData,
                      booking_type_ids: [...formData.booking_type_ids, type.id],
                    });
                  } else {
                    setFormData({
                      ...formData,
                      booking_type_ids: formData.booking_type_ids.filter((id: string) => id !== type.id),
                    });
                  }
                }}
              />
              <label
                htmlFor={type.id}
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {type.name}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : 'Save Item'}
        </Button>
      </div>
    </div>
  );
}
