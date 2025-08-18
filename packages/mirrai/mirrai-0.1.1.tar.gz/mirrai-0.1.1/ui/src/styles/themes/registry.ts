import { Theme, ThemeDefinition } from "./index";
import { lightTheme } from "./light";
import { darkTheme } from "./dark";
import { blueTheme } from "./blue";

export interface ThemeInfo {
    id: Theme;
    name: string;
    description?: string;
    definition: ThemeDefinition;
}

// Central registry of all available themes
export const themeRegistry: Record<Theme, ThemeInfo> = {
    light: {
        id: "light",
        name: "Light",
        description: "Clean and bright theme",
        definition: lightTheme,
    },
    dark: {
        id: "dark",
        name: "Dark",
        description: "Easy on the eyes in low light",
        definition: darkTheme,
    },
    blue: {
        id: "blue",
        name: "Ocean Blue",
        description: "Calming blue gradients",
        definition: blueTheme,
    },
};

// Get list of available theme IDs
export const availableThemes = Object.keys(themeRegistry) as Theme[];

// Get theme definition by ID
export const getTheme = (themeId: Theme): ThemeDefinition => {
    return themeRegistry[themeId].definition;
};

// Get theme info by ID
export const getThemeInfo = (themeId: Theme): ThemeInfo => {
    return themeRegistry[themeId];
};
