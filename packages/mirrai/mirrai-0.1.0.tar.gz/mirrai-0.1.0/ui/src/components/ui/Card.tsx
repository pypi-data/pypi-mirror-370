import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { CardVariant } from "@/styles/themes";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: CardVariant;
    noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
    children,
    className,
    variant = "default",
    noPadding = false,
    ...props
}) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.card[variant];

    return (
        <div className={cn(baseClasses, noPadding && "p-0", className)} {...props}>
            {children}
        </div>
    );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => {
    return (
        <div className={cn("flex items-center justify-between mb-4", className)} {...props}>
            {children}
        </div>
    );
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ children, className, ...props }) => {
    const { activeTheme } = useTheme();

    return (
        <h2 className={cn("text-lg font-semibold", activeTheme.text.primary, className)} {...props}>
            {children}
        </h2>
    );
};

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => {
    const { activeTheme } = useTheme();

    return (
        <div className={cn(activeTheme.text.secondary, className)} {...props}>
            {children}
        </div>
    );
};
