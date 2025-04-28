// Interface with generic type
interface ApiResponse<T> {
    data: T;
    error?: string;
}

// Async/await example
async function fetchData(url: string): Promise<ApiResponse<string>> {
    try {
        const response = await fetch(url);
        return { data: await response.text() };
    } catch (err) {
        return { data: "", error: (err as Error).message };
    }
}

// Tuple type and destructuring
const [name, age]: [string, number] = ["Alice", 30];

// Mapped types
type FeatureFlags = {
    darkMode: boolean;
    newDashboard: boolean;
};
type Options = {
    [Key in keyof FeatureFlags]: string;
};
