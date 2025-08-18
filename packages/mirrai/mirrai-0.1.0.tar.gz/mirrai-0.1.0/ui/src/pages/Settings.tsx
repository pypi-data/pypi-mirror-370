import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { ThemeSelector } from "@/components/ThemeSelector";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

export function Settings() {
    const { activeTheme } = useTheme();

    return (
        <div className="max-w-[800px] mx-auto space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Appearance</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div>
                            <label className={cn("block text-sm font-medium mb-2", activeTheme.text.primary)}>
                                Theme
                            </label>
                            <ThemeSelector showLabel={false} className="w-full max-w-xs" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
