import { writable, derived } from 'svelte/store';

// Raw data from API
export const rawData = writable([]);

// Loading state
export const isLoading = writable(true);

// Growth data (original, not filtered by normal filters)
export const growthMonthly = writable([]);
export const growthYearly = writable([]);

// Active filters
export const filters = writable({
    hostname: '',
    category: [],
    site: [],
    business: [],
    role: []
});

// Filter options (unique values for each dimension)
export const filterOptions = writable({
    category: [],
    site: [],
    business: [],
    role: ['Master', 'Slave/Standby', 'Single Instance']
});

// Derived: Filtered data - automatically recalculates
export const filteredData = derived(
    [rawData, filters],
    ([$rawData, $filters]) => {
        return $rawData.filter(item => {
            if ($filters.hostname && !item.hostname.toLowerCase().includes($filters.hostname.toLowerCase())) {
                return false;
            }
            if ($filters.category.length && !$filters.category.includes(item.category)) {
                return false;
            }
            if ($filters.site.length && !$filters.site.includes(item.site)) {
                return false;
            }
            if ($filters.business.length && !$filters.business.includes(item.business)) {
                return false;
            }
            if ($filters.role.length && !$filters.role.includes(item.role)) {
                return false;
            }
            return true;
        });
    }
);

// Helper: Aggregate data by key
function aggregateData(items, key) {
    const counts = {};
    items.forEach(item => {
        const val = item[key];
        if (val) counts[val] = (counts[val] || 0) + 1;
    });
    return Object.entries(counts)
        .map(([k, v]) => ({ key: k, count: v }))
        .sort((a, b) => b.count - a.count);
}

// Derived: Chart data
export const categoryData = derived(filteredData, ($data) =>
    aggregateData($data, 'category').map(d => ({ category_database: d.key, count: d.count }))
);

export const siteData = derived(filteredData, ($data) =>
    aggregateData($data, 'site').map(d => ({ site: d.key, count: d.count }))
);

export const businessData = derived(filteredData, ($data) =>
    aggregateData($data, 'business').slice(0, 8).map(d => ({ business_category: d.key, count: d.count }))
);

export const statusData = derived(filteredData, ($data) =>
    aggregateData($data, 'status').slice(0, 10).map(d => ({ database_status: d.key, count: d.count }))
);

export const versionData = derived(filteredData, ($data) =>
    aggregateData($data, 'version').filter(d => d.key).slice(0, 10).map(d => ({ version: d.key, count: d.count }))
);

export const roleData = derived(filteredData, ($data) => {
    const prodItems = $data.filter(i => i.category === 'Production');
    return aggregateData(prodItems, 'role').filter(d => d.key).map(d => ({ role: d.key, count: d.count }));
});

// Derived: Stats
export const stats = derived(filteredData, ($data) => ({
    total: $data.length,
    production: $data.filter(i => i.category === 'Production').length,
    development: $data.filter(i => i.category === 'Development').length,
    preprod: $data.filter(i => i.category === 'Pre Production').length
}));

// Derived: Active filter count
export const activeFilterCount = derived(filters, ($filters) => {
    let count = 0;
    if ($filters.hostname) count++;
    count += $filters.category.length;
    count += $filters.site.length;
    count += $filters.business.length;
    count += $filters.role.length;
    return count;
});

// Derived: Growth chart data (recalculated from filtered data)
export const filteredGrowthData = derived(filteredData, ($data) => {
    const monthMap = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    };

    const monthlyCounts = {};
    let validDateCount = 0;

    $data.forEach(item => {
        const d = item.installation_date;
        if (!d) return;

        const dStr = String(d).trim().toLowerCase();
        if (!dStr) return;

        let year = null, month = null;

        // Try YYYY-MM-DD or YYYY/MM/DD
        let match = dStr.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
        if (match) {
            year = parseInt(match[1]);
            month = parseInt(match[2]);
        } else {
            // Try DD-MM-YYYY or DD/MM/YYYY
            match = dStr.match(/(\d{1,2})[-/](\d{1,2})[-/](\d{4})/);
            if (match) {
                year = parseInt(match[3]);
                month = parseInt(match[2]);
            } else {
                // Try "Month YYYY"
                match = dStr.match(/([a-z]+)[,\s-]+\d{0,2}[,\s-]*(\d{4})/);
                if (match) {
                    const mStr = match[1];
                    if (monthMap[mStr]) {
                        year = parseInt(match[2]);
                        month = monthMap[mStr];
                    }
                } else {
                    // Just year
                    match = dStr.match(/(\d{4})/);
                    if (match) {
                        year = parseInt(match[1]);
                        month = 1;
                    }
                }
            }
        }

        if (year && month && year >= 1990 && year <= 2030 && month >= 1 && month <= 12) {
            const key = `${year}-${String(month).padStart(2, '0')}`;
            monthlyCounts[key] = (monthlyCounts[key] || 0) + 1;
            validDateCount++;
        }
    });

    const baseline = $data.length - validDateCount;
    const sortedMonths = Object.keys(monthlyCounts).sort();
    const monthNames = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    let cumulative = baseline;
    const monthly = sortedMonths.map(key => {
        const count = monthlyCounts[key];
        cumulative += count;
        const [y, m] = key.split('-');
        return {
            label: `${monthNames[parseInt(m)]} ${y}`,
            added: count,
            total: cumulative
        };
    });

    // Aggregate yearly
    const yearlyCounts = {};
    sortedMonths.forEach(key => {
        const y = key.split('-')[0];
        yearlyCounts[y] = (yearlyCounts[y] || 0) + monthlyCounts[key];
    });

    cumulative = baseline;
    const yearly = Object.keys(yearlyCounts).sort().map(year => {
        const count = yearlyCounts[year];
        cumulative += count;
        return { label: year, added: count, total: cumulative };
    });

    return { monthly, yearly };
});

// Actions
export function resetFilters() {
    filters.set({
        hostname: '',
        category: [],
        site: [],
        business: [],
        role: []
    });
}

export function toggleFilter(type, value) {
    filters.update(f => {
        if (f[type].includes(value)) {
            f[type] = f[type].filter(v => v !== value);
        } else {
            f[type] = [...f[type], value];
        }
        return { ...f };
    });
}

export function setHostnameFilter(value) {
    filters.update(f => ({ ...f, hostname: value }));
}

export function clearSection(type) {
    filters.update(f => ({ ...f, [type]: [] }));
}
