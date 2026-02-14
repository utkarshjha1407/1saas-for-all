/**
 * Inventory Hook
 * Manages inventory items and usage
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryService, InventoryItem, InventoryItemCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useInventory = () => {
  const queryClient = useQueryClient();

  // Get all items
  const { data: items, isLoading } = useQuery<InventoryItem[]>({
    queryKey: ['inventory'],
    queryFn: () => inventoryService.getAll(),
  });

  // Get low stock items
  const { data: lowStockItems } = useQuery<InventoryItem[]>({
    queryKey: ['inventory', 'low-stock'],
    queryFn: () => inventoryService.getLowStock(),
  });

  // Create item
  const createMutation = useMutation({
    mutationFn: (data: InventoryItemCreate) => inventoryService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Item added successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to add item');
    },
  });

  // Update item
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<InventoryItemCreate> }) =>
      inventoryService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Item updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update item');
    },
  });

  // Update quantity
  const updateQuantityMutation = useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) =>
      inventoryService.updateQuantity(id, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Quantity updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update quantity');
    },
  });

  // Delete item
  const deleteMutation = useMutation({
    mutationFn: (id: string) => inventoryService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Item deleted!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete item');
    },
  });

  return {
    items: items || [],
    lowStockItems: lowStockItems || [],
    isLoading,
    createItem: createMutation.mutate,
    updateItem: updateMutation.mutate,
    updateQuantity: updateQuantityMutation.mutate,
    deleteItem: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};
