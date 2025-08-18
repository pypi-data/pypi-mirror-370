import React from "react";
import { useTheme } from "@/hooks/useTheme";
import { Select } from "@/components/ui/Input";
import { cn } from "@/lib/utils";

interface ThemeSelectorProps {
    className?: string;
    showLabel?: boolean;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({ className, showLabel = true }) => {
    const { theme, setTheme, availableThemes, themeInfo } = useTheme();

    return (
        <div className={cn("flex items-center gap-2", className)}>
            {showLabel && (
                <label htmlFor="theme-select" className="text-sm">
                    Theme:
                </label>
            )}
            <Select
                id="theme-select"
                value={theme}
                onChange={e => setTheme(e.target.value as typeof theme)}
                className="min-w-[120px]"
                title={themeInfo[theme].description}
            >
                {availableThemes.map(themeId => (
                    <option key={themeId} value={themeId}>
                        {themeInfo[themeId].name}
                    </option>
                ))}
            </Select>
        </div>
    );
};
