export type Theme = "light" | "dark" | "blue";

export type ComponentVariant = "default" | "hover" | "active" | "disabled";
export type ButtonVariant = "primary" | "ghost" | "icon";
export type BadgeVariant = "default" | "success" | "warning" | "error" | "tool";
export type CardVariant = "default" | "hover" | "transparent";
export type InputType = "input" | "textarea" | "select";

export interface ThemeDefinition {
    card: Record<CardVariant, string>;
    button: Record<ButtonVariant, string>;
    badge: Record<BadgeVariant, string>;
    input: Record<InputType, string>;
    sidebar: {
        base: string;
        navItem: string;
        navItemActive: string;
        text: {
            primary: string;
            secondary: string;
            muted: string;
        };
    };
    layout: {
        background: string;
        header: string;
        gridPattern: string;
        progressBar: string;
    };
    text: {
        primary: string;
        secondary: string;
        muted: string;
        inverse: string;
    };
    status: {
        success: string;
        warning: string;
        error: string;
        info: string;
    };
    execution: {
        statusBar: string;
        taskDisplay: string;
        toolAction: string;
        quickAction: string;
    };
}

export { lightTheme } from "./light";
export { darkTheme } from "./dark";
export { blueTheme } from "./blue";
