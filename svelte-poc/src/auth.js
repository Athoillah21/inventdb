import { writable } from 'svelte/store';

// Auth state
export const isAuthenticated = writable(false);
export const currentUser = writable(null);
export const authLoading = writable(true);

const API_BASE = import.meta.env.VITE_API_BASE || '';

// Check authentication status
export async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/api/check-auth/`, {
            credentials: 'include',
        });
        const data = await response.json();
        isAuthenticated.set(data.authenticated);
        currentUser.set(data.user || null);
        authLoading.set(false);
        return data.authenticated;
    } catch (error) {
        console.error('Auth check failed:', error);
        isAuthenticated.set(false);
        currentUser.set(null);
        authLoading.set(false);
        return false;
    }
}

// Login
export async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/api/login/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (data.success) {
            isAuthenticated.set(true);
            currentUser.set(data.user);
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Login failed' };
        }
    } catch (error) {
        console.error('Login failed:', error);
        return { success: false, error: 'Network error' };
    }
}

// Signup
export async function signup(username, password) {
    try {
        const response = await fetch(`${API_BASE}/api/signup/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (data.success) {
            isAuthenticated.set(true);
            currentUser.set(data.user);
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Signup failed' };
        }
    } catch (error) {
        console.error('Signup failed:', error);
        return { success: false, error: 'Network error' };
    }
}

// Logout
export async function logout() {
    try {
        await fetch(`${API_BASE}/api/logout/`, {
            credentials: 'include',
        });
        isAuthenticated.set(false);
        currentUser.set(null);
    } catch (error) {
        console.error('Logout failed:', error);
    }
}
