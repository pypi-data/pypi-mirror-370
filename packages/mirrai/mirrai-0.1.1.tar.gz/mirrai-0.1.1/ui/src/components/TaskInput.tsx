import React, { useState } from "react";
import { useExecutionStore } from "@/stores/executionStore";
import { Textarea } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export const TaskInput: React.FC = () => {
    const [task, setTask] = useState("");
    const { status, startExecution, windowSpec, task: executingTask } = useExecutionStore();

    const isRunning = status === "running" || status === "starting";

    // Clear the input when status changes to idle (after completion/error)
    React.useEffect(() => {
        if (status === "idle") {
            setTask("");
        }
    }, [status]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!task.trim() || isRunning) return;

        try {
            await startExecution(task, windowSpec || undefined);
            // Don't clear the task - keep it visible while running
        } catch (error) {
            console.error("Failed to start execution:", error);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        // Submit on Ctrl/Cmd + Enter
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full">
            <div className="space-y-4">
                <Textarea
                    id="task"
                    value={isRunning && executingTask ? executingTask : task}
                    onChange={e => setTask(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Describe the automation task you want to perform..."
                    className="min-h-[80px]"
                    disabled={isRunning}
                    readOnly={isRunning}
                    autoFocus
                />

                <div className="flex items-center justify-end space-x-2">
                    <Button type="button" variant="ghost" size="sm" onClick={() => setTask("")}>
                        Clear
                    </Button>
                    <Button type="submit" disabled={!task.trim() || isRunning} size="sm">
                        {isRunning ? (
                            <span className="flex items-center">
                                <svg
                                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        className="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                    ></circle>
                                    <path
                                        className="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    ></path>
                                </svg>
                                Running...
                            </span>
                        ) : (
                            "Execute Task"
                        )}
                    </Button>
                </div>
            </div>
        </form>
    );
};
