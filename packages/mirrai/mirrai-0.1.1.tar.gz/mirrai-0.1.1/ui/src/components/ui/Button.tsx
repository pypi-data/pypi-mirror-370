import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";
import { ButtonVariant } from "@/styles/themes";
import { baseStyles } from "@/styles/themes/base";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
    children,
    className,
    variant = "primary",
    size = "md",
    disabled,
    ...props
}) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.button[variant];
    const sizeClasses =
        variant !== "icon"
            ? baseStyles.spacing.button[size] + " " + baseStyles.text[size === "lg" ? "base" : "sm"]
            : "";

    return (
        <button className={cn(baseClasses, sizeClasses, className)} disabled={disabled} {...props}>
            {children}
        </button>
    );
};
