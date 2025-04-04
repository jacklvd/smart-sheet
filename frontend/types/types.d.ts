// Types
interface SummaryRequest {
  text: string
  max_length?: number
  type?: 'concise' | 'detailed'
}

interface SummaryResponse {
  summary: string
  original_length: number
  summary_length: number
  reduction_percentage?: number // Make this optional
  id?: number // If you have this field
}

interface MarkdownRequest {
  text: string
  mode: 'to_markdown' | 'to_text'
}

interface MarkdownResponse {
  result: string
}
