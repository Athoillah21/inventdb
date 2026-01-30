<script>
    import {
        filters,
        filterOptions,
        activeFilterCount,
        resetFilters,
        toggleFilter,
        setHostnameFilter,
        clearSection,
    } from "../stores.js";

    let isOpen = false;

    function toggle() {
        isOpen = !isOpen;
    }

    function handleReset() {
        resetFilters();
    }

    function handleToggle(type, value) {
        toggleFilter(type, value);
    }

    function handleClearSection(type) {
        clearSection(type);
    }
</script>

<!-- Toggle Button -->
<button class="filter-toggle-btn" on:click={toggle}>
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
    >
        <line x1="4" y1="21" x2="4" y2="14"></line>
        <line x1="4" y1="10" x2="4" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12" y2="3"></line>
        <line x1="20" y1="21" x2="20" y2="16"></line>
        <line x1="20" y1="12" x2="20" y2="3"></line>
        <line x1="1" y1="14" x2="7" y2="14"></line>
        <line x1="9" y1="8" x2="15" y2="8"></line>
        <line x1="17" y1="16" x2="23" y2="16"></line>
    </svg>
    Filters
    {#if $activeFilterCount > 0}
        <span class="badge">{$activeFilterCount}</span>
    {/if}
</button>

<!-- Overlay -->
{#if isOpen}
    <div
        class="overlay"
        on:click={toggle}
        on:keydown={(e) => e.key === "Escape" && toggle()}
        role="button"
        tabindex="0"
    ></div>
{/if}

<!-- Slide-out Panel -->
<div class="filter-panel" class:open={isOpen}>
    <div class="panel-header">
        <h3>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                style="margin-right: 8px; vertical-align: middle;"
            >
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"
                ></polygon>
            </svg>
            Filters
        </h3>
        <button class="close-btn" on:click={toggle}>×</button>
    </div>

    <div class="panel-content">
        {#if $activeFilterCount > 0}
            <div class="active-count">
                ✓ {$activeFilterCount} filter{$activeFilterCount > 1 ? "s" : ""}
                active
            </div>
        {/if}

        <!-- Hostname Filter -->
        <div class="filter-section">
            <div class="section-header">
                <span class="section-title">Hostname</span>
                <button class="clear-btn" on:click={() => setHostnameFilter("")}
                    >Clear</button
                >
            </div>
            <input
                type="text"
                value={$filters.hostname}
                on:input={(e) => setHostnameFilter(e.target.value)}
                placeholder="Type hostname to filter..."
                class="hostname-input"
            />
            <div class="hint">Search by partial hostname match</div>
        </div>

        <!-- Category Filter -->
        <div class="filter-section">
            <div class="section-header">
                <span class="section-title">Category</span>
                <button
                    class="clear-btn"
                    on:click={() => handleClearSection("category")}
                    >Clear</button
                >
            </div>
            {#each $filterOptions.category as option}
                <label
                    class="filter-option"
                    class:active={$filters.category.includes(option)}
                >
                    <input
                        type="checkbox"
                        checked={$filters.category.includes(option)}
                        on:change={() => handleToggle("category", option)}
                    />
                    {option}
                </label>
            {/each}
        </div>

        <!-- Site Filter -->
        <div class="filter-section">
            <div class="section-header">
                <span class="section-title">Site</span>
                <button
                    class="clear-btn"
                    on:click={() => handleClearSection("site")}>Clear</button
                >
            </div>
            {#each $filterOptions.site as option}
                <label
                    class="filter-option"
                    class:active={$filters.site.includes(option)}
                >
                    <input
                        type="checkbox"
                        checked={$filters.site.includes(option)}
                        on:change={() => handleToggle("site", option)}
                    />
                    {option}
                </label>
            {/each}
        </div>

        <!-- Business Filter -->
        <div class="filter-section">
            <div class="section-header">
                <span class="section-title">Business Category</span>
                <button
                    class="clear-btn"
                    on:click={() => handleClearSection("business")}
                    >Clear</button
                >
            </div>
            {#each $filterOptions.business as option}
                <label
                    class="filter-option"
                    class:active={$filters.business.includes(option)}
                >
                    <input
                        type="checkbox"
                        checked={$filters.business.includes(option)}
                        on:change={() => handleToggle("business", option)}
                    />
                    {option}
                </label>
            {/each}
        </div>

        <!-- Role Filter -->
        <div class="filter-section">
            <div class="section-header">
                <span class="section-title">Role</span>
                <button
                    class="clear-btn"
                    on:click={() => handleClearSection("role")}>Clear</button
                >
            </div>
            {#each $filterOptions.role as option}
                <label
                    class="filter-option"
                    class:active={$filters.role.includes(option)}
                >
                    <input
                        type="checkbox"
                        checked={$filters.role.includes(option)}
                        on:change={() => handleToggle("role", option)}
                    />
                    {option}
                </label>
            {/each}
        </div>

        <button class="reset-btn" on:click={handleReset}>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                style="vertical-align: middle; margin-right: 6px;"
            >
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"
                ></path>
                <path d="M3 3v5h5"></path>
            </svg>
            Reset All
        </button>
    </div>
</div>

<style>
    .filter-toggle-btn {
        position: fixed;
        top: 80px;
        left: 16px;
        z-index: 999;
        background: linear-gradient(135deg, #047c94 0%, #2f6f7e 100%);
        border: none;
        border-radius: 10px;
        padding: 10px 16px;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(4, 124, 148, 0.3);
        transition: all 0.2s ease;
    }

    .filter-toggle-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(4, 124, 148, 0.4);
    }

    .badge {
        background: #f87171;
        color: white;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 11px;
    }

    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }

    .filter-panel {
        position: fixed;
        top: 0;
        left: -320px;
        width: 300px;
        height: 100vh;
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(47, 111, 126, 0.3);
        z-index: 1000;
        transition: left 0.3s ease;
        overflow-y: auto;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
    }

    .filter-panel.open {
        left: 0;
    }

    .panel-header {
        padding: 20px;
        border-bottom: 1px solid rgba(47, 111, 126, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        background: #0f172a;
        z-index: 10;
    }

    .panel-header h3 {
        margin: 0;
        color: #f8fafc;
        font-size: 16px;
    }

    .close-btn {
        background: transparent;
        border: none;
        color: #94a3b8;
        font-size: 24px;
        cursor: pointer;
        padding: 4px;
    }

    .panel-content {
        padding: 16px;
    }

    .active-count {
        color: #22d3ee;
        font-size: 12px;
        margin-bottom: 12px;
    }

    .filter-section {
        margin-bottom: 20px;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .section-title {
        color: #94a3b8;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    .clear-btn {
        background: transparent;
        border: none;
        color: #f87171;
        font-size: 11px;
        cursor: pointer;
        padding: 2px 6px;
        border-radius: 4px;
    }

    .clear-btn:hover {
        background: rgba(248, 113, 113, 0.1);
    }

    .hostname-input {
        width: 100%;
        padding: 10px 12px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(47, 111, 126, 0.4);
        border-radius: 8px;
        color: #f8fafc;
        font-size: 13px;
        outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
    }

    .hostname-input:focus {
        border-color: #22d3ee;
    }

    .hint {
        color: #64748b;
        font-size: 11px;
        margin-top: 6px;
    }

    .filter-option {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s ease;
        color: #cbd5e1;
        font-size: 13px;
        border: 1px solid transparent;
    }

    .filter-option:hover {
        background: rgba(47, 111, 126, 0.2);
    }

    .filter-option.active {
        background: rgba(6, 182, 212, 0.2);
        color: #22d3ee;
        border-color: rgba(6, 182, 212, 0.3);
    }

    .filter-option input {
        margin-right: 10px;
        accent-color: #06b6d4;
    }

    .reset-btn {
        width: 100%;
        padding: 10px;
        background: transparent;
        border: 1px solid rgba(248, 113, 113, 0.5);
        border-radius: 8px;
        color: #f87171;
        font-size: 13px;
        cursor: pointer;
        margin-top: 8px;
        transition: all 0.2s ease;
    }

    .reset-btn:hover {
        background: rgba(248, 113, 113, 0.1);
    }
</style>
