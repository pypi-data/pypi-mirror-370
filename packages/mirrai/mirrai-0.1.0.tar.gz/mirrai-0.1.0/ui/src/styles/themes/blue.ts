import { ThemeDefinition } from "./index";
import { cn } from "@/lib/utils";
import { baseStyles } from "./base";

export const blueTheme: ThemeDefinition = {
    card: {
        default: cn(
            "bg-gradient-to-br from-blue-50/50 to-indigo-50/50 border border-blue-200/50",
            baseStyles.rounded.lg,
            baseStyles.spacing.card
        ),
        hover: cn(
            "bg-gradient-to-br from-blue-50/50 to-indigo-50/50 border border-blue-200/50",
            "hover:from-blue-50/70 hover:to-indigo-50/70 hover:border-blue-300/50 hover:shadow-lg hover:shadow-blue-100/50",
            baseStyles.rounded.lg,
            baseStyles.spacing.card,
            baseStyles.transitions.default
        ),
        transparent: cn("bg-transparent border-0", baseStyles.rounded.lg),
    },

    button: {
        primary: cn(
            "bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white",
            "shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30",
            "hover:-translate-y-[1px] active:translate-y-0",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none",
            baseStyles.font.medium,
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        ghost: cn(
            "bg-transparent hover:bg-blue-50 text-blue-700",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        icon: cn(
            "bg-transparent hover:bg-blue-50 text-blue-600 p-2",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
    },

    badge: {
        default: cn(
            "bg-blue-100 border-blue-300 text-blue-700",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        success: cn(
            "bg-emerald-100 border-emerald-300 text-emerald-700",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        warning: cn(
            "bg-amber-100 border-amber-300 text-amber-700",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        error: cn(
            "bg-rose-100 border-rose-300 text-rose-700",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        tool: cn(
            "bg-indigo-100 border-indigo-300 text-indigo-700",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
    },

    input: {
        input: cn(
            "w-full bg-white/80 border border-blue-200",
            "text-blue-900 placeholder:text-blue-400",
            "focus:bg-white focus:border-blue-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/20",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        textarea: cn(
            "w-full bg-white/80 border border-blue-200",
            "text-blue-900 placeholder:text-blue-400",
            "focus:bg-white focus:border-blue-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/20",
            "disabled:opacity-50 disabled:cursor-not-allowed resize-none",
            baseStyles.spacing.textarea,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        select: cn(
            "bg-white/80 border border-blue-200",
            "text-blue-900",
            "focus:bg-white focus:border-blue-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500/20",
            "disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
    },

    sidebar: {
        base: cn(
            "bg-gradient-to-b from-blue-600 to-indigo-700",
            "border-r border-white/10",
            "flex flex-col",
            baseStyles.effects.backdropBlur,
            baseStyles.transitions.slow
        ),
        navItem: cn("w-full flex items-center", "hover:bg-white/10", baseStyles.rounded.md),
        navItemActive: cn("w-full flex items-center", "bg-white/15", baseStyles.rounded.md),
        text: {
            primary: "text-white",
            secondary: "text-white/90",
            muted: "text-white/70",
        },
    },

    layout: {
        background: "bg-gradient-to-br from-blue-50 via-white to-indigo-50",
        header: cn(
            "border-b border-blue-200/50",
            baseStyles.layout.headerHeight,
            "px-6 flex items-center justify-between"
        ),
        gridPattern: cn(
            "absolute inset-0 opacity-30",
            "bg-[linear-gradient(rgba(59,130,246,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.05)_1px,transparent_1px)]",
            "bg-[size:32px_32px]"
        ),
        progressBar: "bg-blue-100",
    },

    text: {
        primary: "text-blue-900",
        secondary: "text-blue-800", // Better contrast
        muted: "text-blue-600", // Better contrast
        inverse: "text-white",
    },

    status: {
        success: "text-emerald-600",
        warning: "text-amber-600",
        error: "text-rose-600",
        info: "text-blue-600",
    },

    execution: {
        statusBar: "bg-blue-100/50",
        taskDisplay: "bg-blue-50/70",
        toolAction: "bg-gradient-to-br from-blue-50/50 to-indigo-50/50 border border-blue-200/50",
        quickAction: cn(
            "bg-gradient-to-br from-blue-50/30 to-indigo-50/30 border border-blue-200/50",
            "hover:from-blue-50/50 hover:to-indigo-50/50 hover:border-blue-300/50"
        ),
    },
};
