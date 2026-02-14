/**
 * Message Service
 * Handles messaging and conversations
 */

import apiClient from '../client';
import { Message, Conversation } from '../types';

export const messageService = {
  /**
   * Get all conversations
   */
  async getConversations(): Promise<Conversation[]> {
    const response = await apiClient.get<Conversation[]>('/messages/conversations');
    return response.data;
  },

  /**
   * Get messages in a conversation
   */
  async getMessages(conversationId: string): Promise<Message[]> {
    const response = await apiClient.get<Message[]>(`/messages/conversations/${conversationId}/messages`);
    return response.data;
  },

  /**
   * Send a message
   */
  async sendMessage(conversationId: string, data: { content: string; channel: 'email' | 'sms' }): Promise<Message> {
    const response = await apiClient.post<Message>(`/messages/conversations/${conversationId}/messages`, {
      conversation_id: conversationId,
      ...data,
    });
    return response.data;
  },

  /**
   * Mark conversation as read
   */
  async markAsRead(conversationId: string): Promise<void> {
    await apiClient.post(`/messages/conversations/${conversationId}/mark-read`);
  },
};
