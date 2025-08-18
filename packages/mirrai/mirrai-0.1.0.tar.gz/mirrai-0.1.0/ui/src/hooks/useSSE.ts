import { useEffect, useRef } from "react";
import { useExecutionStore } from "@/stores/executionStore";

export const useSSE = () => {
    const eventSourceRef = useRef<EventSource | null>(null);
    const connectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const { executionId, status, addMessage, addToolUse, updateIteration, setStatus, setError, loadInitialMessages } =
        useExecutionStore();

    useEffect(() => {
        // Only connect if we have an execution ID and status is running
        if (!executionId || status !== "running") {
            // Clean up any existing connection if status is not running
            if (eventSourceRef.current && status !== "running") {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
            return;
        }

        // Prevent multiple connections to the same execution
        if (eventSourceRef.current) {
            return;
        }

        // Add a small delay before connecting to SSE to allow backend to fully initialize
        connectTimeoutRef.current = setTimeout(() => {
            const apiUrl = (window as any).electronAPI?.getApiUrl() || "http://127.0.0.1:8777";

            // Fetch initial state and connect to SSE in parallel
            // This ensures we get history but also don't miss new events

            // Start fetching initial state
            fetch(`${apiUrl}/agent/executions/${executionId}`)
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error("Failed to fetch execution");
                })
                .then(data => {
                    // Load historical messages
                    if (data.messages && data.messages.length > 0) {
                        loadInitialMessages(data.messages);
                    }

                    // Update status if different
                    if (data.status && data.status !== status) {
                        setStatus(data.status);
                    }
                })
                .catch(error => {
                    console.error("Failed to fetch initial execution state:", error);
                    // Continue - SSE is already connecting
                });

            // Connect to SSE immediately (in parallel with fetch)
            const url = `${apiUrl}/agent/executions/${executionId}/stream`;

            // Create EventSource connection
            const eventSource = new EventSource(url);
            eventSourceRef.current = eventSource;

            // Handle open
            eventSource.onopen = () => {
                // Connection established
            };

            // Handle messages
            eventSource.onmessage = event => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case "status":
                            // Handle status updates
                            if (data.data?.status === "completed") {
                                setStatus("completed");
                                eventSource.close();
                                eventSourceRef.current = null;
                            }
                            // Ignore keepalive messages
                            break;

                        case "message":
                            // The actual message data is nested in data.data
                            if (data.data) {
                                const content = data.data.content || "";
                                const role = data.data.role || "assistant";
                                const id = data.data.id;
                                const timestamp = data.data.timestamp ? new Date(data.data.timestamp) : undefined;
                                addMessage(role, content, id, timestamp);
                            }
                            break;

                        case "action":
                        case "tool_use":
                            // Handle both 'action' and 'tool_use' types
                            if (data.data) {
                                const action = data.data.action || data.data.tool || "";

                                // Check if this is an iteration action
                                if (action === "iteration" && data.data.details) {
                                    updateIteration(data.data.details.current || 0, data.data.details.max || 0);
                                    // Don't add iteration actions to the feed, just update the count
                                } else {
                                    // Add non-iteration actions to the feed
                                    addToolUse(action, data.data.details || data.data);
                                }
                            }
                            break;

                        case "iteration":
                            if (data.data) {
                                updateIteration(data.data.current || 0, data.data.max || 0);
                            }
                            break;

                        case "error":
                            setError(data.data?.message || data.message || "Unknown error");
                            eventSource.close();
                            break;

                        case "complete":
                        case "completed":
                            // Handle both 'complete' and 'completed' types
                            addMessage("system", "Task completed successfully");
                            setStatus("completed");
                            eventSource.close();
                            eventSourceRef.current = null;
                            break;

                        default:
                        // Ignore unknown event types
                    }
                } catch (error) {
                    console.error("Failed to parse SSE data:", error);
                }
            };

            // Handle errors
            eventSource.onerror = error => {
                // Prevent automatic reconnection
                if (eventSource.readyState === EventSource.CONNECTING) {
                    eventSource.close();
                    eventSourceRef.current = null;
                }

                // Check if the connection was closed
                if (eventSource.readyState === EventSource.CLOSED) {
                    // If we're still running and this is our current connection,
                    // it might mean the execution completed but we didn't get the event
                    if (status === "running" && eventSourceRef.current === eventSource) {
                        // Fetch the execution status to see if it actually completed
                        fetch(`${apiUrl}/agent/executions/${executionId}`)
                            .then(res => res.json())
                            .then(data => {
                                if (data.status === "completed") {
                                    addMessage("system", "Task completed");
                                    setStatus("completed");
                                } else if (data.status === "failed") {
                                    setError(data.error || "Execution failed");
                                    setStatus("error");
                                } else {
                                    // Still running but connection lost
                                    setError("Connection to execution stream lost");
                                    setStatus("error");
                                }
                            })
                            .catch(err => {
                                setError("Connection lost and unable to check status");
                                setStatus("error");
                            });
                    }

                    eventSourceRef.current = null;
                }
            };
        }, 500); // Wait 500ms before connecting

        // Cleanup
        return () => {
            if (connectTimeoutRef.current) {
                clearTimeout(connectTimeoutRef.current);
                connectTimeoutRef.current = null;
            }
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [executionId, status, addMessage, addToolUse, updateIteration, setStatus, setError, loadInitialMessages]);

    return {
        isConnected: eventSourceRef.current?.readyState === EventSource.OPEN,
    };
};
