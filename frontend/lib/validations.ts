import * as z from 'zod'

// Summary Form Validation Schema
export const summaryFormSchema = z.object({
  text: z.string().min(10, {
    message: 'Text must be at least 10 characters.'
  }),
  type: z.enum(['concise', 'detailed']),
  max_length: z.coerce.number().int().positive().optional()
})

export type SummaryFormValues = z.infer<typeof summaryFormSchema>

// Markdown Form Validation Schema
export const markdownFormSchema = z.object({
  text: z.string().min(1, {
    message: 'Please enter some text to convert.'
  }),
  mode: z.enum(['to_markdown', 'to_text'])
})

export type MarkdownFormValues = z.infer<typeof markdownFormSchema>
