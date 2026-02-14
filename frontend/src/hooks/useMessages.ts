/**
 * Messages Hook
 * Manages conversations and messages
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messageService, Conversation, Message, MessageCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useMessages = () => {
  const queryClient = useQueryClient();

  // Get conversations
  const { data: conversations, isLoading: conversationsLoading } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: () => messageService.getConversations(),
  });

  // Send message
  const sendMessageMutation = useMutation({
    mutationFn: (data: MessageCreate) => messageService.sendMessage(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['messages'] });
      toast.success('Message sent!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to send message');
    },
  });

  // Get messages for a conversation
  const useConversationMessages = (conversationId?: string) => {
    return useQuery<Message[]>({
      queryKey: ['messages', conversationId],
      queryFn: () => messageService.getMessages(conversationId!),
      enabled: !!conversationId,
    });
  };

  return {
    conversations: conversations || [],
    isLoading: conversationsLoading,
    sendMessage: sendMessageMutation.mutate,
    isSending: sendMessageMutation.isPending,
    useConversationMessages,
  };
};
