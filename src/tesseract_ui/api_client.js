const API_BASE_URL = 'http://localhost:5000';

export async function getLogs() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        // The data is already clean thanks to your Pandas backend
        return result.data; 
    } catch (error) {
        console.error("Failed to fetch logs:", error);
        return []; // Return empty array on error
    }
}

export async function executeCommand(command) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/execute_command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to execute command "${command}":`, error);
        return { status: 'error', message: error.message };
    }
}