/* eslint-disable @typescript-eslint/no-explicit-any */
// global.d.ts
declare module '@/lib/actions/api' {
  const api: {
    summarize: (request: any) => Promise<any>
    convertMarkdown: (request: any) => Promise<any>
  }
  export default api
}

declare module '@/lib/validations' {
  import { z } from 'zod'
  export const summaryFormSchema: z.ZodObject<any>
  export const markdownFormSchema: z.ZodObject<any>
  export type SummaryFormValues = any
  export type MarkdownFormValues = any
}

declare module '@/lib/utils' {
  export function cn(...classes: (string | undefined)[]): string
}
