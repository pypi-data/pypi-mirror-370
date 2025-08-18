import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "./ui/Button";
import { useTheme } from "@/hooks/useTheme";
import { baseStyles } from "@/styles/themes/base";

interface SidebarProps {
    className?: string;
}

const SIDEBAR_COLLAPSED_KEY = "sidebarCollapsed";

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
    const [isCollapsed, setIsCollapsed] = useState(() => {
        // Initialize from localStorage
        const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
        return stored === "true";
    });
    const { theme, activeTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();

    // Persist to localStorage whenever collapsed state changes
    useEffect(() => {
        localStorage.setItem(SIDEBAR_COLLAPSED_KEY, isCollapsed.toString());
    }, [isCollapsed]);

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    const expandSidebar = () => {
        if (isCollapsed) {
            setIsCollapsed(false);
        }
    };

    const navItems = [
        { id: "dashboard", label: "Dashboard", icon: HomIcon, path: "/dashboard" },
        { id: "settings", label: "Settings", icon: SettingsIcon, path: "/settings" },
    ];

    return (
        <aside
            className={cn(
                activeTheme.sidebar.base,
                isCollapsed ? baseStyles.layout.sidebarCollapsed : baseStyles.layout.sidebarWidth,
                className
            )}
        >
            {/* Logo Section */}
            <div
                className={cn(
                    baseStyles.layout.headerHeight,
                    "flex items-center",
                    theme === "light" ? "border-b border-black/10" : "border-b border-white/5",
                    isCollapsed ? "px-0" : "px-6"
                )}
            >
                <div className={cn("flex items-center w-full", isCollapsed ? "justify-center" : "justify-between")}>
                    <div
                        className={cn("flex items-center cursor-pointer", isCollapsed ? "justify-center" : "space-x-3")}
                        onClick={expandSidebar}
                    >
                        <div className="w-10 h-10 bg-neutral-600 rounded-lg flex items-center justify-center flex-shrink-0 relative group">
                            <BoltIcon
                                className={cn(
                                    "w-6 h-6 text-white transition-opacity duration-200",
                                    isCollapsed && "group-hover:opacity-0"
                                )}
                            />
                            {isCollapsed && (
                                <ChevronRightIcon className="w-6 h-6 text-white absolute opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                            )}
                        </div>
                        {!isCollapsed && (
                            <div>
                                <h1 className={cn("font-semibold", activeTheme.sidebar.text.primary)}>Mirrai</h1>
                                <p className={cn("text-xs", activeTheme.sidebar.text.muted)}>Desktop Automation</p>
                            </div>
                        )}
                    </div>
                    {!isCollapsed && (
                        <Button variant="icon" onClick={toggleSidebar} className="ml-auto">
                            <ChevronLeftIcon className={cn("w-5 h-5", activeTheme.sidebar.text.muted)} />
                        </Button>
                    )}
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
                {navItems.map(item => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;

                    return (
                        <button
                            key={item.id}
                            onClick={() => {
                                navigate(item.path);
                                // Remove focus from button after navigation
                                (document.activeElement as HTMLElement)?.blur();
                            }}
                            className={cn(
                                isActive ? activeTheme.sidebar.navItemActive : activeTheme.sidebar.navItem,
                                isCollapsed ? "p-0 h-10 w-10 mx-auto justify-center" : "px-4 py-2.5",
                                "focus:outline-none focus-visible:outline-none border-0"
                            )}
                        >
                            <Icon
                                className={cn(activeTheme.sidebar.text.muted, isCollapsed ? "w-5 h-5" : "w-5 h-5 mr-3")}
                            />
                            {!isCollapsed && (
                                <span className={cn("text-sm", activeTheme.sidebar.text.secondary)}>{item.label}</span>
                            )}
                        </button>
                    );
                })}
            </nav>

            {/* Bottom Section */}
            <div className="p-4">
                {/* API Status */}
                <div className={cn("flex items-center", isCollapsed ? "justify-center" : "justify-between px-4")}>
                    {!isCollapsed && <span className={cn("text-xs", activeTheme.sidebar.text.muted)}>API Status</span>}
                    <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse-slow" />
                        {!isCollapsed && <span className={cn("text-xs", activeTheme.status.success)}>Connected</span>}
                    </div>
                </div>
            </div>
        </aside>
    );
};

// Icon Components
const HomIcon: React.FC<React.SVGProps<SVGSVGElement>> = props => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
        <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
        />
    </svg>
);

const BoltIcon: React.FC<React.SVGProps<SVGSVGElement>> = props => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

const SettingsIcon: React.FC<React.SVGProps<SVGSVGElement>> = props => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
        <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
);

const ChevronLeftIcon: React.FC<React.SVGProps<SVGSVGElement>> = props => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
    </svg>
);

const ChevronRightIcon: React.FC<React.SVGProps<SVGSVGElement>> = props => (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
);
