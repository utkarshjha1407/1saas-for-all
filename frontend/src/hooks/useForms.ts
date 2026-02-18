/**
 * Forms Hook
 * Manages form templates (file uploads) and submissions
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formService } from '@/lib/api/services/form.service';
import type { FormTemplate, FormSubmission, FormTemplateCreate, FormSubmissionUpdate } from '@/lib/api/types';

export const useForms = () => {
  const queryClient = useQueryClient();

  // Get templates
  const { data: templates = [], isLoading: templatesLoading, refetch: fetchTemplates } = useQuery<FormTemplate[]>({
    queryKey: ['forms', 'templates'],
    queryFn: () => formService.getTemplates(),
  });

  // Get submissions
  const { data: submissions = [], isLoading: submissionsLoading, refetch: fetchSubmissions } = useQuery<FormSubmission[]>({
    queryKey: ['forms', 'submissions'],
    queryFn: () => formService.getSubmissions(),
  });

  // Create template
  const createTemplateMutation = useMutation({
    mutationFn: (data: FormTemplateCreate) => formService.createTemplate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
    },
  });

  // Update template
  const updateTemplateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FormTemplateCreate> }) =>
      formService.updateTemplate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
    },
  });

  // Delete template
  const deleteTemplateMutation = useMutation({
    mutationFn: (id: string) => formService.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'templates'] });
    },
  });

  // Update submission
  const updateSubmissionMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: FormSubmissionUpdate }) =>
      formService.updateSubmission(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forms', 'submissions'] });
    },
  });

  return {
    templates,
    submissions,
    isLoading: templatesLoading || submissionsLoading,
    fetchTemplates,
    fetchSubmissions,
    createTemplate: createTemplateMutation.mutateAsync,
    updateTemplate: updateTemplateMutation.mutateAsync,
    deleteTemplate: deleteTemplateMutation.mutateAsync,
    updateSubmission: updateSubmissionMutation.mutateAsync,
    isCreatingTemplate: createTemplateMutation.isPending,
    isUpdatingTemplate: updateTemplateMutation.isPending,
    isDeletingTemplate: deleteTemplateMutation.isPending,
  };
};
