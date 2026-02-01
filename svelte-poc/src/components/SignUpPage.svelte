<script>
    import { signup } from "../auth.js";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    let username = "";
    let password = "";
    let confirmPassword = "";
    let error = "";
    let successMessage = "";
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
            if (result.pending) {
                successMessage = result.message;
            } else {
                dispatch("signup");
            }
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
        {#if successMessage}
            <div class="success-content">
                <!-- User/Account Icon -->
                <div class="success-icon-bg">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="32"
                        height="32"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"
                        ></path>
                        <circle cx="12" cy="7" r="4"></circle>
                        <line x1="20" y1="8" x2="20" y2="14"></line>
                        <line x1="23" y1="11" x2="17" y2="11"></line>
                    </svg>
                </div>

                <h2 class="success-title">Create Account</h2>
                <p class="success-subtitle">Sign up for PostgreSQL Dashboard</p>

                <!-- Checkmark -->
                <div class="checkmark-circle">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="48"
                        height="48"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="#4ade80"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    >
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                </div>

                <h3 class="approval-title">Approval Pending</h3>
                <p class="approval-text">
                    {successMessage}
                </p>

                <button class="return-btn" on:click={goToLogin}>
                    Return to Login
                </button>
            </div>
        {:else}
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
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"
                        ></path>
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
        {/if}

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
        /* Dynamic Viewport aligned height */
        min-height: 100dvh;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e293b 50%,
            #0f172a 100%
        );
        padding: 20px;
        padding-top: max(20px, env(safe-area-inset-top));
        padding-bottom: max(20px, env(safe-area-inset-bottom));
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
        -webkit-backdrop-filter: blur(10px);
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

    /* Mobile Responsive */
    @media (max-width: 480px) {
        .login-container {
            padding: 15px;
        }

        .login-card {
            padding: 25px 20px;
            border-radius: 16px;
        }

        .logo {
            width: 64px;
            height: 64px;
            border-radius: 14px;
            margin-bottom: 15px;
        }

        .logo svg {
            width: 36px;
            height: 36px;
        }

        .login-header h1 {
            font-size: 20px;
        }

        .login-header p {
            font-size: 13px;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-group input {
            padding: 12px 14px;
            font-size: 14px;
        }

        .login-btn {
            padding: 12px;
            font-size: 14px;
        }

        .login-footer {
            margin-top: 20px;
            padding-top: 15px;
        }
    }
    /* Success Popup Styles */
    .success-content {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px 0;
    }

    .success-icon-bg {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #047c94 0%, #2f6f7e 100%);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(4, 124, 148, 0.2);
    }

    .success-title {
        font-size: 24px;
        font-weight: 700;
        color: #f8fafc;
        margin: 0 0 8px;
    }

    .success-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin: 0 0 30px;
    }

    .checkmark-circle {
        margin-bottom: 15px;
        animation: scaleIn 0.5s ease-out;
    }

    @keyframes scaleIn {
        0% {
            transform: scale(0);
            opacity: 0;
        }
        60% {
            transform: scale(1.2);
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }

    .approval-title {
        font-size: 20px;
        color: #f8fafc;
        margin: 0 0 10px;
        font-weight: 600;
    }

    .approval-text {
        color: #94a3b8;
        margin-bottom: 30px;
        line-height: 1.6;
        font-size: 14px;
        max-width: 300px;
    }

    .return-btn {
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
        box-shadow: 0 4px 12px rgba(34, 211, 238, 0.2);
    }

    .return-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(34, 211, 238, 0.4);
    }
</style>
