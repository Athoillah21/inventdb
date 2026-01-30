<script>
    import { onMount, onDestroy } from 'svelte';
    import * as echarts from 'echarts';
    
    // Props - reactive data from parent
    export let data = [];
    export let title = 'Chart';
    
    // Colors
    const colors = ['#22c55e', '#f59e0b', '#2F6F7E', '#0891b2', '#06b6d4', '#22d3ee'];
    
    let chartContainer;
    let chart;
    
    // Reactive statement - auto-updates when data changes!
    $: if (chart && data) {
        updateChart();
    }
    
    function updateChart() {
        if (!data.length) {
            chart.clear();
            return;
        }
        
        chart.setOption({
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                borderColor: 'rgba(47, 111, 126, 0.5)',
                textStyle: { color: '#f8fafc' }
            },
            legend: { bottom: '5%', textStyle: { color: '#94a3b8' } },
            series: [{
                type: 'pie',
                radius: ['30%', '70%'],
                center: ['50%', '45%'],
                roseType: 'area',
                itemStyle: { borderRadius: 8, borderColor: '#0f172a', borderWidth: 3 },
                label: { color: '#f8fafc', fontSize: 12 },
                emphasis: {
                    scale: true,
                    scaleSize: 15,
                    itemStyle: { shadowBlur: 30, shadowColor: 'rgba(47, 111, 126, 0.6)' }
                },
                data: data.map((d, i) => ({
                    value: d.count,
                    name: d.category_database || 'Unknown',
                    itemStyle: { color: colors[i % colors.length] }
                })),
                animationDuration: 300
            }]
        });
    }
    
    onMount(() => {
        chart = echarts.init(chartContainer);
        updateChart();
        
        // Handle resize
        const resizeHandler = () => chart?.resize();
        window.addEventListener('resize', resizeHandler);
        
        return () => window.removeEventListener('resize', resizeHandler);
    });
    
    onDestroy(() => {
        chart?.dispose();
    });
</script>

<div class="chart-card">
    <h3>{title}</h3>
    <div bind:this={chartContainer} class="chart-container"></div>
</div>

<style>
    .chart-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(47, 111, 126, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .chart-card h3 {
        color: #f8fafc;
        margin: 0 0 15px 0;
        font-size: 16px;
        font-weight: 600;
    }
    
    .chart-container {
        width: 100%;
        height: 320px;
    }
</style>
