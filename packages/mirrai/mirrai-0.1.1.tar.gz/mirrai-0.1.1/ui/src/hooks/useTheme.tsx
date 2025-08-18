import React, { createContext, useContext, useEffect, useState } from "react";
import { Theme, ThemeDefinition, lightTheme, darkTheme, blueTheme } from "@/styles/themes";
import { availableThemes, themeRegistry } from "@/styles/themes/registry";

// Map of theme definitions for easy access
const themeDefinitions: Record<Theme, ThemeDefinition> = {
    light: lightTheme,
    dark: darkTheme,
    blue: blueTheme,
};

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    toggleTheme: () => void;
    availableThemes: Theme[];
    themeInfo: typeof themeRegistry;
    activeTheme: ThemeDefinition;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [theme, setTheme] = useState<Theme>(() => {
        // Check localStorage first
        const stored = localStorage.getItem("theme") as Theme;
        // Validate that stored theme exists in registry
        if (stored && availableThemes.includes(stored)) {
            return stored;
        }
        // Default to first available theme
        return availableThemes[0];
    });

    useEffect(() => {
        // Update localStorage
        localStorage.setItem("theme", theme);

        // Add theme data attribute
        document.documentElement.setAttribute("data-theme", theme);

        // Apply theme-specific body styles
        const themeStyles = {
            light: "bg-neutral-50 text-neutral-900",
            dark: "bg-neutral-950 text-neutral-100",
            blue: "bg-gradient-to-br from-blue-50 via-white to-indigo-50 text-blue-900",
        };

        // Remove all theme classes first
        Object.values(themeStyles).forEach(classes => {
            document.body.className = document.body.className
                .split(" ")
                .filter(c => !classes.split(" ").includes(c))
                .join(" ");
        });

        // Add current theme classes
        const currentStyles = themeStyles[theme as keyof typeof themeStyles];
        if (currentStyles) {
            document.body.className += " " + currentStyles;
        }
    }, [theme]);

    const toggleTheme = () => {
        // Cycle through available themes
        const currentIndex = availableThemes.indexOf(theme);
        const nextIndex = (currentIndex + 1) % availableThemes.length;
        setTheme(availableThemes[nextIndex]);
    };

    return (
        <ThemeContext.Provider
            value={{
                theme,
                setTheme,
                toggleTheme,
                availableThemes,
                themeInfo: themeRegistry,
                activeTheme: themeDefinitions[theme],
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
};
