import React from "react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input: React.FC<InputProps> = ({ className, ...props }) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.input.input;

    return <input className={cn(baseClasses, className)} {...props} />;
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea: React.FC<TextareaProps> = ({ className, ...props }) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.input.textarea;

    return <textarea className={cn(baseClasses, className)} {...props} />;
};

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const Select: React.FC<SelectProps> = ({ className, children, ...props }) => {
    const { activeTheme } = useTheme();
    const baseClasses = activeTheme.input.select;

    return (
        <select className={cn(baseClasses, className)} {...props}>
            {children}
        </select>
    );
};
