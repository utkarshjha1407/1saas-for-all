/**
 * Inventory Hook
 * Manages inventory items, usage tracking, and forecasting
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryService } from '@/lib/api/services/inventory.service';
import type {
  InventoryItem,
  InventoryItemCreate,
  InventoryItemUpdate,
  InventoryAdjustment,
  InventoryForecast,
} from '@/lib/api/types';

export const useInventory = () => {
  const queryClient = useQueryClient();

  // Get items
  const { data: items = [], isLoading: itemsLoading, refetch: fetchItems } = useQuery<InventoryItem[]>({
    queryKey: ['inventory', 'items'],
    queryFn: () => inventoryService.getItems(),
  });

  // Get low stock items
  const { data: lowStockItems = [], refetch: fetchLowStockItems } = useQuery<InventoryItem[]>({
    queryKey: ['inventory', 'items', 'low-stock'],
    queryFn: () => inventoryService.getItems(true),
  });

  // Get forecast
  const { data: forecast = [], isLoading: forecastLoading, refetch: fetchForecast } = useQuery<InventoryForecast[]>({
    queryKey: ['inventory', 'forecast'],
    queryFn: () => inventoryService.getForecast(30),
  });

  // Create item
  const createItemMutation = useMutation({
    mutationFn: (data: InventoryItemCreate) => inventoryService.createItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });

  // Update item
  const updateItemMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: InventoryItemUpdate }) =>
      inventoryService.updateItem(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });

  // Delete item
  const deleteItemMutation = useMutation({
    mutationFn: (id: string) => inventoryService.deleteItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });

  // Adjust quantity
  const adjustQuantityMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: InventoryAdjustment }) =>
      inventoryService.adjustQuantity(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });

  return {
    items,
    lowStockItems,
    forecast,
    isLoading: itemsLoading || forecastLoading,
    fetchItems,
    fetchLowStockItems,
    fetchForecast,
    createItem: createItemMutation.mutateAsync,
    updateItem: updateItemMutation.mutateAsync,
    deleteItem: deleteItemMutation.mutateAsync,
    adjustQuantity: adjustQuantityMutation.mutateAsync,
    isCreatingItem: createItemMutation.isPending,
    isUpdatingItem: updateItemMutation.isPending,
    isDeletingItem: deleteItemMutation.isPending,
    isAdjustingQuantity: adjustQuantityMutation.isPending,
  };
};
