'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter
} from '@/components/ui/card'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Loader2, Info } from 'lucide-react'
import api from '@/lib/actions/api'
import MarkdownResult from '@/components/result/markdown-result'
import { markdownFormSchema, type MarkdownFormValues } from '@/lib/validations'

export default function MarkdownForm() {
  const [activeTab, setActiveTab] = useState<'to_markdown' | 'to_text'>(
    'to_markdown'
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<MarkdownResponse | null>(null)
  const [showInfo, setShowInfo] = useState(true)

  // Initialize the form
  const form = useForm<MarkdownFormValues>({
    resolver: zodResolver(markdownFormSchema),
    defaultValues: {
      text: '',
      mode: 'to_markdown'
    } as MarkdownFormValues
  })

  // When tab changes, update the form value
  const handleTabChange = (value: string) => {
    setActiveTab(value as 'to_markdown' | 'to_text')
    form.setValue('mode', value as 'to_markdown' | 'to_text')
    setShowInfo(true) // Show info when changing modes
  }

  // Form submission handler
  const onSubmit = async (values: MarkdownFormValues) => {
    setIsSubmitting(true)
    setError(null)

    try {
      const request: MarkdownRequest = {
        text: values.text,
        mode: values.mode
      }

      const response = await api.convertMarkdown(request)
      setResult(response)
    } catch (err) {
      setError('An error occurred while converting the text. Please try again.')
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Examples for each mode
  const examples = {
    to_markdown: `This is a paragraph of text.

This is another paragraph with some **important** information.

Here's a code example:

def hello_world():
    print("Hello, world!")
    return True

And a list:
1. First item
2. Second item
3. Third item`,

    to_text: `# Main Heading

## Subheading

This is a paragraph with **bold text** and *italic text*.

- List item 1
- List item 2
- List item 3

\`\`\`py
def example_function():
    return "This is a code block"
\`\`\`

Here's an \`<inline>\` HTML tag.`
  }

  // Load example into form
  const loadExample = () => {
    form.setValue('text', examples[activeTab])
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Markdown Converter</CardTitle>
          <CardDescription>
            Convert between plain text and Markdown format
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs
            defaultValue="to_markdown"
            value={activeTab}
            onValueChange={handleTabChange}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="to_markdown">Text to Markdown</TabsTrigger>
              <TabsTrigger value="to_text">Markdown to Text</TabsTrigger>
            </TabsList>

            {showInfo && (
              <Alert className="mt-4">
                <Info className="h-4 w-4" />
                <AlertTitle>
                  {activeTab === 'to_markdown'
                    ? 'Text to Markdown'
                    : 'Markdown to Text'}{' '}
                  Mode
                </AlertTitle>
                <AlertDescription>
                  {activeTab === 'to_markdown' ? (
                    <div className="text-sm">
                      <p>
                        This mode converts plain text to Markdown format. The
                        converter will:
                      </p>
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        <li>
                          Detect code blocks and wrap them in ```py ``` for
                          Python code
                        </li>
                        <li>
                          Format single HTML tags with backticks like
                          `&lt;div&gt;`
                        </li>
                        <li>Identify headings and format them appropriately</li>
                        <li>Detect lists and maintain their formatting</li>
                        <li>Convert URLs to proper Markdown links</li>
                      </ul>
                    </div>
                  ) : (
                    <div className="text-sm">
                      <p>This mode converts Markdown to plain text. It will:</p>
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        <li>Convert Markdown formatting to simple text</li>
                        <li>Preserve code blocks with proper spacing</li>
                        <li>
                          Format lists with appropriate numbers or bullets
                        </li>
                        <li>Convert links to show both text and URL</li>
                      </ul>
                    </div>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={loadExample}
                  >
                    Load Example
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2 ml-2"
                    onClick={() => setShowInfo(false)}
                  >
                    Dismiss
                  </Button>
                </AlertDescription>
              </Alert>
            )}

            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-6 pt-4"
              >
                <FormField
                  control={form.control}
                  name="text"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        {activeTab === 'to_markdown'
                          ? 'Plain Text to Convert'
                          : 'Markdown to Convert'}
                      </FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder={
                            activeTab === 'to_markdown'
                              ? 'Enter plain text here...'
                              : 'Enter markdown here...'
                          }
                          className="min-h-32 font-mono"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Converting...
                    </>
                  ) : activeTab === 'to_markdown' ? (
                    'Convert to Markdown'
                  ) : (
                    'Convert to Plain Text'
                  )}
                </Button>
              </form>
            </Form>
          </Tabs>
        </CardContent>
        <CardFooter className="text-xs text-muted-foreground">
          {activeTab === 'to_markdown' ? (
            <p>
              Our converter detects code blocks and wraps them in triple
              backticks with language identifiers. Python code will be wrapped
              in ```py ... ``` automatically.
            </p>
          ) : (
            <p>
              When converting from Markdown, formatting such as bold, italic,
              and headings will be converted to plain text while preserving the
              overall structure.
            </p>
          )}
        </CardFooter>
      </Card>

      {result && (
        <div className="mt-8">
          <MarkdownResult
            result={result.result}
            originalText={form.getValues().text}
            mode={form.getValues().mode}
          />
        </div>
      )}
    </div>
  )
}
