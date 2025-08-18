import { ThemeDefinition } from "./index";
import { cn } from "@/lib/utils";
import { baseStyles } from "./base";

export const lightTheme: ThemeDefinition = {
    card: {
        default: cn("bg-black/[0.02] border border-black/[0.06]", baseStyles.rounded.lg, baseStyles.spacing.card),
        hover: cn(
            "bg-black/[0.02] border border-black/[0.06]",
            "hover:bg-black/[0.04] hover:border-black/10",
            baseStyles.rounded.lg,
            baseStyles.spacing.card,
            baseStyles.transitions.default
        ),
        transparent: cn("bg-transparent border-0", baseStyles.rounded.lg),
    },

    button: {
        primary: cn(
            "bg-neutral-600 hover:bg-neutral-500 text-white",
            "hover:shadow-lg hover:-translate-y-[1px] active:translate-y-0",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none",
            baseStyles.font.medium,
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        ghost: cn(
            "bg-transparent hover:bg-black/5 text-neutral-700",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        icon: cn(
            "bg-transparent hover:bg-black/5 text-neutral-500 p-2",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
    },

    badge: {
        default: cn(
            "bg-white/5 border-white/10 text-neutral-600",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        success: cn(
            "bg-green-500/10 border-green-500/30 text-green-600",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        warning: cn(
            "bg-yellow-500/10 border-yellow-500/30 text-yellow-600",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        error: cn(
            "bg-red-500/10 border-red-500/30 text-red-600",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        tool: cn(
            "bg-white/5 border-white/10 text-neutral-500",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
    },

    input: {
        input: cn(
            "w-full bg-white/80 border border-black/10",
            "text-neutral-900 placeholder:text-neutral-500",
            "focus:bg-white/95 focus:border-neutral-500",
            "focus:outline-none focus:ring-2 focus:ring-black/5",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        textarea: cn(
            "w-full bg-white/80 border border-black/10",
            "text-neutral-900 placeholder:text-neutral-500",
            "focus:bg-white/95 focus:border-neutral-500",
            "focus:outline-none focus:ring-2 focus:ring-black/5",
            "disabled:opacity-50 disabled:cursor-not-allowed resize-none",
            baseStyles.spacing.textarea,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        select: cn(
            "bg-white/80 border border-black/10",
            "text-neutral-900",
            "focus:bg-white/95 focus:border-neutral-500",
            "focus:outline-none focus:ring-2 focus:ring-black/5",
            "disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
    },

    sidebar: {
        base: cn(
            "bg-white/80",
            "border-r border-black/10",
            "flex flex-col",
            baseStyles.effects.backdropBlur,
            baseStyles.transitions.slow
        ),
        navItem: cn("w-full flex items-center", "hover:bg-black/5", baseStyles.rounded.md),
        navItemActive: cn("w-full flex items-center", "bg-black/[0.03]", baseStyles.rounded.md),
        text: {
            primary: "text-neutral-900",
            secondary: "text-neutral-700",
            muted: "text-neutral-500",
        },
    },

    layout: {
        background: "bg-neutral-50",
        header: cn(
            "border-b border-black/10",
            baseStyles.layout.headerHeight,
            "px-6 flex items-center justify-between"
        ),
        gridPattern: cn(
            "absolute inset-0 opacity-50",
            "bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)]",
            "bg-[size:32px_32px]"
        ),
        progressBar: "bg-neutral-200",
    },

    text: {
        primary: "text-neutral-900",
        secondary: "text-neutral-700",
        muted: "text-neutral-500",
        inverse: "text-white",
    },

    status: {
        success: "text-green-600",
        warning: "text-yellow-600",
        error: "text-red-600",
        info: "text-blue-600",
    },

    execution: {
        statusBar: "bg-black/5",
        taskDisplay: "bg-neutral-100",
        toolAction: "bg-black/[0.02] border border-black/[0.06]",
        quickAction: cn("bg-black/[0.02] border border-black/[0.06]", "hover:bg-black/[0.04] hover:border-black/10"),
    },
};
