import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { Dashboard } from "@/pages/Dashboard";
import { Settings } from "@/pages/Settings";
import { AnimatedRoute } from "@/components/AnimatedRoute";

export function AppRoutes() {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route
                    path="/dashboard"
                    element={
                        <AnimatedRoute>
                            <Dashboard />
                        </AnimatedRoute>
                    }
                />
                <Route
                    path="/settings"
                    element={
                        <AnimatedRoute>
                            <Settings />
                        </AnimatedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </AnimatePresence>
    );
}
