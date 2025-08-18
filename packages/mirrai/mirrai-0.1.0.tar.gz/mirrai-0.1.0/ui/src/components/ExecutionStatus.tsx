import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { useExecutionStore } from "@/stores/executionStore";
import { Card } from "@/components/ui/Card";

export const ExecutionStatus: React.FC = () => {
    const { status } = useExecutionStore();
    const { activeTheme } = useTheme();

    return (
        <Card>
            <h3 className={cn("text-sm font-semibold mb-4", activeTheme.text.secondary)}>Execution Status</h3>
            <div className="space-y-4">
                <div>
                    <div className="flex justify-between text-xs mb-2">
                        <span className={activeTheme.text.muted}>Progress</span>
                        <span className={activeTheme.text.secondary}>7 / 50 steps</span>
                    </div>
                    <div className={cn("w-full rounded-full h-2", activeTheme.layout.progressBar)}>
                        <div
                            className="bg-neutral-600 h-2 rounded-full transition-all duration-150"
                            style={{ width: "14%" }}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <p className={cn("text-xs", activeTheme.text.muted)}>Duration</p>
                        <p className={cn("text-sm font-mono font-medium", activeTheme.text.primary)}>00:04:23</p>
                    </div>
                    <div>
                        <p className={cn("text-xs", activeTheme.text.muted)}>Status</p>
                        <p className={cn("text-sm font-medium", activeTheme.status.warning)}>
                            {status === "idle" && "Ready"}
                            {status === "starting" && "Starting"}
                            {status === "running" && "Running"}
                            {status === "completed" && "Completed"}
                            {status === "error" && "Error"}
                        </p>
                    </div>
                    <div>
                        <p className={cn("text-xs", activeTheme.text.muted)}>CPU Usage</p>
                        <p className={cn("text-sm font-mono font-medium", activeTheme.text.primary)}>12%</p>
                    </div>
                    <div>
                        <p className={cn("text-xs", activeTheme.text.muted)}>Memory</p>
                        <p className={cn("text-sm font-mono font-medium", activeTheme.text.primary)}>2.1GB</p>
                    </div>
                </div>
            </div>
        </Card>
    );
};
