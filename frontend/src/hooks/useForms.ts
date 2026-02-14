/**
 * Forms Hook
 * Manages form templates and submissions
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formService, FormTemplate, FormSubmission, FormTemplateCreate, FormSubmissionCreate } from '@/lib/api';
import { toast } from 'sonner';

export const useForms = () => {
  const queryClient = useQueryClient();

  // Get templates
  const { data: templates, isLoading: templatesLoading } = useQuery<FormTemplate[]>({
    queryKey: ['forms', 'templates'],
    queryFn: () => formService.getTemplates(),
  });

  // Get submissions
  const { data: submissions, isLoading: submissionsLoading } = useQuery<FormSubmission[]>({
    queryKey: ['forms', 'submissions'],
    queryFn: () => formService.getSubmissions(),
  });

  // Create template
  const createTemplateMutation = useMutation({
    mutationFn: (data: FormTemplateCreate) => formService.createTemplate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
      toast.success('Template created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create template');
    },
  });

  // Update template
  const updateTemplateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FormTemplateCreate> }) =>
      formService.updateTemplate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
      toast.success('Template updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update template');
    },
  });

  // Delete template
  const deleteTemplateMutation = useMutation({
    mutationFn: (id: string) => formService.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
      toast.success('Template deleted!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete template');
    },
  });

  // Update submission status
  const updateSubmissionStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: FormSubmission['status'] }) =>
      formService.updateSubmissionStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'submissions'] });
      toast.success('Status updated!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update status');
    },
  });

  return {
    templates: templates || [],
    submissions: submissions || [],
    isLoading: templatesLoading || submissionsLoading,
    createTemplate: createTemplateMutation.mutate,
    updateTemplate: updateTemplateMutation.mutate,
    deleteTemplate: deleteTemplateMutation.mutate,
    updateSubmissionStatus: updateSubmissionStatusMutation.mutate,
    isCreatingTemplate: createTemplateMutation.isPending,
    isUpdatingTemplate: updateTemplateMutation.isPending,
    isDeletingTemplate: deleteTemplateMutation.isPending,
  };
};
