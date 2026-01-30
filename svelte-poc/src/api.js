// API service for fetching dashboard data

// In development, API_BASE is empty (Vite proxy handles it)
// In production, set VITE_API_BASE to your Django backend URL
const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function fetchDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/api/dashboard-data/`, {
            credentials: 'include', // Important for Django session auth
        });

        if (!response.ok) {
            if (response.status === 403 || response.status === 401) {
                // Handle unauthorized access if needed, though App.svelte handles this via auth check
                throw new Error('Unauthorized');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await handleResponse(response);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        throw error;
    }
}

export async function fetchInventory() {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/`, {
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await handleResponse(response);
        return data.inventory || [];
    } catch (error) {
        console.error('Error fetching inventory:', error);
        throw error;
    }
}

export async function deleteInventoryItem(id) {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/${id}/delete/`, {
            method: 'DELETE',
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`Delete failed: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error deleting inventory item:', error);
        throw error;
    }
}

export async function createInventoryItem(data) {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`Create failed: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error creating inventory item:', error);
        throw error;
    }
}

export async function updateInventoryItem(id, data) {
    try {
        const response = await fetch(`${API_BASE}/api/inventory/${id}/update/`, {
            method: 'POST', // or PUT if preferred, backend supports both
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error(`Update failed: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error updating inventory item:', error);
        throw error;
    }
}

// Helper to debug response
async function handleResponse(response) {
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        const json = await response.json();
        console.log("DEBUG api.js: Received JSON:", Object.keys(json));
        if (json.raw_data) console.log("DEBUG api.js: raw_data length:", json.raw_data.length);
        return json;
    } else {
        const text = await response.text();
        console.error("Expected JSON params, got:", text.substring(0, 500)); // Log first 500 chars
        if (text.includes("<!DOCTYPE html>")) {
            throw new Error("Received HTML login page instead of JSON. Auth session might be invalid.");
        }
        throw new Error("Invalid API response format (not JSON)");
    }
}

// Fallback sample data (not used when API is connected)
export function getSampleData() {
    return {
        raw_data: [],
        filter_options: null
    };
}
