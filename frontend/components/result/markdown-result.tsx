/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Card, CardDescription, CardHeader, CardTitle, CardFooter, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Copy, Check, Eye, Code, Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface MarkdownResultProps {
    result: string;
    originalText: string;
    mode: "to_markdown" | "to_text";
}

export default function MarkdownResult({ result, originalText, mode }: MarkdownResultProps) {
    const [copied, setCopied] = useState(false);
    const [viewType, setViewType] = useState<"preview" | "code">(
        mode === "to_markdown" ? "preview" : "code"
    );

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Custom components for ReactMarkdown
    const components: any = {
        code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
                <div className="rounded-md overflow-hidden my-4">
                    <div className="bg-gray-800 text-white text-xs px-4 py-1.5 flex items-center justify-between">
                        <span>{match[1].toUpperCase()}</span>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 text-xs text-gray-300 hover:text-white"
                            onClick={() => copyToClipboard(String(children).replace(/\n$/, ''))}
                        >
                            {copied ? <Check className="h-3 w-3 mr-1" /> : <Copy className="h-3 w-3 mr-1" />}
                            {copied ? "Copied" : "Copy"}
                        </Button>
                    </div>
                    <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        className="m-0"
                        {...props}
                    >
                        {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                </div>
            ) : (
                <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm" {...props}>
                    {children}
                </code>
            );
        },
        a({ children, ...props }: any) {
            return (
                <a
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                    {...props}
                >
                    {children}
                </a>
            );
        },
        ul({ children, ...props }: any) {
            return (
                <ul className="list-disc pl-6 my-4 space-y-2" {...props}>
                    {children}
                </ul>
            );
        },
        ol({ children, ...props }: any) {
            return (
                <ol className="list-decimal pl-6 my-4 space-y-2" {...props}>
                    {children}
                </ol>
            );
        },
        li({ children, ...props }: any) {
            return (
                <li className="my-1" {...props}>
                    {children}
                </li>
            );
        },
        h1({ children, ...props }: any) {
            return (
                <h1 className="text-2xl font-bold mt-6 mb-4" {...props}>
                    {children}
                </h1>
            );
        },
        h2({ children, ...props }: any) {
            return (
                <h2 className="text-xl font-bold mt-5 mb-3" {...props}>
                    {children}
                </h2>
            );
        },
        h3({ children, ...props }: any) {
            return (
                <h3 className="text-lg font-bold mt-4 mb-2" {...props}>
                    {children}
                </h3>
            );
        },
        blockquote({ children, ...props }: any) {
            return (
                <blockquote className="border-l-4 border-gray-300 dark:border-gray-700 pl-4 py-1 my-4 italic text-gray-700 dark:text-gray-300" {...props}>
                    {children}
                </blockquote>
            );
        },
        table({ children, ...props }: any) {
            return (
                <div className="overflow-x-auto my-6">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700" {...props}>
                        {children}
                    </table>
                </div>
            );
        },
        thead({ children, ...props }: any) {
            return (
                <thead className="bg-gray-50 dark:bg-gray-800" {...props}>
                    {children}
                </thead>
            );
        },
        tbody({ children, ...props }: any) {
            return (
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700" {...props}>
                    {children}
                </tbody>
            );
        },
        tr({ children, ...props }: any) {
            return (
                <tr className="hover:bg-gray-50 dark:hover:bg-gray-800" {...props}>
                    {children}
                </tr>
            );
        },
        th({ children, ...props }: any) {
            return (
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" {...props}>
                    {children}
                </th>
            );
        },
        td({ children, ...props }: any) {
            return (
                <td className="px-4 py-3 whitespace-nowrap text-sm" {...props}>
                    {children}
                </td>
            );
        },
    };

    return (
        <Card className="shadow-md border-gray-200 dark:border-gray-800 pointer-events-auto">
            <CardHeader className="pb-3 dark:bg-gray-900 border-b dark:border-gray-800">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                        <CardTitle className="text-xl font-bold flex items-center">
                            Conversion Result
                            <Badge variant="outline" className="ml-2 text-xs font-normal">
                                {mode === "to_markdown" ? "Markdown" : "Plain Text"}
                            </Badge>
                        </CardTitle>
                        <CardDescription className="mt-1">
                            {mode === "to_markdown"
                                ? "Text converted to Markdown format"
                                : "Markdown converted to plain text"}
                        </CardDescription>
                    </div>

                    {mode === "to_markdown" && (
                        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1 self-start sm:self-center">
                            <Button
                                variant="ghost"
                                size="sm"
                                className={cn(
                                    "rounded-md transition-all",
                                    viewType === "preview" ? "bg-white dark:bg-gray-700 shadow-sm" : "hover:bg-gray-200 dark:hover:bg-gray-700"
                                )}
                                onClick={() => setViewType("preview")}
                            >
                                <Eye className="h-4 w-4 mr-1.5" />
                                Preview
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                className={cn(
                                    "rounded-md transition-all",
                                    viewType === "code" ? "bg-white dark:bg-gray-700 shadow-sm" : "hover:bg-gray-200 dark:hover:bg-gray-700"
                                )}
                                onClick={() => setViewType("code")}
                            >
                                <Code className="h-4 w-4 mr-1.5" />
                                Markdown
                            </Button>
                        </div>
                    )}
                </div>
            </CardHeader>

            <Tabs defaultValue="result" className="w-full">
                <TabsList className="w-full rounded bg-gray-100 dark:bg-gray-900 p-2 mb-0">
                    <TabsTrigger
                        value="result"
                        className="rounded data-[state=active]:bg-white dark:data-[state=active]:bg-gray-800 flex-1 py-3 border-b-2 data-[state=active]:border-primary data-[state=inactive]:border-transparent"
                    >
                        Result
                    </TabsTrigger>
                    <TabsTrigger
                        value="original"
                        className="rounded data-[state=active]:bg-white dark:data-[state=active]:bg-gray-800 flex-1 py-3 border-b-2 data-[state=active]:border-primary data-[state=inactive]:border-transparent"
                    >
                        Original
                    </TabsTrigger>
                </TabsList>

                <CardContent className="p-0">
                    <TabsContent value="result" className="mt-0 p-0">
                        {mode === "to_markdown" && viewType === "preview" ? (
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-bl-md rounded-br-md">
                                <div className="prose dark:prose-invert max-w-none">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={components}
                                    >
                                        {result}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white dark:bg-gray-800 p-6 rounded-bl-md rounded-br-md">
                                <div className="relative">
                                    <div className="border border-gray-200 dark:border-gray-700 p-4 rounded-md whitespace-pre-wrap font-mono text-sm overflow-x-auto max-h-[500px] overflow-y-auto">
                                        {result}
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="absolute top-3 right-3 h-8 bg-white dark:bg-gray-700 shadow-sm"
                                        onClick={() => copyToClipboard(result)}
                                    >
                                        {copied ? <Check className="h-3.5 w-3.5 mr-1.5" /> : <Copy className="h-3.5 w-3.5 mr-1.5" />}
                                        {copied ? "Copied!" : "Copy"}
                                    </Button>
                                </div>
                            </div>
                        )}
                    </TabsContent>
                    <TabsContent value="original" className="mt-0 p-0">
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-bl-md rounded-br-md">
                            <div className="border border-gray-200 dark:border-gray-700 p-4 rounded-md max-h-[500px] overflow-y-auto whitespace-pre-wrap font-mono text-sm">
                                {originalText}
                            </div>
                        </div>
                    </TabsContent>
                </CardContent>
            </Tabs>

            <CardFooter className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 px-6 py-3">
                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                    <Info className="h-3.5 w-3.5 mr-1.5" />
                    {mode === "to_markdown" ? (
                        viewType === "preview" ?
                            "This is a rendered preview of the Markdown. Switch to 'Markdown' to see the raw format." :
                            "This is the raw Markdown format. Switch to 'Preview' to see how it renders."
                    ) : (
                        "Markdown formatting has been converted to plain text."
                    )}
                </div>
            </CardFooter>
        </Card>
    );
}