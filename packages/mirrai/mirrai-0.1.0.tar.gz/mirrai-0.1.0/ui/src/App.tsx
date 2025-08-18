import { BrowserRouter as Router } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import { AppRoutes } from "@/components/AppRoutes";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

function App() {
    const { activeTheme } = useTheme();

    return (
        <Router>
            <div className={cn("h-screen flex overflow-hidden", activeTheme.layout.background)}>
                {/* Grid background pattern */}
                <div className={activeTheme.layout.gridPattern} />

                {/* Main Layout Container */}
                <div className="relative flex w-full h-full">
                    {/* Sidebar */}
                    <Sidebar />

                    {/* Main Content Area */}
                    <main className="flex-1 flex flex-col overflow-hidden">
                        {/* Header */}
                        <header className={activeTheme.layout.header}>
                            <div>
                                <h1 className={cn("text-lg font-bold", activeTheme.text.primary)}>
                                    Automation Control
                                </h1>
                                <p className={cn("text-xs", activeTheme.text.muted)}>
                                    Execute and monitor desktop automation tasks
                                </p>
                            </div>
                        </header>

                        {/* Content Area */}
                        <div className="flex-1 p-6 overflow-y-auto">
                            <AppRoutes />
                        </div>
                    </main>
                </div>
            </div>
        </Router>
    );
}

export default App;
