/**
 * API Type Definitions
 * TypeScript interfaces matching backend schemas
 */

// Authentication Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  workspace_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'owner' | 'staff';
  workspace_id: string;
  is_active: boolean;
}

// Workspace Types
export interface WorkspaceCreate {
  name: string;
  address: string;
  timezone: string;
  contact_email: string;
}

export interface Workspace {
  id: string;
  name: string;
  address: string;
  timezone: string;
  contact_email: string;
  status: 'setup' | 'active' | 'suspended';
  onboarding_step: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface OnboardingStatus {
  current_step: string;
  completed_steps: string[];
  is_complete: boolean;
  next_step: string | null;
  missing_requirements: string[];
}

// Booking Types
export interface BookingCreate {
  booking_type_id: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string;
  scheduled_at: string;
  notes?: string;
}

export interface Booking {
  id: string;
  workspace_id: string;
  booking_type_id: string;
  contact_id: string;
  scheduled_at: string;
  status: 'pending' | 'confirmed' | 'completed' | 'no_show' | 'cancelled';
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Contact Types
export interface ContactCreate {
  name: string;
  email?: string;
  phone?: string;
  message?: string;
}

export interface Contact {
  id: string;
  workspace_id: string;
  name: string;
  email?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

// Dashboard Types
export interface DashboardStats {
  bookings: {
    today_count: number;
    upcoming_count: number;
    completed_count: number;
    no_show_count: number;
  };
  leads: {
    new_inquiries: number;
    ongoing_conversations: number;
    unanswered_messages: number;
  };
  forms: {
    pending_count: number;
    overdue_count: number;
    completed_count: number;
  };
  inventory: {
    low_stock_items: number;
    critical_items: number;
  };
  total_alerts: number;
  critical_alerts: number;
  generated_at: string;
}

// Message Types
export interface Message {
  id: string;
  conversation_id: string;
  sender_id?: string;
  content: string;
  channel: 'email' | 'sms';
  message_type: 'automated' | 'manual';
  is_read: boolean;
  sent_at: string;
}

export interface Conversation {
  id: string;
  workspace_id: string;
  contact_id: string;
  last_message_at: string;
  unread_count: number;
  is_automated_paused: boolean;
  created_at: string;
}

// Form Types
export interface FormTemplate {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  fields: any[];
  booking_type_ids: string[];
  created_at: string;
}

export interface FormSubmission {
  id: string;
  form_template_id: string;
  booking_id: string;
  contact_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  data: Record<string, any>;
  submitted_at?: string;
  created_at: string;
}

// Inventory Types
export interface InventoryItem {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  quantity: number;
  low_stock_threshold: number;
  unit: string;
  is_low_stock: boolean;
  created_at: string;
  updated_at: string;
}

// API Error Type
export interface ApiError {
  message: string;
  status?: number;
  data?: any;
}
