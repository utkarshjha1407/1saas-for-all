import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Onboarding from "./pages/Onboarding";
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
