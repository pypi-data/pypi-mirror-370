import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { BadgeVariant } from "@/styles/themes";

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: BadgeVariant;
}

export const Badge: React.FC<BadgeProps> = ({ children, className, variant = "default", ...props }) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.badge[variant];

    return (
        <div className={cn(baseClasses, className)} {...props}>
            {children}
        </div>
    );
};
