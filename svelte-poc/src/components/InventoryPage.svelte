<script>
    import { onMount, createEventDispatcher } from "svelte";
    import {
        fetchInventory,
        deleteInventoryItem,
        createInventoryItem,
        updateInventoryItem,
    } from "../api.js";
    import { fade, fly, scale } from "svelte/transition";
    import { quintOut } from "svelte/easing";

    const dispatch = createEventDispatcher();

    let inventory = [];
    let isLoading = true;
    let error = null;

    // Filters
    let filters = {
        hostname: "",
        db_name: "",
        category: "",
        site: "",
        role: "",
        status: "",
    };

    // Filter Options
    let categories = [];
    let sites = [];
    let roles = ["Master", "Slave/Standby", "Single Instance"];

    // Pagination
    let currentPage = 1;
    let itemsPerPage = 20;

    onMount(async () => {
        await loadInventory();
    });

    async function loadInventory() {
        isLoading = true;
        try {
            inventory = await fetchInventory();
            extractFilterOptions(inventory);
            isLoading = false;
        } catch (e) {
            error = e.message;
            isLoading = false;
        }
    }

    function extractFilterOptions(data) {
        categories = [
            ...new Set(data.map((i) => i.category).filter(Boolean)),
        ].sort();
        sites = [...new Set(data.map((i) => i.site).filter(Boolean))].sort();
    }

    // Reactive Filtering
    $: filteredInventory = inventory.filter((item) => {
        const matchHostname = item.hostname
            .toLowerCase()
            .includes(filters.hostname.toLowerCase());
        const matchDb = item.db_name
            .toLowerCase()
            .includes(filters.db_name.toLowerCase());
        const matchStatus = item.status
            .toLowerCase()
            .includes(filters.status.toLowerCase());
        const matchCategory =
            !filters.category || item.category === filters.category;
        const matchSite = !filters.site || item.site === filters.site;
        const matchRole = !filters.role || item.role === filters.role;

        return (
            matchHostname &&
            matchDb &&
            matchStatus &&
            matchCategory &&
            matchSite &&
            matchRole
        );
    });

    // Pagination Logic
    $: totalPages = Math.ceil(filteredInventory.length / itemsPerPage);
    $: paginatedItems = filteredInventory.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage,
    );

    let oldLength = 0;
    $: if (filteredInventory.length !== oldLength) {
        currentPage = 1;
        oldLength = filteredInventory.length;
    }

    function resetFilters() {
        filters = {
            hostname: "",
            db_name: "",
            category: "",
            site: "",
            role: "",
            status: "",
        };
        currentPage = 1;
    }

    function nextPage() {
        if (currentPage < totalPages) currentPage++;
    }

    function prevPage() {
        if (currentPage > 1) currentPage--;
    }

    // Toast Notifications
    let toast = { show: false, message: "", type: "info" };

    function showToast(message, type = "info") {
        toast = { show: true, message, type };
        setTimeout(() => {
            toast.show = false;
        }, 3000);
    }

    // Confirmation Dialog
    let confirmDialog = { show: false, message: "", onConfirm: null };

    function confirmAction(message, action) {
        confirmDialog = { show: true, message, onConfirm: action };
    }

    function closeConfirm() {
        confirmDialog = { show: false, message: "", onConfirm: null };
    }

    async function executeConfirm() {
        if (confirmDialog.onConfirm) {
            await confirmDialog.onConfirm();
        }
        closeConfirm();
    }

    async function handleDelete(id) {
        confirmAction(
            "Are you sure you want to delete this database?",
            async () => {
                try {
                    await deleteInventoryItem(id);
                    // Remove from local state
                    inventory = inventory.filter((item) => item.id !== id);
                    showToast("Database deleted successfully", "success");
                } catch (e) {
                    showToast("Failed to delete: " + e.message, "error");
                }
            },
        );
    }

    function downloadCSV() {
        const headers = [
            "ID",
            "Hostname",
            "Database",
            "Status",
            "Category",
            "Site",
            "Role",
            "Version",
            "Port",
        ];
        const rows = filteredInventory.map((i) => [
            i.id,
            i.hostname,
            i.db_name,
            i.status,
            i.category,
            i.site,
            i.role,
            i.version,
            i.port,
        ]);

        let csvContent =
            "data:text/csv;charset=utf-8," +
            headers.join(",") +
            "\n" +
            rows.map((e) => e.join(",")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "inventory_export.csv");
        document.body.appendChild(link);
        link.click();
    }

    // Modal & Form Logic
    let isModalOpen = false;
    let isEditing = false;
    let isSaving = false;
    let currentItem = {
        id: null,
        hostname: "",
        db_name: "",
        category: "Development",
        site: "BSD",
        role: "Single Instance",
        status: "Open",
        version: "",
        port: "5432",
        business: "Business Support",
        is_dismantled: false,
    };

    function openCreateModal() {
        isEditing = false;
        currentItem = {
            id: null,
            hostname: "",
            db_name: "",
            category: "Development",
            site: "BSD",
            role: "Single Instance",
            status: "Open",
            version: "",
            port: "5432",
            business: "Business Support",
            is_dismantled: false,
        };
        isModalOpen = true;
    }

    function openEditModal(item) {
        isEditing = true;
        currentItem = { ...item };
        // Map role back if needed, assuming role is correct in item
        if (!currentItem.port) currentItem.port = "5432";
        if (currentItem.is_dismantled === undefined)
            currentItem.is_dismantled = false;
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
    }

    async function handleSave() {
        if (!currentItem.hostname || !currentItem.db_name) {
            showToast("Hostname and Database Name are required.", "warning");
            return;
        }

        isSaving = true;
        try {
            if (isEditing) {
                await updateInventoryItem(currentItem.id, currentItem);
                showToast("Database updated successfully!", "success");
            } else {
                await createInventoryItem(currentItem);
                showToast("Database created successfully!", "success");
            }
            isModalOpen = false;
            await loadInventory(); // Reload list
        } catch (e) {
            showToast("Failed to save: " + e.message, "error");
        } finally {
            isSaving = false;
        }
    }
</script>

<div class="inventory-page" in:fade={{ duration: 300 }}>
    <div class="table-card">
        <div class="card-header">
            <div class="header-title">
                <span class="icon">🗄️</span>
                <h2>All Databases ({filteredInventory.length} records)</h2>
            </div>
            <button class="btn-primary" on:click={openCreateModal}>
                + Add New Database
            </button>
        </div>

        <div class="filter-bar">
            <div class="filter-group">
                <label>Hostname</label>
                <input
                    type="text"
                    placeholder="Search hostname..."
                    bind:value={filters.hostname}
                />
            </div>
            <div class="filter-group">
                <label>Database</label>
                <input
                    type="text"
                    placeholder="Search database..."
                    bind:value={filters.db_name}
                />
            </div>
            <div class="filter-group">
                <label>Category</label>
                <select bind:value={filters.category}>
                    <option value="">All Categories</option>
                    {#each categories as cat}
                        <option value={cat}>{cat}</option>
                    {/each}
                </select>
            </div>
            <div class="filter-group">
                <label>Site</label>
                <select bind:value={filters.site}>
                    <option value="">All Sites</option>
                    {#each sites as site}
                        <option value={site}>{site}</option>
                    {/each}
                </select>
            </div>
            <div class="filter-group">
                <label>Role</label>
                <select bind:value={filters.role}>
                    <option value="">All Roles</option>
                    {#each roles as role}
                        <option value={role}>{role}</option>
                    {/each}
                </select>
            </div>
            <div class="filter-group">
                <label>Status</label>
                <input
                    type="text"
                    placeholder="Search status..."
                    bind:value={filters.status}
                />
            </div>

            <div class="filter-actions">
                <button class="btn-secondary" on:click={resetFilters}
                    >Reset</button
                >
                <button class="btn-outline" on:click={downloadCSV}
                    >Download</button
                >
            </div>
        </div>

        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th width="40">No</th>
                        <th>Hostname</th>
                        <th>DB</th>
                        <th>Status</th>
                        <th>Category</th>
                        <th>Site</th>
                        <th>Role</th>
                        <!-- Added Column -->
                        <th>Version</th>
                        <th>Port</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {#if isLoading}
                        <tr>
                            <td colspan="10" class="loading-cell"
                                >Loading inventory data...</td
                            >
                        </tr>
                    {:else if filteredInventory.length === 0}
                        <tr>
                            <td colspan="10" class="empty-cell"
                                >No records found matching your filters.</td
                            >
                        </tr>
                    {:else}
                        {#each paginatedItems as item, i (item.id)}
                            <tr
                                in:fly={{ y: 20, duration: 300, delay: i * 20 }}
                                class:dismantled={item.is_dismantled}
                            >
                                <td class="index-cell"
                                    >{(currentPage - 1) * itemsPerPage +
                                        i +
                                        1}</td
                                >
                                <td class="font-bold">
                                    {item.hostname}
                                    {#if item.is_dismantled}
                                        <span class="dismantled-badge"
                                            >DISMANTLED</span
                                        >
                                    {/if}
                                </td>
                                <td>{item.db_name}</td>
                                <td>
                                    <span
                                        class="status-badge"
                                        class:error={item.status !== "Open"}
                                    >
                                        {item.status}
                                    </span>
                                </td>
                                <td>
                                    <span
                                        class="category-tag"
                                        data-cat={item.category}
                                    >
                                        {item.category}
                                    </span>
                                </td>
                                <td
                                    ><span class="site-tag">{item.site}</span
                                    ></td
                                >
                                <td
                                    ><!-- Role Badge -->
                                    <span
                                        class="role-badge"
                                        data-role={item.role}
                                    >
                                        {item.role || "-"}
                                    </span>
                                </td>
                                <td class="mono">{item.version}</td>
                                <td class="mono">{item.port}</td>
                                <td>
                                    <div class="actions">
                                        <button
                                            class="btn-icon"
                                            title="Edit"
                                            on:click={() => openEditModal(item)}
                                            >✏️</button
                                        >
                                        <button
                                            class="btn-icon delete"
                                            title="Delete"
                                            on:click={() =>
                                                handleDelete(item.id)}
                                            >🗑️</button
                                        >
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>

        {#if !isLoading && filteredInventory.length > 0}
            <div class="pagination-footer">
                <div class="page-info">
                    Showing <span class="highlight"
                        >{(currentPage - 1) * itemsPerPage + 1}</span
                    >
                    to
                    <span class="highlight"
                        >{Math.min(
                            currentPage * itemsPerPage,
                            filteredInventory.length,
                        )}</span
                    >
                    of <span class="highlight">{filteredInventory.length}</span>
                    entries
                </div>
                <div class="pagination-btns">
                    <button
                        class="page-btn"
                        disabled={currentPage === 1}
                        on:click={prevPage}>Previous</button
                    >
                    <div class="page-indicator">
                        Page {currentPage} of {Math.max(1, totalPages)}
                    </div>
                    <button
                        class="page-btn"
                        disabled={currentPage === totalPages ||
                            totalPages === 0}
                        on:click={nextPage}>Next</button
                    >
                </div>
            </div>
        {/if}
    </div>

    {#if isModalOpen}
        <div
            class="modal-overlay"
            on:click|self={closeModal}
            transition:fade={{ duration: 200 }}
        >
            <div class="modal-content" in:fly={{ y: -20, duration: 300 }}>
                <div class="modal-header">
                    <h3>{isEditing ? "Edit Database" : "Add New Database"}</h3>
                    <button class="close-btn" on:click={closeModal}>×</button>
                </div>
                <div class="modal-body">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Hostname *</label>
                            <input
                                type="text"
                                bind:value={currentItem.hostname}
                                placeholder="e.g. pg-prod-01"
                            />
                        </div>
                        <div class="form-group">
                            <label>Database Name *</label>
                            <input
                                type="text"
                                bind:value={currentItem.db_name}
                                placeholder="e.g. core_db"
                            />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Category</label>
                            <select bind:value={currentItem.category}>
                                {#each categories as cat}
                                    <option value={cat}>{cat}</option>
                                {/each}
                                <option value="Production">Production</option>
                                <option value="Development">Development</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Site</label>
                            <select bind:value={currentItem.site}>
                                {#each sites as site}
                                    <option value={site}>{site}</option>
                                {/each}
                                <option value="BSD">BSD</option>
                                <option value="TBS">TBS</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Role</label>
                            <select bind:value={currentItem.role}>
                                {#each roles as role}
                                    <option value={role}>{role}</option>
                                {/each}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <input
                                type="text"
                                bind:value={currentItem.status}
                                placeholder="e.g. Open"
                            />
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Version</label>
                            <input
                                type="text"
                                bind:value={currentItem.version}
                                placeholder="e.g. PostgreSQL 13.4"
                            />
                        </div>
                        <div class="form-group">
                            <label>Port</label>
                            <input
                                type="text"
                                bind:value={currentItem.port}
                                placeholder="5432"
                            />
                        </div>
                    </div>
                    {#if isEditing}
                        <div class="form-row dismantle-row">
                            <label class="toggle-label">
                                <input
                                    type="checkbox"
                                    bind:checked={currentItem.is_dismantled}
                                />
                                <span class="toggle-text"
                                    >Mark as Dismantled</span
                                >
                                <span class="toggle-hint"
                                    >(Excludes from dashboard count)</span
                                >
                            </label>
                        </div>
                    {/if}
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" on:click={closeModal}
                        >Cancel</button
                    >
                    <button
                        class="btn-primary"
                        on:click={handleSave}
                        disabled={isSaving}
                    >
                        {isSaving
                            ? "Saving..."
                            : isEditing
                              ? "Save Changes"
                              : "Create Database"}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Toast Notification -->
    {#if toast.show}
        <div
            class="toast"
            class:success={toast.type === "success"}
            class:error={toast.type === "error"}
            class:warning={toast.type === "warning"}
            transition:fly={{ y: 50, duration: 300 }}
        >
            <span class="toast-icon">
                {#if toast.type === "success"}✅{/if}
                {#if toast.type === "error"}❌{/if}
                {#if toast.type === "warning"}⚠️{/if}
                {#if toast.type === "info"}ℹ️{/if}
            </span>
            <span class="toast-message">{toast.message}</span>
        </div>
    {/if}

    <!-- Confirmation Modal -->
    {#if confirmDialog.show}
        <div class="modal-overlay" transition:fade={{ duration: 200 }}>
            <div
                class="modal-content confirm-box"
                in:scale={{ start: 0.9, duration: 200 }}
            >
                <div class="confirm-body">
                    <span class="confirm-icon">❓</span>
                    <h3>Confirm Action</h3>
                    <p>{confirmDialog.message}</p>
                </div>
                <div class="confirm-actions">
                    <button class="btn-secondary" on:click={closeConfirm}
                        >Cancel</button
                    >
                    <button class="btn-danger" on:click={executeConfirm}
                        >Confirm</button
                    >
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    .inventory-page {
        padding-bottom: 20px;
    }

    .table-card {
        background: linear-gradient(
            135deg,
            rgba(30, 41, 59, 0.4) 0%,
            rgba(15, 23, 42, 0.6) 100%
        );
        border: 1px solid rgba(47, 111, 126, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        overflow: hidden;
    }

    .card-header {
        padding: 20px;
        background: rgba(15, 23, 42, 0.5);
        border-bottom: 1px solid rgba(47, 111, 126, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .header-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .header-title h2 {
        font-size: 18px;
        font-weight: 600;
        color: #e2e8f0;
        margin: 0;
    }

    .btn-primary {
        background: #0ea5e9;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-primary:hover {
        background: #0284c7;
    }
    .btn-primary:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .btn-danger {
        background: #ef4444;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-danger:hover {
        background: #dc2626;
    }

    .btn-secondary {
        background: #334155;
        color: #e2e8f0;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-secondary:hover {
        background: #475569;
    }

    .btn-outline {
        background: transparent;
        border: 1px solid #475569;
        color: #94a3b8;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-outline:hover {
        border-color: #94a3b8;
        color: #f8fafc;
    }

    .filter-bar {
        padding: 20px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        border-bottom: 1px solid rgba(47, 111, 126, 0.1);
        align-items: end;
    }

    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .filter-group label {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    input,
    select {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        color: #f8fafc;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
        width: 100%;
    }
    input:focus,
    select:focus {
        border-color: #0ea5e9;
        outline: none;
    }

    .filter-actions {
        display: flex;
        gap: 8px;
    }

    .table-responsive {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    th {
        text-align: left;
        padding: 16px 20px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 11px;
        border-bottom: 1px solid rgba(47, 111, 126, 0.1);
    }

    td {
        padding: 12px 20px;
        border-bottom: 1px solid rgba(47, 111, 126, 0.1);
        color: #cbd5e1;
        vertical-align: middle;
    }

    tr:hover td {
        background: rgba(30, 41, 59, 0.3);
    }

    .font-bold {
        font-weight: 600;
        color: #f8fafc;
    }
    .mono {
        font-family: monospace;
        color: #94a3b8;
    }
    .index-cell {
        color: #64748b;
    }

    .category-tag {
        background: rgba(14, 165, 233, 0.1);
        color: #38bdf8;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
    }
    .category-tag[data-cat="Production"] {
        background: rgba(34, 197, 94, 0.1);
        color: #4ade80;
    }
    .category-tag[data-cat="Development"] {
        background: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
    }
    .category-tag[data-cat="Pre Production"] {
        background: rgba(168, 85, 247, 0.1);
        color: #c084fc;
    }

    .site-tag {
        background: rgba(71, 85, 105, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
    }

    /* New Role Badge Styles */
    .role-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }

    .role-badge[data-role="Master"] {
        background: rgba(34, 211, 238, 0.1);
        color: #22d3ee;
        border-color: rgba(34, 211, 238, 0.3);
    }

    .role-badge[data-role="Slave/Standby"] {
        background: rgba(244, 63, 94, 0.1);
        color: #f43f5e;
        border-color: rgba(244, 63, 94, 0.3);
    }

    .status-badge {
        opacity: 0.8;
    }
    .status-badge.error {
        color: #f87171;
    }

    .actions {
        display: flex;
        gap: 8px;
    }

    .btn-icon {
        background: transparent;
        border: none;
        cursor: pointer;
        opacity: 0.6;
        transition: opacity 0.2s;
    }
    .btn-icon:hover {
        opacity: 1;
    }
    .btn-icon.delete:hover {
        transform: scale(1.1);
    }

    .loading-cell,
    .empty-cell {
        text-align: center;
        padding: 40px;
        color: #94a3b8;
        font-style: italic;
    }

    .pagination-footer {
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.3);
        border-top: 1px solid rgba(47, 111, 126, 0.1);
    }

    .page-info {
        font-size: 13px;
        color: #94a3b8;
    }
    .highlight {
        color: #cbd5e1;
        font-weight: 600;
    }

    .pagination-btns {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .page-btn {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(71, 85, 105, 0.5);
        color: #cbd5e1;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .page-btn:hover:not(:disabled) {
        background: rgba(56, 189, 248, 0.1);
        border-color: #38bdf8;
        color: #38bdf8;
    }
    .page-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .page-indicator {
        font-size: 13px;
        color: #cbd5e1;
        min-width: 80px;
        text-align: center;
    }

    /* Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background: #1e293b;
        border: 1px solid rgba(47, 111, 126, 0.5);
        border-radius: 12px;
        width: 100%;
        max-width: 600px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    .modal-header {
        padding: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-header h3 {
        margin: 0;
        color: #f8fafc;
        font-size: 18px;
    }

    .close-btn {
        background: transparent;
        border: none;
        color: #94a3b8;
        font-size: 24px;
        cursor: pointer;
    }
    .close-btn:hover {
        color: #fff;
    }

    .modal-body {
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .form-group label {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 600;
    }

    .modal-footer {
        padding: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        background: rgba(15, 23, 42, 0.3);
    }

    /* Toast Styles */
    .toast {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #1e293b;
        color: #f8fafc;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 2000;
        border-left: 4px solid #3b82f6; /* info default */
    }
    .toast.success {
        border-left-color: #22c55e;
    }
    .toast.error {
        border-left-color: #ef4444;
    }
    .toast.warning {
        border-left-color: #f59e0b;
    }
    .toast-message {
        font-size: 14px;
        font-weight: 500;
    }

    /* Confirmation Modal Specifics */
    .confirm-box {
        max-width: 400px;
        text-align: center;
        overflow: hidden;
    }
    .confirm-body {
        padding: 30px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
    .confirm-icon {
        font-size: 40px;
        margin-bottom: 8px;
    }
    .confirm-body h3 {
        color: #f8fafc;
        margin: 0;
        font-size: 18px;
    }
    .confirm-body p {
        color: #94a3b8;
        margin: 0;
        font-size: 14px;
    }
    .confirm-actions {
        padding: 16px;
        background: rgba(15, 23, 42, 0.3);
        display: flex;
        justify-content: center;
        gap: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Dismantled Styles */
    tr.dismantled td {
        opacity: 0.5;
        text-decoration: line-through;
    }
    tr.dismantled td:last-child {
        text-decoration: none;
        opacity: 1;
    }
    .dismantled-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        font-size: 9px;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
        text-decoration: none;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* Toggle in Modal */
    .dismantle-row {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    .toggle-label {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        color: #f87171;
        font-size: 14px;
    }
    .toggle-label input[type="checkbox"] {
        width: 18px;
        height: 18px;
        accent-color: #ef4444;
    }
    .toggle-text {
        font-weight: 600;
    }
    .toggle-hint {
        color: #64748b;
        font-size: 12px;
    }
</style>
