import { useState, useEffect } from "react";
import { Search, Send, Phone, Mail, Loader2, Bot, User, PauseCircle, PlayCircle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useMessages } from "@/hooks/useMessages";
import { useContacts } from "@/hooks/useContacts";

export default function Inbox() {
  const { conversations, isLoading, sendMessage, markAsRead } = useMessages();
  const { contacts } = useContacts();
  const [selectedConvoId, setSelectedConvoId] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSending, setIsSending] = useState(false);

  const selectedConvo = conversations?.find(c => c.id === selectedConvoId);
  
  // Get contact details for selected conversation
  const selectedContact = selectedConvo 
    ? contacts?.find(c => c.id === selectedConvo.contact_id)
    : null;

  // Auto-select first conversation
  useEffect(() => {
    if (!selectedConvoId && conversations && conversations.length > 0) {
      setSelectedConvoId(conversations[0].id);
    }
  }, [conversations, selectedConvoId]);

  // Mark as read when conversation is selected
  useEffect(() => {
    if (selectedConvoId && selectedConvo?.unread_count > 0) {
      markAsRead(selectedConvoId);
    }
  }, [selectedConvoId, selectedConvo?.unread_count, markAsRead]);

  // Filter conversations by search
  const filteredConversations = conversations?.filter(convo => {
    if (!searchQuery) return true;
    const contact = contacts?.find(c => c.id === convo.contact_id);
    return contact?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
           contact?.email?.toLowerCase().includes(searchQuery.toLowerCase());
  }) || [];

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedConvoId || !selectedConvo) return;
    
    setIsSending(true);
    try {
      await sendMessage({
        conversationId: selectedConvoId,
        content: messageInput,
        channel: selectedConvo.last_channel || "email"
      });
      setMessageInput("");
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="text-center">
          <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No Conversations Yet</h3>
          <p className="text-sm text-muted-foreground">
            Conversations will appear here when contacts reach out via email or SMS
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Conversations list */}
      <div className="w-80 border-r border-border bg-card flex flex-col shrink-0">
        {/* Search */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2 bg-secondary rounded-lg px-3 py-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground w-full"
            />
          </div>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.map((convo) => {
            const contact = contacts?.find(c => c.id === convo.contact_id);
            const lastMessageTime = new Date(convo.last_message_at);
            const timeStr = lastMessageTime.toLocaleTimeString('en-US', { 
              hour: 'numeric', 
              minute: '2-digit' 
            });
            
            return (
              <button
                key={convo.id}
                onClick={() => setSelectedConvoId(convo.id)}
                className={`w-full text-left px-4 py-3 border-b border-border/50 hover:bg-secondary/50 transition-colors ${
                  selectedConvoId === convo.id ? "bg-accent/50" : ""
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center text-primary-foreground text-xs font-bold shrink-0 mt-0.5">
                    {contact?.name?.split(" ").map(n => n[0]).join("").toUpperCase() || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm ${convo.unread_count > 0 ? "font-semibold text-card-foreground" : "font-medium text-muted-foreground"}`}>
                        {contact?.name || "Unknown Contact"}
                      </span>
                      <span className="text-xs text-muted-foreground">{timeStr}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {convo.last_channel === "sms" ? (
                        <Phone className="w-3 h-3 text-muted-foreground" />
                      ) : (
                        <Mail className="w-3 h-3 text-muted-foreground" />
                      )}
                      {convo.is_automated_paused && (
                        <PauseCircle className="w-3 h-3 text-warning" />
                      )}
                      <p className={`text-xs truncate ${convo.unread_count > 0 ? "text-card-foreground font-medium" : "text-muted-foreground"}`}>
                        {convo.last_message_preview || "No messages yet"}
                      </p>
                    </div>
                  </div>
                  {convo.unread_count > 0 && (
                    <span className="min-w-[20px] h-5 px-1.5 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center shrink-0 mt-1">
                      {convo.unread_count}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Message area */}
      {selectedConvo && selectedContact ? (
        <div className="flex-1 flex flex-col">
          {/* Chat header */}
          <div className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center text-primary-foreground text-xs font-bold">
                {selectedContact.name.split(" ").map(n => n[0]).join("").toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-semibold text-card-foreground">{selectedContact.name}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    {selectedConvo.last_channel === "sms" ? (
                      <Phone className="w-3 h-3" />
                    ) : (
                      <Mail className="w-3 h-3" />
                    )}
                    {selectedConvo.last_channel}
                  </span>
                  {selectedConvo.is_automated_paused && (
                    <span className="flex items-center gap-1 text-warning">
                      <PauseCircle className="w-3 h-3" />
                      Automation paused
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {selectedContact.email && (
                <span className="text-xs text-muted-foreground">{selectedContact.email}</span>
              )}
              {selectedContact.phone && (
                <span className="text-xs text-muted-foreground">{selectedContact.phone}</span>
              )}
            </div>
          </div>

          {/* Automation pause notice */}
          {selectedConvo.is_automated_paused && (
            <div className="bg-warning/10 border-b border-warning/20 px-6 py-3">
              <div className="flex items-center gap-2 text-sm">
                <AlertCircle className="w-4 h-4 text-warning" />
                <span className="text-warning font-medium">Automation Paused</span>
                <span className="text-muted-foreground">
                  - Automated messages are disabled for this conversation
                </span>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-secondary/20">
            <AnimatePresence>
              {selectedConvo.messages?.map((msg: any) => {
                const isIncoming = msg.message_type === "automated" || !msg.sender_id;
                const isAutomated = msg.message_type === "automated";
                const messageTime = new Date(msg.sent_at);
                const timeStr = messageTime.toLocaleTimeString('en-US', { 
                  hour: 'numeric', 
                  minute: '2-digit' 
                });

                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className={`flex ${isIncoming ? "justify-start" : "justify-end"}`}
                  >
                    <div className={`max-w-md ${isIncoming ? "mr-12" : "ml-12"}`}>
                      <div className={`px-4 py-2.5 rounded-2xl text-sm ${
                        isIncoming
                          ? "bg-card text-card-foreground rounded-bl-sm"
                          : "bg-primary text-primary-foreground rounded-br-sm"
                      }`}>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                      <div className={`flex items-center gap-2 mt-1 px-1 ${isIncoming ? "" : "justify-end"}`}>
                        {isAutomated && (
                          <Bot className="w-3 h-3 text-muted-foreground" />
                        )}
                        {!isIncoming && (
                          <User className="w-3 h-3 text-muted-foreground" />
                        )}
                        <span className="text-xs text-muted-foreground">
                          {timeStr}
                          {isAutomated && " • Automated"}
                          {msg.channel === "sms" && " • SMS"}
                          {msg.channel === "email" && " • Email"}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>

          {/* Input */}
          <div className="border-t border-border bg-card p-4">
            <div className="flex items-end gap-3">
              <textarea
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Reply via ${selectedConvo.last_channel}...`}
                rows={1}
                className="flex-1 bg-secondary rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring resize-none min-h-[42px] max-h-32"
                style={{ 
                  height: 'auto',
                  minHeight: '42px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 128) + 'px';
                }}
              />
              <button 
                onClick={handleSendMessage}
                disabled={!messageInput.trim() || isSending}
                className="p-2.5 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send • Shift+Enter for new line
              {!selectedConvo.is_automated_paused && " • Sending will pause automation"}
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-secondary/20">
          <div className="text-center">
            <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Select a Conversation</h3>
            <p className="text-sm text-muted-foreground">
              Choose a conversation from the list to view messages
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
