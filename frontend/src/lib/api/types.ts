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
  last_message_preview?: string;
  last_channel?: 'email' | 'sms';
  unread_count: number;
  is_automated_paused: boolean;
  messages?: Message[];
  created_at: string;
}

export interface MessageCreate {
  conversationId: string;
  content: string;
  channel: 'email' | 'sms';
}

// Form Types (File Upload)
export interface FormTemplate {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  file_url: string;
  file_type?: string;
  file_size?: number;
  booking_type_ids: string[];
  created_at: string;
}

export interface FormTemplateCreate {
  name: string;
  description?: string;
  file_url: string;
  file_type?: string;
  file_size?: number;
  booking_type_ids: string[];
}

export interface FormSubmission {
  id: string;
  form_template_id: string;
  booking_id: string;
  contact_id: string;
  workspace_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  data: Record<string, any>;
  submitted_at?: string;
  viewed_at?: string;
  downloaded_at?: string;
  created_at: string;
  access_token?: string;
  public_url?: string;
}

export interface FormSubmissionCreate {
  form_template_id: string;
  booking_id: string;
  contact_id: string;
  status?: string;
  data?: Record<string, any>;
}

export interface FormSubmissionUpdate {
  status?: string;
  data?: Record<string, any>;
  viewed_at?: string;
  downloaded_at?: string;
  submitted_at?: string;
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
  booking_type_ids: string[];
  quantity_per_booking: number;
  created_at: string;
  updated_at: string;
}

export interface InventoryItemCreate {
  name: string;
  description?: string;
  quantity: number;
  low_stock_threshold: number;
  unit?: string;
  booking_type_ids?: string[];
  quantity_per_booking?: number;
}

export interface InventoryItemUpdate {
  name?: string;
  description?: string;
  quantity?: number;
  low_stock_threshold?: number;
  unit?: string;
  booking_type_ids?: string[];
  quantity_per_booking?: number;
}

export interface InventoryAdjustment {
  adjustment: number;
  reason?: string;
}

export interface InventoryUsage {
  id: string;
  inventory_item_id: string;
  booking_id: string;
  quantity_used: number;
  notes?: string;
  created_at: string;
}

export interface InventoryForecast {
  item_id: string;
  item_name: string;
  current_quantity: number;
  low_stock_threshold: number;
  quantity_per_booking: number;
  upcoming_bookings: number;
  estimated_usage: number;
  days_until_depleted?: number;
  reorder_recommended: boolean;
}

// Staff Management Types
export interface StaffPermissions {
  can_access_inbox: boolean;
  can_manage_bookings: boolean;
  can_view_forms: boolean;
  can_view_inventory: boolean;
}

export interface StaffInvitation {
  id: string;
  workspace_id: string;
  email: string;
  invited_by: string;
  token: string;
  permissions: StaffPermissions;
  status: 'pending' | 'accepted' | 'expired';
  expires_at: string;
  accepted_at?: string;
  created_at: string;
}

export interface StaffInvitationCreate {
  email: string;
  permissions?: StaffPermissions;
}

export interface StaffInvitationAccept {
  token: string;
  full_name: string;
  password: string;
}

export interface StaffMember {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  permissions?: StaffPermissions;
  created_at: string;
}

export interface WorkspaceActivationChecklist {
  communication_connected: boolean;
  booking_type_exists: boolean;
  availability_defined: boolean;
  all_requirements_met: boolean;
}

export interface WorkspaceActivation {
  is_activated: boolean;
  activated_at?: string;
  checklist: WorkspaceActivationChecklist;
  can_activate: boolean;
  missing_requirements: string[];
}

// API Error Type
export interface ApiError {
  message: string;
  status?: number;
  data?: any;
}

export interface BookingTypeCreate {
  name: string;
  description?: string;
  duration_minutes: number;
  location_type: 'in-person' | 'phone' | 'video' | 'client-location';
}

export interface BookingTypeUpdate {
  name?: string;
  description?: string;
  duration_minutes?: number;
  location_type?: 'in-person' | 'phone' | 'video' | 'client-location';
  is_active?: boolean;
}

export interface BookingType {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  duration_minutes: number;
  location_type: string;
  is_active: boolean;
  created_at: string;
}

export interface AvailabilitySlot {
  id?: string;
  booking_type_id?: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  created_at?: string;
}

export interface TimeSlot {
  start: string;
  end: string;
  available: boolean;
}
