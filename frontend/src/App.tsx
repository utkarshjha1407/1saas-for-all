import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Onboarding from "./pages/Onboarding";
import IntegrationSetup from "./pages/IntegrationSetup";
import ContactFormBuilder from "./pages/ContactFormBuilder";
import PublicContactForm from "./pages/PublicContactForm";
import BookingSetup from "./pages/BookingSetup";
import PublicBookingPage from "./pages/PublicBookingPage";
import FormUpload from "./pages/FormUpload";
import PublicFormView from "./pages/PublicFormView";
import InventorySetup from "./pages/InventorySetup";
import StaffManagement from "./pages/StaffManagement";
import WorkspaceActivation from "./pages/WorkspaceActivation";
import Dashboard from "./pages/Dashboard";
import Inbox from "./pages/Inbox";
import Bookings from "./pages/Bookings";
import Contacts from "./pages/Contacts";
import Forms from "./pages/Forms";
import Inventory from "./pages/Inventory";
import SettingsPage from "./pages/SettingsPage";
import Profile from "./pages/Profile";
import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

const queryClient = new QueryClient();

const AppPage = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute>
    <AppLayout>{children}</AppLayout>
  </ProtectedRoute>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/integration-setup" element={<ProtectedRoute><IntegrationSetup /></ProtectedRoute>} />
          <Route path="/contact-form-builder" element={<ProtectedRoute><ContactFormBuilder /></ProtectedRoute>} />
          <Route path="/booking-setup" element={<ProtectedRoute><BookingSetup /></ProtectedRoute>} />
          <Route path="/form-upload" element={<ProtectedRoute><FormUpload /></ProtectedRoute>} />
          <Route path="/inventory-setup" element={<ProtectedRoute><InventorySetup /></ProtectedRoute>} />
          <Route path="/staff-management" element={<ProtectedRoute><StaffManagement /></ProtectedRoute>} />
          <Route path="/workspace-activation" element={<ProtectedRoute><WorkspaceActivation /></ProtectedRoute>} />
          <Route path="/public/:slug/contact" element={<PublicContactForm />} />
          <Route path="/public/book/:workspaceId" element={<PublicBookingPage />} />
          <Route path="/public/forms/:submissionId" element={<PublicFormView />} />
          <Route path="/dashboard" element={<AppPage><Dashboard /></AppPage>} />
          <Route path="/inbox" element={<AppPage><Inbox /></AppPage>} />
          <Route path="/bookings" element={<AppPage><Bookings /></AppPage>} />
          <Route path="/contacts" element={<AppPage><Contacts /></AppPage>} />
          <Route path="/forms" element={<AppPage><Forms /></AppPage>} />
          <Route path="/inventory" element={<AppPage><Inventory /></AppPage>} />
          <Route path="/settings" element={<AppPage><SettingsPage /></AppPage>} />
          <Route path="/profile" element={<AppPage><Profile /></AppPage>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
