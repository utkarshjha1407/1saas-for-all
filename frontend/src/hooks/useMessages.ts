/**
 * Messages Hook
 * Manages conversations and messages
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messageService, Conversation, Message, MessageCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useMessages = () => {
  const queryClient = useQueryClient();

  // Get conversations with messages
  const { data: conversations, isLoading: conversationsLoading } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: async () => {
      const convos = await messageService.getConversations();
      // Fetch messages for each conversation
      const convosWithMessages = await Promise.all(
        convos.map(async (convo) => {
          try {
            const messages = await messageService.getMessages(convo.id);
            return { ...convo, messages };
          } catch {
            return { ...convo, messages: [] };
          }
        })
      );
      return convosWithMessages;
    },
    refetchInterval: 10000, // Refetch every 10 seconds for new messages
  });

  // Send message
  const sendMessageMutation = useMutation({
    mutationFn: (data: MessageCreate) => messageService.sendMessage(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['messages'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      toast.success('Message sent! Automation paused for this conversation.');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to send message');
    },
  });

  // Mark conversation as read
  const markAsReadMutation = useMutation({
    mutationFn: (conversationId: string) => messageService.markAsRead(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    },
  });

  return {
    conversations: conversations || [],
    isLoading: conversationsLoading,
    sendMessage: (data: MessageCreate) => sendMessageMutation.mutateAsync(data),
    isSending: sendMessageMutation.isPending,
    markAsRead: markAsReadMutation.mutate,
  };
};
