# Svelte Dashboard - PostgreSQL Inventory

A Svelte implementation of the PostgreSQL Database Dashboard, matching all features of the Django version.

## Features

✅ **All 7 Charts:**
- Category Distribution (Rose Pie)
- Master/Slave Distribution (Donut)
- Site Distribution (Pie)
- Business Category (Horizontal Bar)
- PostgreSQL Versions (Bar)
- Database Status Overview (Bar)
- Database Growth (Line + Bar with Monthly/Yearly toggle)

✅ **4 Stat Cards:**
- Total Databases
- Production Count
- Development Count
- Pre-Production Count

✅ **Filter Panel (Slide-out):**
- Hostname (text input with partial match)
- Category (checkboxes)
- Site (checkboxes)
- Business Category (checkboxes)
- Role (checkboxes)

✅ **Reactive Filtering:**
- All charts update instantly when filters change
- Growth chart recalculates from filtered data
- No server calls needed - 100% client-side

## Project Structure

```
svelte-poc/
├── src/
│   ├── main.js              # Entry point
│   ├── App.svelte           # Main dashboard layout
│   ├── stores.js            # Reactive state + derived data
│   ├── api.js               # API service + sample data
│   └── components/
│       ├── CategoryChart.svelte
│       ├── RoleChart.svelte
│       ├── SiteChart.svelte
│       ├── BusinessChart.svelte
│       ├── VersionChart.svelte
│       ├── StatusChart.svelte
│       ├── GrowthChart.svelte
│       ├── FilterPanel.svelte
│       └── StatsCards.svelte
├── index.html
├── vite.config.js
└── package.json
```

## How to Run

```bash
cd svelte-poc
npm install
npm run dev
```

Open http://localhost:5173

## Connecting to Django API

1. Start Django: `python manage.py runserver`
2. The Vite proxy in `vite.config.js` forwards `/api` to Django
3. Update `api.js` to fetch from `/api/dashboard-data/`

## Key Svelte Features Used

- **Stores** (`writable`, `derived`) - Reactive state management
- **Reactive Statements** (`$:`) - Auto-update charts when data changes
- **Component Lifecycle** (`onMount`, `onDestroy`) - ECharts initialization
- **Two-way Binding** (`bind:value`) - Filter inputs
