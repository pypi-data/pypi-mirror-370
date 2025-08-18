import { ThemeDefinition } from "./index";
import { cn } from "@/lib/utils";
import { baseStyles } from "./base";

export const darkTheme: ThemeDefinition = {
    card: {
        default: cn("bg-white/[0.03] border border-white/[0.08]", baseStyles.rounded.lg, baseStyles.spacing.card),
        hover: cn(
            "bg-white/[0.02] border border-white/[0.06]",
            "hover:bg-white/[0.04] hover:border-white/10",
            baseStyles.rounded.lg,
            baseStyles.spacing.card,
            baseStyles.transitions.default
        ),
        transparent: cn("bg-transparent border-0", baseStyles.rounded.lg),
    },

    button: {
        primary: cn(
            "bg-neutral-600 hover:bg-neutral-700 text-white",
            "hover:shadow-lg hover:-translate-y-[1px] active:translate-y-0",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none",
            baseStyles.font.medium,
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        ghost: cn(
            "bg-transparent hover:bg-white/5 text-neutral-300",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
        icon: cn(
            "bg-transparent hover:bg-white/5 text-neutral-400 p-2",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.rounded.md,
            baseStyles.transitions.default
        ),
    },

    badge: {
        default: cn(
            "bg-white/5 border-white/10 text-neutral-400",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        success: cn(
            "bg-green-500/10 border-green-500/30 text-green-400",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        warning: cn(
            "bg-yellow-500/10 border-yellow-500/30 text-yellow-400",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        error: cn(
            "bg-red-500/10 border-red-500/30 text-red-400",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
        tool: cn(
            "bg-white/5 border-white/10 text-neutral-400",
            "inline-flex items-center px-3 py-1.5",
            "border rounded-md",
            "text-xs font-medium"
        ),
    },

    input: {
        input: cn(
            "w-full bg-black/30 border border-white/10",
            "text-white placeholder:text-neutral-500",
            "focus:bg-black/50 focus:border-neutral-600",
            "focus:outline-none focus:ring-2 focus:ring-white/5",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        textarea: cn(
            "w-full bg-black/30 border border-white/10",
            "text-white placeholder:text-neutral-500",
            "focus:bg-black/50 focus:border-neutral-600",
            "focus:outline-none focus:ring-2 focus:ring-white/5",
            "disabled:opacity-50 disabled:cursor-not-allowed resize-none",
            baseStyles.spacing.textarea,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
        select: cn(
            "bg-black/30 border border-white/10",
            "text-white",
            "focus:bg-black/50 focus:border-neutral-600",
            "focus:outline-none focus:ring-2 focus:ring-white/5",
            "disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
            baseStyles.spacing.input,
            baseStyles.rounded.md,
            baseStyles.text.sm,
            baseStyles.transitions.default
        ),
    },

    sidebar: {
        base: cn(
            "bg-black/40",
            "border-r border-white/5",
            "flex flex-col",
            baseStyles.effects.backdropBlur,
            baseStyles.transitions.slow
        ),
        navItem: cn("w-full flex items-center", "hover:bg-white/5", baseStyles.rounded.md),
        navItemActive: cn("w-full flex items-center", "bg-white/[0.03]", baseStyles.rounded.md),
        text: {
            primary: "text-white",
            secondary: "text-neutral-300",
            muted: "text-neutral-400",
        },
    },

    layout: {
        background: "bg-neutral-900",
        header: cn("border-b border-white/5", baseStyles.layout.headerHeight, "px-6 flex items-center justify-between"),
        gridPattern: cn(
            "absolute inset-0 opacity-50",
            "bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)]",
            "bg-[size:32px_32px]"
        ),
        progressBar: "bg-neutral-800",
    },

    text: {
        primary: "text-white",
        secondary: "text-white/90", // More contrast - closer to white
        muted: "text-neutral-400",
        inverse: "text-neutral-900",
    },

    status: {
        success: "text-green-400",
        warning: "text-yellow-400",
        error: "text-red-400",
        info: "text-blue-400",
    },

    execution: {
        statusBar: "bg-white/5",
        taskDisplay: "bg-neutral-800/50",
        toolAction: "bg-white/[0.02] border border-white/[0.06]",
        quickAction: cn("bg-white/[0.02] border border-white/[0.06]", "hover:bg-white/[0.04] hover:border-white/10"),
    },
};
