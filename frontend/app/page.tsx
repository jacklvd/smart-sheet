"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import SummaryForm from "@/components/form/summary-form";
import MarkdownForm from "@/components/form/markdown-form";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("summarize");

  return (
    <main className="container mx-auto py-10 px-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold tracking-tight">Smart Content Tool</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Summarize content and convert between text and markdown formats
        </p>
      </div>

      <Tabs
        defaultValue="summarize"
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full max-w-3xl mx-auto"
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="summarize">Text Summarizer</TabsTrigger>
          <TabsTrigger value="markdown">Markdown Converter</TabsTrigger>
        </TabsList>
        <TabsContent value="summarize" className="pt-6">
          <SummaryForm />
        </TabsContent>
        <TabsContent value="markdown" className="pt-6">
          <MarkdownForm />
        </TabsContent>
      </Tabs>
    </main>
  );
}