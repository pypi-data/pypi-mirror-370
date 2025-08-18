import React, { useEffect, useRef } from "react";
import { useExecutionStore } from "@/stores/executionStore";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

export const ExecutionFeed: React.FC = () => {
    const { status, messages, toolUses, error } = useExecutionStore();
    const { activeTheme } = useTheme();
    const feedEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, toolUses]);

    if (status === "idle") {
        return (
            <div className={cn("flex items-center justify-center h-full", activeTheme.text.muted)}>
                <p>No execution running. Enter a task above to get started.</p>
            </div>
        );
    }

    return (
        <div className="space-y-3 h-full">
            {/* Error Display */}
            {error && (
                <Badge variant="error" className="w-full p-3">
                    <p className="text-sm">{error}</p>
                </Badge>
            )}

            {/* Combined Messages and Tools Feed - Chronological Order */}
            {[...messages, ...toolUses]
                .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
                .map(item => {
                    // Check if it's a message or tool use based on properties
                    if ("role" in item && "content" in item) {
                        return <MessageCard key={`msg-${item.id}`} message={item} />;
                    } else if ("action" in item) {
                        return <ToolUseCard key={`tool-${item.id}`} toolUse={item} />;
                    }
                    return null;
                })}

            <div ref={feedEndRef} className="h-6" />
        </div>
    );
};

// Status Indicator Component
export const StatusIndicator: React.FC<{ status: string; isConnected: boolean }> = ({ status, isConnected }) => {
    let colorClass = "bg-neutral-400";
    let pulseClass = "";

    if (status === "starting") {
        colorClass = "bg-yellow-500";
        pulseClass = "animate-pulse";
    } else if (status === "running") {
        colorClass = isConnected ? "bg-green-500" : "bg-yellow-500";
        pulseClass = isConnected ? "animate-pulse-slow" : "animate-pulse";
    } else if (status === "completed") {
        colorClass = "bg-green-500";
    } else if (status === "error") {
        colorClass = "bg-red-500";
    }

    return <div className={cn("w-2 h-2 rounded-full", colorClass, pulseClass)} />;
};

// Message Card Component
const MessageCard: React.FC<{ message: any }> = ({ message }) => {
    const { activeTheme } = useTheme();
    const isUser = message.role === "user";
    const isAssistant = message.role === "assistant";
    const isSystem = message.role === "system";

    return (
        <div className="flex items-start space-x-3">
            <div
                className={cn(
                    "w-1 h-full rounded-full",
                    isSystem && "bg-neutral-600",
                    isAssistant && "bg-neutral-500",
                    isUser && "bg-neutral-400"
                )}
            />
            <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                    <span className={cn("text-xs font-medium", activeTheme.text.muted)}>
                        {(message.role || "unknown").toUpperCase()}
                    </span>
                    <span className={cn("text-xs font-mono", activeTheme.text.muted)}>
                        {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ""}
                    </span>
                </div>
                <p className={cn("text-sm", activeTheme.text.primary)}>{message.content || ""}</p>
            </div>
        </div>
    );
};

// Tool Use Card Component
const ToolUseCard: React.FC<{ toolUse: any }> = ({ toolUse }) => {
    const { activeTheme } = useTheme();
    const actionIcons: Record<string, string> = {
        screenshot: "📸",
        left_click: "👆",
        right_click: "👆",
        middle_click: "👆",
        double_click: "👆",
        type_text: "⌨️",
        key: "⌨️",
        scroll: "📜",
        drag: "✋",
        wait: "⏱️",
    };

    const icon = actionIcons[toolUse.action] || "🔧";

    return (
        <div className={cn("ml-4 p-3 rounded-lg", activeTheme.execution.toolAction)}>
            <div className="flex items-center justify-between mb-2">
                <Badge variant="tool">
                    <span className="mr-1">{icon}</span>
                    {toolUse.action}
                </Badge>
                <span className={cn("text-xs font-mono", activeTheme.text.muted)}>
                    {new Date(toolUse.timestamp).toLocaleTimeString()}
                </span>
            </div>
            {toolUse.details && Object.keys(toolUse.details).length > 0 && (
                <div className={cn("text-xs font-mono space-y-1", activeTheme.text.muted)}>
                    {Object.entries(toolUse.details).map(([key, value]) => (
                        <div key={key}>
                            {key}: {JSON.stringify(value)}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
