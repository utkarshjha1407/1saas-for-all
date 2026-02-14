import { useState } from "react";
import { Search, Send, Paperclip, MoreVertical, Phone, Mail, Clock, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useMessages } from "@/hooks/useMessages";

export default function Inbox() {
  const { conversations, isLoading, sendMessage } = useMessages();
  const [selectedConvoId, setSelectedConvoId] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState("");
  
  const { messages: conversationMessages, isLoading: messagesLoading } = useMessages().useConversationMessages(
    selectedConvoId || ""
  );

  const selectedConvo = conversations?.find(c => c.id === selectedConvoId);

  // Auto-select first conversation
  if (!selectedConvoId && conversations && conversations.length > 0) {
    setSelectedConvoId(conversations[0].id);
  }

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedConvoId) return;
    
    sendMessage({
      conversationId: selectedConvoId,
      content: messageInput,
      channel: "email"
    });
    setMessageInput("");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* Conversations list */}
      <div className="w-80 border-r border-border bg-card flex flex-col shrink-0">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2 bg-secondary rounded-lg px-3 py-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search conversations..."
              className="bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground w-full"
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map((convo) => (
            <button
              key={convo.id}
              onClick={() => setSelectedConvo(convo)}
              className={`w-full text-left px-4 py-3 border-b border-border/50 hover:bg-secondary/50 transition-colors ${
                selectedConvo.id === convo.id ? "bg-accent/50" : ""
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold shrink-0 mt-0.5">
                  {convo.name.split(" ").map(n => n[0]).join("")}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className={`text-sm ${convo.unread ? "font-semibold text-card-foreground" : "font-medium text-muted-foreground"}`}>
                      {convo.name}
                    </span>
                    <span className="text-xs text-muted-foreground">{convo.time}</span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    {convo.channel === "sms" ? <Phone className="w-3 h-3 text-muted-foreground" /> : <Mail className="w-3 h-3 text-muted-foreground" />}
                    <p className={`text-xs truncate ${convo.unread ? "text-card-foreground" : "text-muted-foreground"}`}>
                      {convo.message}
                    </p>
                  </div>
                </div>
                {convo.unread && <span className="w-2 h-2 rounded-full bg-primary shrink-0 mt-2" />}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Message area */}
      <div className="flex-1 flex flex-col">
        {/* Chat header */}
        <div className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
              {selectedConvo.name.split(" ").map(n => n[0]).join("")}
            </div>
            <div>
              <p className="text-sm font-semibold text-card-foreground">{selectedConvo.name}</p>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-success" />
                via {selectedConvo.channel}
              </p>
            </div>
          </div>
          <button className="p-2 rounded-lg hover:bg-secondary transition-colors">
            <MoreVertical className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.incoming ? "justify-start" : "justify-end"}`}
            >
              <div className={`max-w-md px-4 py-2.5 rounded-2xl text-sm ${
                (msg as any).system
                  ? "bg-accent text-accent-foreground text-center text-xs italic"
                  : msg.incoming
                  ? "bg-secondary text-secondary-foreground rounded-bl-sm"
                  : "bg-primary text-primary-foreground rounded-br-sm"
              }`}>
                <p>{msg.content}</p>
                <p className={`text-xs mt-1 ${msg.incoming ? "text-muted-foreground" : "text-primary-foreground/70"}`}>{msg.time}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Input */}
        <div className="border-t border-border bg-card p-4">
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg hover:bg-secondary transition-colors">
              <Paperclip className="w-4 h-4 text-muted-foreground" />
            </button>
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-secondary rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring"
            />
            <button className="p-2.5 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
