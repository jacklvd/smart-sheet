'use client'

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Check } from 'lucide-react'

interface SummaryResultProps {
  result: SummaryResponse
  originalText: string
}

export default function SummaryResult({
  result,
  originalText
}: SummaryResultProps) {
  const [copied, setCopied] = useState(false)

  // Calculate reduction percentage if it doesn't exist in the result
  const reductionPercentage =
    result.reduction_percentage !== undefined
      ? result.reduction_percentage
      : result.original_length > 0
        ? ((result.original_length - result.summary_length) /
            result.original_length) *
          100
        : 0

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Summary Result</CardTitle>
        <CardDescription>
          Reduced by {reductionPercentage.toFixed(1)}% (from{' '}
          {result.original_length} to {result.summary_length} words)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="original">Original Text</TabsTrigger>
          </TabsList>
          <TabsContent value="summary" className="pt-4">
            <div className="relative">
              <div className="bg-muted p-4 rounded-md whitespace-pre-wrap">
                {result.summary}
              </div>
              <Button
                variant="outline"
                size="icon"
                className="absolute top-2 right-2"
                onClick={() => copyToClipboard(result.summary)}
              >
                {copied ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </TabsContent>
          <TabsContent value="original" className="pt-4">
            <div className="bg-muted p-4 rounded-md max-h-96 overflow-y-auto whitespace-pre-wrap">
              {originalText}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
