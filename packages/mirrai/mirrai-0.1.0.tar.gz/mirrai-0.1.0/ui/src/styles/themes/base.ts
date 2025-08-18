export const baseStyles = {
    transitions: {
        default: "transition-all duration-150",
        fast: "transition-all duration-75",
        slow: "transition-all duration-300",
    },

    rounded: {
        sm: "rounded",
        md: "rounded-lg",
        lg: "rounded-xl",
        full: "rounded-full",
    },

    spacing: {
        card: "p-6",
        button: {
            sm: "px-3 py-1.5",
            md: "px-4 py-2",
            lg: "px-5 py-2.5",
        },
        input: "px-3 py-2",
        textarea: "px-4 py-3",
    },

    text: {
        xs: "text-xs",
        sm: "text-sm",
        base: "text-base",
        lg: "text-lg",
        xl: "text-xl",
    },

    font: {
        normal: "font-normal",
        medium: "font-medium",
        semibold: "font-semibold",
        bold: "font-bold",
        mono: "font-mono",
    },

    layout: {
        headerHeight: "h-[72px]",
        sidebarWidth: "w-64",
        sidebarCollapsed: "w-20",
    },

    animation: {
        spin: "animate-spin",
        pulse: "animate-pulse",
        pulseSlow: "animate-pulse-slow",
    },

    effects: {
        backdropBlur: "backdrop-blur-lg",
        backdropBlurSm: "backdrop-blur",
        backdropBlurXl: "backdrop-blur-xl",
    },
};
