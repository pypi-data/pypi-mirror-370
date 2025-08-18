import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { Card } from "@/components/ui/Card";

export const RecentTasks: React.FC = () => {
    const { activeTheme } = useTheme();

    return (
        <Card>
            <h3 className={cn("text-sm font-semibold mb-4", activeTheme.text.secondary)}>Recent Tasks</h3>
            <div className="space-y-3">
                <div className="flex items-start space-x-3">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5" />
                    <div className="flex-1">
                        <p className={cn("text-sm", activeTheme.text.secondary)}>Enable dark mode</p>
                        <p className={cn("text-xs", activeTheme.text.muted)}>2 minutes ago • 4.2s</p>
                    </div>
                </div>
                <div className="flex items-start space-x-3">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-1.5" />
                    <div className="flex-1">
                        <p className={cn("text-sm", activeTheme.text.secondary)}>Extract table data</p>
                        <p className={cn("text-xs", activeTheme.text.muted)}>15 minutes ago • 6.8s</p>
                    </div>
                </div>
                <div className="flex items-start space-x-3">
                    <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5" />
                    <div className="flex-1">
                        <p className={cn("text-sm", activeTheme.text.secondary)}>Fill form fields</p>
                        <p className={cn("text-xs", activeTheme.text.muted)}>1 hour ago • Failed</p>
                    </div>
                </div>
            </div>
        </Card>
    );
};
