import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { TaskInput } from "@/components/TaskInput";
import { WindowSelector } from "@/components/WindowSelector";
import { ExecutionFeed, StatusIndicator } from "@/components/ExecutionFeed";
import { useExecutionStore } from "@/stores/executionStore";
import { useSSE } from "@/hooks/useSSE";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

export function Dashboard() {
    const { activeTheme } = useTheme();
    const { status, currentIteration } = useExecutionStore();
    const { isConnected } = useSSE();

    return (
        <div className="max-w-[1000px] mx-auto space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Command Input</CardTitle>
                    <WindowSelector />
                </CardHeader>
                <CardContent>
                    <TaskInput />
                </CardContent>
            </Card>

            <Card noPadding className="overflow-hidden h-[500px] flex flex-col">
                <div className="px-6 py-4 flex items-center justify-between">
                    <h2 className={cn("text-lg font-semibold", activeTheme.text.primary)}>Execution Log</h2>
                    {status !== "idle" && (
                        <div className="flex items-center space-x-3">
                            {status === "running" && currentIteration > 0 && (
                                <span className={cn("text-xs", activeTheme.text.muted)}>
                                    Iteration {currentIteration}
                                </span>
                            )}
                            <div className="flex items-center space-x-2">
                                <StatusIndicator status={status} isConnected={isConnected} />
                                <span className={cn("text-sm", activeTheme.text.muted)}>
                                    {status === "starting" && "Starting..."}
                                    {status === "running" && "Running"}
                                    {status === "completed" && "Completed"}
                                    {status === "error" && "Error"}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
                <div className="flex-1 p-6 overflow-y-auto">
                    <ExecutionFeed />
                </div>
            </Card>
        </div>
    );
}
