/**
 * Authentication Hook
 * Manages authentication state and operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService, LoginRequest, RegisterRequest, User } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useAuth = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Get current user
  const { data: user, isLoading, error } = useQuery<User>({
    queryKey: ['currentUser'],
    queryFn: () => authService.getCurrentUser(),
    enabled: authService.isAuthenticated(),
    retry: false,
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Login successful!');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Login failed');
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      toast.success('Registration successful!');
      navigate('/onboarding');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Registration failed');
    },
  });

  // Logout
  const logout = () => {
    authService.logout();
    queryClient.clear();
    toast.success('Logged out successfully');
  };

  return {
    user,
    isLoading,
    isAuthenticated: authService.isAuthenticated(),
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
  };
};
