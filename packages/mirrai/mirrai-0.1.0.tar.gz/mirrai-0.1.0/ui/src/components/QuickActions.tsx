import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { Card } from "@/components/ui/Card";

export const QuickActions: React.FC = () => {
    const { activeTheme } = useTheme();

    return (
        <Card>
            <h3 className={cn("text-sm font-semibold mb-4", activeTheme.text.secondary)}>Quick Actions</h3>
            <div className="space-y-2">
                <button
                    className={cn(
                        "w-full p-3 text-left text-sm rounded-lg transition-all duration-150",
                        activeTheme.execution.quickAction
                    )}
                >
                    <div className="flex items-center justify-between">
                        <span className={activeTheme.text.secondary}>Take Screenshot</span>
                        <kbd className={cn("text-xs", activeTheme.text.muted)}>Ctrl+S</kbd>
                    </div>
                </button>
                <button
                    className={cn(
                        "w-full p-3 text-left text-sm rounded-lg transition-all duration-150",
                        activeTheme.execution.quickAction
                    )}
                >
                    <div className="flex items-center justify-between">
                        <span className={activeTheme.text.secondary}>Refresh Windows</span>
                        <kbd className={cn("text-xs", activeTheme.text.muted)}>Ctrl+R</kbd>
                    </div>
                </button>
                <button
                    className={cn(
                        "w-full p-3 text-left text-sm rounded-lg transition-all duration-150",
                        activeTheme.execution.quickAction
                    )}
                >
                    <div className="flex items-center justify-between">
                        <span className={activeTheme.text.secondary}>Stop Execution</span>
                        <kbd className={cn("text-xs", activeTheme.text.muted)}>Esc</kbd>
                    </div>
                </button>
            </div>
        </Card>
    );
};
