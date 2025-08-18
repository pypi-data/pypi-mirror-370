import React, { useState, useEffect } from "react";
import { useExecutionStore } from "@/stores/executionStore";
import { Select } from "@/components/ui/Input";
import { cn } from "@/lib/utils";

interface Window {
    window_id: number;
    title: string;
    class_name: string;
    pid: number;
}

export const WindowSelector: React.FC = () => {
    const [windows, setWindows] = useState<Window[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { windowSpec, status } = useExecutionStore();
    const [selectedWindow, setSelectedWindow] = useState<string>(windowSpec || "");

    const isRunning = status === "running" || status === "starting";

    // Fetch windows on mount
    useEffect(() => {
        fetchWindows();
    }, []);

    const fetchWindows = async () => {
        setLoading(true);
        setError(null);

        try {
            const apiUrl = window.electronAPI?.getApiUrl() || "http://127.0.0.1:8777";
            const response = await fetch(`${apiUrl}/windows`);

            if (!response.ok) {
                throw new Error(`Failed to fetch windows: ${response.statusText}`);
            }

            const data = await response.json();
            setWindows(data.windows || []);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Unknown error";
            setError(errorMessage);
            console.error("Failed to fetch windows:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectWindow = (value: string) => {
        setSelectedWindow(value);
        // Update the store
        useExecutionStore.setState({ windowSpec: value || null });
    };

    return (
        <Select
            id="window"
            value={selectedWindow}
            onChange={e => handleSelectWindow(e.target.value)}
            disabled={isRunning || loading}
            className={cn("max-w-xs", error && "border-red-500")}
            title={selectedWindow ? windows.find(w => `id:${w.window_id}` === selectedWindow)?.title : "Full Desktop"}
        >
            <option value="">Full Desktop (No specific window)</option>
            {windows.map(window => {
                const displayTitle =
                    window.title && window.title.length > 40
                        ? `${window.title.substring(0, 40)}...`
                        : window.title || "Untitled";
                return (
                    <option key={window.window_id} value={`id:${window.window_id}`}>
                        {displayTitle} - {window.class_name}
                    </option>
                );
            })}
        </Select>
    );
};
