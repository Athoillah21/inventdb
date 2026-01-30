<script>
    import { signup } from "../auth.js";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    let username = "";
    let password = "";
    let confirmPassword = "";
    let error = "";
    let loading = false;

    async function handleSubmit() {
        if (!username || !password || !confirmPassword) {
            error = "Please fill in all fields";
            return;
        }

        if (password !== confirmPassword) {
            error = "Passwords do not match";
            return;
        }

        loading = true;
        error = "";

        const result = await signup(username, password);

        loading = false;

        if (result.success) {
            dispatch("signup");
        } else {
            error = result.error;
        }
    }

    function goToLogin() {
        dispatch("switch", { mode: "login" });
    }
</script>

<div class="login-container">
    <div class="login-card">
        <div class="login-header">
            <div class="logo">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="48"
                    height="48"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="8.5" cy="7" r="4"></circle>
                    <line x1="20" y1="8" x2="20" y2="14"></line>
                    <line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
            </div>
            <h1>Create Account</h1>
            <p>Sign up for PostgreSQL Dashboard</p>
        </div>

        <form on:submit|preventDefault={handleSubmit}>
            {#if error}
                <div class="error-message">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    {error}
                </div>
            {/if}

            <div class="form-group">
                <label for="username">Username</label>
                <input
                    type="text"
                    id="username"
                    bind:value={username}
                    placeholder="Choose a username"
                    autocomplete="username"
                    disabled={loading}
                />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    type="password"
                    id="password"
                    bind:value={password}
                    placeholder="Choose a password"
                    autocomplete="new-password"
                    disabled={loading}
                />
            </div>

            <div class="form-group">
                <label for="confirm-password">Confirm Password</label>
                <input
                    type="password"
                    id="confirm-password"
                    bind:value={confirmPassword}
                    placeholder="Confirm your password"
                    autocomplete="new-password"
                    disabled={loading}
                />
            </div>

            <button type="submit" class="login-btn" disabled={loading}>
                {#if loading}
                    <span class="spinner"></span>
                    Creating Account...
                {:else}
                    Sign Up
                {/if}
            </button>
        </form>

        <div class="login-footer">
            <p>
                Already have an account? <a
                    href="#"
                    on:click|preventDefault={goToLogin}>Sign In</a
                >
            </p>
        </div>
    </div>
</div>

<style>
    /* Reuse same styles as Login Page for consistency */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e293b 50%,
            #0f172a 100%
        );
        padding: 20px;
    }

    .login-card {
        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.9),
            rgba(30, 41, 59, 0.8)
        );
        border-radius: 20px;
        padding: 40px;
        width: 100%;
        max-width: 420px;
        border: 1px solid rgba(47, 111, 126, 0.3);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
    }

    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg, #047c94 0%, #2f6f7e 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }

    .login-header h1 {
        font-size: 24px;
        font-weight: 700;
        color: #f8fafc;
        margin: 0 0 8px;
    }

    .login-header p {
        color: #94a3b8;
        font-size: 14px;
        margin: 0;
    }

    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .form-group input {
        width: 100%;
        padding: 14px 16px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(47, 111, 126, 0.4);
        border-radius: 10px;
        color: #f8fafc;
        font-size: 14px;
        outline: none;
        transition: all 0.2s;
        box-sizing: border-box;
    }

    .form-group input:focus {
        border-color: #22d3ee;
        box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1);
    }

    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #f87171;
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 13px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .login-btn {
        width: 100%;
        padding: 14px;
        background: linear-gradient(135deg, #047c94 0%, #22d3ee 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    .login-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(34, 211, 238, 0.3);
    }

    .login-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .spinner {
        width: 18px;
        height: 18px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .login-footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid rgba(47, 111, 126, 0.2);
    }

    .login-footer p {
        color: #64748b;
        font-size: 12px;
        margin: 0;
    }

    .login-footer a {
        color: #22d3ee;
        text-decoration: none;
        font-weight: 500;
    }

    .login-footer a:hover {
        text-decoration: underline;
    }
</style>
