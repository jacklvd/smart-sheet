'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import api from '@/lib/actions/sheet.actions'
import SummaryResult from '@/components/result/summary-result'
import { summaryFormSchema, type SummaryFormValues } from '@/lib/validations'

export default function SummaryForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SummaryResponse | null>(null)

  // Initialize the form
  const form = useForm<SummaryFormValues>({
    resolver: zodResolver(summaryFormSchema),
    defaultValues: {
      text: '',
      type: 'concise',
      max_length: undefined
    }
  })

  // Form submission handler
  const onSubmit = async (values: SummaryFormValues) => {
    setIsSubmitting(true)
    setError(null)

    try {
      const request: SummaryRequest = {
        text: values.text,
        type: values.type,
        max_length: values.max_length
      }

      const response = await api.summarize(request)
      setResult(response)
    } catch (err) {
      setError(
        'An error occurred while summarizing the text. Please try again.'
      )
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Summarize Text</CardTitle>
          <CardDescription>
            Paste your content below to generate a smart summary
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content to Summarize</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Paste your text here..."
                        className="min-h-32"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex flex-col sm:flex-row gap-4">
                <FormField
                  control={form.control}
                  name="type"
                  render={({ field }) => (
                    <FormItem className="flex-1">
                      <FormLabel>Summary Type</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select summary type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="concise">Concise</SelectItem>
                          <SelectItem value="detailed">Detailed</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="max_length"
                  render={({ field }) => (
                    <FormItem className="flex-1">
                      <FormLabel>Max Length (optional)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="Maximum words"
                          {...field}
                          onChange={(e) =>
                            field.onChange(
                              e.target.value === ''
                                ? undefined
                                : parseInt(e.target.value)
                            )
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Summarizing...
                  </>
                ) : (
                  'Generate Summary'
                )}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {result && (
        <div className="mt-8">
          <SummaryResult result={result} originalText={form.getValues().text} />
        </div>
      )}
    </div>
  )
}
