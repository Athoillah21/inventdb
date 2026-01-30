<script>
    import { onMount } from "svelte";
    import { rawData, filterOptions, isLoading } from "./stores.js";
    import { fetchDashboardData } from "./api.js";
    import {
        isAuthenticated,
        authLoading,
        checkAuth,
        login,
        logout,
        currentUser,
    } from "./auth.js";
    import { fade, fly, scale } from "svelte/transition";
    import { quintOut, cubicInOut } from "svelte/easing";

    // Components
    import LoginPage from "./components/LoginPage.svelte";
    import SignUpPage from "./components/SignUpPage.svelte";
    import FilterPanel from "./components/FilterPanel.svelte";
    import StatsCards from "./components/StatsCards.svelte";
    import CategoryChart from "./components/CategoryChart.svelte";
    import SiteChart from "./components/SiteChart.svelte";
    import BusinessChart from "./components/BusinessChart.svelte";
    import RoleChart from "./components/RoleChart.svelte";
    import VersionChart from "./components/VersionChart.svelte";
    import StatusChart from "./components/StatusChart.svelte";
    import GrowthChart from "./components/GrowthChart.svelte";
    import InventoryPage from "./components/InventoryPage.svelte";

    import {
        categoryData,
        siteData,
        businessData,
        roleData,
        versionData,
        statusData,
        filteredGrowthData,
    } from "./stores.js";

    let view = "login";
    let currentPage = "dashboard";

    let dataError = null;
    let loginError = "";
    let isLoggingOut = false;
    let isLoggingIn = false;

    // Boot Sequence State
    let bootStage = 0;
    let loginProgress = 0;

    // Icon Definitions (Lucid Style)
    const icons = {
        auth: `<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><path d="M12 16h.01"/>`,
        network: `<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>`,
        data: `<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>`,
        ui: `<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><path d="M3 9h18"/><path d="M9 21V9"/>`,
    };

    // Computes current state based on stage
    $: currentStage = [
        {
            icon: icons.auth,
            text: "Verifying Identity...",
            header: "Authenticating",
        },
        {
            icon: icons.network,
            text: "Establishing Connection...",
            header: "Connecting",
        },
        {
            icon: icons.data,
            text: "Fetching Inventory...",
            header: "Synchronizing",
        },
        { icon: icons.ui, text: "Building Dashboard...", header: "Finalizing" },
    ][bootStage] || { icon: icons.auth, text: "...", header: "..." };

    onMount(async () => {
        const authed = await checkAuth();
        if (authed) {
            loadData();
        }
    });

    async function loadData() {
        isLoading.set(true);
        dataError = null;
        try {
            const data = await fetchDashboardData();
            rawData.set(data.raw_data || []);
            if (data.filter_options) filterOptions.set(data.filter_options);
            isLoading.set(false);
        } catch (error) {
            console.error("Error loading data:", error);
            dataError = error.message;
            isLoading.set(false);
        }
    }

    async function handleAttemptLogin(event) {
        const { username, password } = event.detail;

        isLoggingIn = true;
        loginError = "";

        // STAGE 0: Auth
        bootStage = 0;
        loginProgress = 5;

        const loginPromise = login(username, password);

        await new Promise((r) => setTimeout(r, 600));
        loginProgress = 25;

        try {
            const result = await loginPromise;

            if (result.success) {
                // STAGE 1: Network
                bootStage = 1;
                loginProgress = 40;
                await new Promise((r) => setTimeout(r, 600));

                // STAGE 2: Data Load
                bootStage = 2;
                loginProgress = 60;

                const dataPromise = loadData();
                await new Promise((r) => setTimeout(r, 600));
                await dataPromise;

                // STAGE 3: UI Prep
                bootStage = 3;
                loginProgress = 100;
                await new Promise((r) => setTimeout(r, 500));

                isLoggingIn = false;
                currentPage = "dashboard";
            } else {
                isLoggingIn = false;
                loginError = result.error;
            }
        } catch (e) {
            isLoggingIn = false;
            loginError = "Network connection failed";
        }
    }

    function handleSignup() {
        isLoggingIn = true;
        setTimeout(async () => {
            await loadData();
            isLoggingIn = false;
        }, 2000);
    }

    function handleSwitch(event) {
        view = event.detail.mode;
        loginError = "";
    }

    async function handleLogout() {
        isLoggingOut = true;
        await new Promise((resolve) => setTimeout(resolve, 1500));
        await logout();
        isLoggingOut = false;
        view = "login";
        rawData.set([]);
        bootStage = 0;
    }
</script>

<!-- Login Boot Transition -->
{#if isLoggingIn}
    <div
        class="transition-screen"
        in:fade={{ duration: 200 }}
        out:fade={{ duration: 500 }}
    >
        <div class="transition-content">
            <div class="icon-stage-container">
                {#key bootStage}
                    <div
                        class="icon-wrapper"
                        in:fly={{ x: -60, duration: 500, opacity: 0 }}
                        out:fly={{ x: 60, duration: 500, opacity: 0 }}
                    >
                        <svg
                            class="minimal-icon"
                            xmlns="http://www.w3.org/2000/svg"
                            width="64"
                            height="64"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            {@html currentStage.icon}
                        </svg>
                    </div>
                {/key}
            </div>

            <h1 in:fade>{currentStage.header}</h1>

            <div class="progress-container">
                <div class="progress-bar" style="width: {loginProgress}%"></div>
            </div>

            <div class="status-container">
                <p class="status-text" in:fade>{currentStage.text}</p>
            </div>
        </div>
    </div>
{:else if isLoggingOut}
    <div
        class="transition-screen"
        in:fade={{ duration: 300 }}
        out:fade={{ duration: 500 }}
    >
        <div
            class="transition-content"
            in:scale={{ start: 0.95, duration: 800, easing: quintOut }}
        >
            <div class="icon-bye">👋</div>
            <h1>See you soon!</h1>
            <p>Signing off...</p>
        </div>
    </div>
{:else if $authLoading}
    <div class="loading-screen" out:fade>
        <div class="spinner"></div>
    </div>
{:else if !$isAuthenticated}
    <div in:fade={{ duration: 600 }}>
        {#if view === "signup"}
            <SignUpPage on:signup={handleSignup} on:switch={handleSwitch} />
        {:else}
            <LoginPage
                on:attemptLogin={handleAttemptLogin}
                on:switch={handleSwitch}
                error={loginError}
            />
        {/if}
    </div>
{:else}
    <!-- Main App Layout -->
    <main in:fade={{ duration: 800 }}>
        {#if currentPage === "dashboard"}
            <FilterPanel />
        {/if}

        <header in:fly={{ y: -50, duration: 800, easing: quintOut }}>
            <div class="header-content">
                <div>
                    {#if currentPage === "dashboard"}
                        <h1>Database Analytics Dashboard</h1>
                        <p>Overview of PostgreSQL database infrastructure</p>
                    {:else}
                        <h1>Database Inventory</h1>
                        <p>Manage your PostgreSQL database Infrastructure</p>
                    {/if}
                </div>
                <div class="user-controls">
                    <span class="username">👤 {$currentUser}</span>

                    <button
                        class:active={currentPage === "dashboard"}
                        class="nav-btn"
                        on:click={() => {
                            currentPage = "dashboard";
                            loadData(); // Refresh data on switch
                        }}
                    >
                        Dashboard
                    </button>
                    <button
                        class:active={currentPage === "inventory"}
                        class="nav-btn"
                        on:click={() => (currentPage = "inventory")}
                    >
                        Inventory
                    </button>

                    <button class="logout-btn" on:click={handleLogout}
                        >Logout</button
                    >
                </div>
            </div>
            <!-- Removed Badge from Header -->
        </header>

        <div class="content-body">
            {#if currentPage === "dashboard"}
                {#if $isLoading}
                    <div class="loading" in:fade>
                        <div class="spinner"></div>
                        <p>Loading dashboard data...</p>
                    </div>
                {:else if dataError}
                    <div class="error-container" in:fly={{ y: 20 }}>
                        <div class="error-icon">⚠️</div>
                        <h3>Failed to load data</h3>
                        <p>{dataError}</p>
                        <button on:click={loadData} class="retry-btn"
                            >Retry</button
                        >
                    </div>
                {:else}
                    <StatsCards />

                    <div
                        class="charts-grid two-columns"
                        in:fly={{
                            y: 50,
                            duration: 1000,
                            delay: 600,
                            easing: quintOut,
                        }}
                    >
                        <CategoryChart
                            data={$categoryData}
                            title="Category Distribution"
                        />
                        <RoleChart
                            data={$roleData}
                            title="Master/Slave Distribution"
                        />
                        <SiteChart data={$siteData} title="Site Distribution" />
                        <BusinessChart
                            data={$businessData}
                            title="Business Category"
                        />
                        <VersionChart
                            data={$versionData}
                            title="PostgreSQL Versions"
                        />
                        <StatusChart
                            data={$statusData}
                            title="Database Status Overview"
                        />
                    </div>

                    <div
                        class="charts-grid one-column"
                        in:fly={{
                            y: 50,
                            duration: 1000,
                            delay: 800,
                            easing: quintOut,
                        }}
                    >
                        <GrowthChart
                            data={$filteredGrowthData}
                            title="Database Growth (Cumulative)"
                        />
                    </div>
                {/if}
            {:else if currentPage === "inventory"}
                <div in:fade={{ duration: 300 }}>
                    <InventoryPage hideHeader={true} />
                </div>
            {/if}
        </div>

        <footer class="app-footer">
            <span class="svelte-badge-footer">⚡ Powered by Svelte</span>
        </footer>
    </main>
{/if}

<style>
    :global(*) {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    :global(body) {
        font-family:
            "Inter",
            -apple-system,
            BlinkMacSystemFont,
            sans-serif;
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #0c4a6e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
        color: #f8fafc;
        overflow-x: hidden;
    }

    /* Loading Screen & Transition Styles */
    .loading-screen,
    .transition-screen {
        height: 100vh;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 2000;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(20px);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .transition-content {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 300px;
        position: relative;
    }

    .icon-stage-container {
        height: 80px;
        width: 100%;
        display: grid;
        place-items: center;
        margin-bottom: 20px;
    }

    .icon-wrapper {
        grid-area: 1 / 1;
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .icon-bye {
        font-size: 64px;
        margin-bottom: 20px;
        animation: wave 2s infinite;
    }

    @keyframes wave {
        0% {
            transform: rotate(0deg);
        }
        25% {
            transform: rotate(20deg);
        }
        75% {
            transform: rotate(-20deg);
        }
        100% {
            transform: rotate(0deg);
        }
    }

    .minimal-icon {
        color: #22d3ee;
        filter: drop-shadow(0 0 15px rgba(34, 211, 238, 0.4));
    }

    .transition-content h1 {
        font-size: 24px;
        font-weight: 600;
        color: #f8fafc;
        margin: 10px 0;
        letter-spacing: -0.5px;
        height: 30px;
    }

    .progress-container {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        overflow: hidden;
        margin-top: 10px;
    }

    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #22d3ee, #06b6d4);
        border-radius: 2px;
        transition: width 0.4s ease-out;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
    }

    .status-container {
        height: 20px;
        margin-top: 8px;
    }

    .status-text {
        color: #94a3b8;
        font-size: 13px;
        font-family: monospace;
        margin: 0;
    }

    /* Main Layout */
    main {
        max-width: 1400px;
        margin: 0 auto;
        padding: 30px;
        padding-left: 80px;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    header {
        margin-bottom: 30px;
        position: relative;
    }

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    .user-controls {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }

    .username {
        font-size: 14px;
        color: #cbd5e1;
    }

    /* Buttons */
    .logout-btn,
    .nav-btn {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.5);
        color: #f87171;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s;
        text-decoration: none;
    }

    .logout-btn:hover {
        background: rgba(239, 68, 68, 0.2);
    }

    .nav-btn {
        background: rgba(14, 165, 233, 0.1);
        border: 1px solid rgba(14, 165, 233, 0.5);
        color: #38bdf8;
    }

    .nav-btn:hover {
        background: rgba(14, 165, 233, 0.2);
    }

    .nav-btn.active {
        background: #0ea5e9;
        color: white;
    }

    h1 {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }

    header p {
        color: #94a3b8;
        font-size: 14px;
    }

    /* Footer */
    .app-footer {
        margin-top: auto; /* Push to bottom */
        padding-top: 40px;
        padding-bottom: 10px;
        text-align: center;
        width: 100%;
    }

    .svelte-badge-footer {
        display: inline-block;
        background: linear-gradient(135deg, #ff3e00 0%, #ff6d00 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        opacity: 0.8;
        box-shadow: 0 4px 10px rgba(255, 62, 0, 0.2);
        transition: transform 0.2s;
    }

    .svelte-badge-footer:hover {
        transform: translateY(-2px);
        opacity: 1;
    }

    .charts-grid {
        display: grid;
        gap: 20px;
        margin-bottom: 20px;
    }

    .charts-grid.two-columns {
        grid-template-columns: repeat(2, 1fr);
    }

    .charts-grid.one-column {
        grid-template-columns: 1fr;
    }

    @media (max-width: 1024px) {
        .charts-grid.two-columns {
            grid-template-columns: 1fr;
        }
    }

    /* Tablet Responsive */
    @media (max-width: 768px) {
        main {
            padding: 20px;
            padding-left: 20px;
        }

        .header-content {
            flex-direction: column;
            align-items: flex-start;
            gap: 15px;
        }

        .user-controls {
            width: 100%;
            flex-wrap: wrap;
            gap: 10px;
        }

        h1 {
            font-size: 22px;
        }

        header p {
            font-size: 13px;
        }

        .nav-btn,
        .logout-btn {
            padding: 8px 12px;
            font-size: 12px;
        }
    }

    /* Mobile Responsive */
    @media (max-width: 480px) {
        main {
            padding: 15px;
            padding-top: 70px; /* Space for fixed filter button */
        }

        header {
            margin-bottom: 20px;
        }

        .header-content {
            flex-direction: column;
            gap: 15px;
        }

        .header-content > div:first-child {
            width: 100%;
        }

        .user-controls {
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
        }

        .username {
            grid-column: 1 / -1;
            font-size: 12px;
            text-align: center;
            padding: 8px 0;
            border-top: 1px solid rgba(148, 163, 184, 0.2);
            margin-top: 4px;
            order: 4;
        }

        h1 {
            font-size: 20px;
            line-height: 1.2;
        }

        header p {
            font-size: 12px;
        }

        .nav-btn,
        .logout-btn {
            width: 100%;
            text-align: center;
            padding: 10px 6px;
            font-size: 11px;
        }

        .svelte-badge-footer {
            font-size: 10px;
            padding: 3px 10px;
        }

        .charts-grid {
            gap: 15px;
        }
    }

    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        color: #94a3b8;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(47, 111, 126, 0.3);
        border-top-color: #22d3ee;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .error-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        margin: 20px 0;
    }

    .error-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }

    .error-container h3 {
        color: #f87171;
        margin-bottom: 8px;
    }

    .error-container p {
        color: #fca5a5;
        margin-bottom: 20px;
    }

    .retry-btn {
        background: #f87171;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.2s;
    }

    .retry-btn:hover {
        background: #ef4444;
    }
</style>
