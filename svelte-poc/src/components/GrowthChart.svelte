<script>
    import { onMount, onDestroy } from "svelte";
    import * as echarts from "echarts";

    export let data = { monthly: [], yearly: [] };
    export let title = "Database Growth (Cumulative)";

    let chartContainer;
    let chart;
    let timeframe = "monthly";

    $: chartData = timeframe === "monthly" ? data.monthly : data.yearly;

    $: if (chart && chartData) {
        updateChart();
    }

    function setTimeframe(tf) {
        timeframe = tf;
    }

    function updateChart() {
        if (!chartData || !chartData.length) {
            chart.clear();
            return;
        }

        chart.setOption({
            backgroundColor: "transparent",
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "cross",
                    label: { backgroundColor: "#2F6F7E" },
                },
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "rgba(47, 111, 126, 0.5)",
                textStyle: { color: "#f8fafc" },
            },
            grid: {
                left: "3%",
                right: "4%",
                top: "10%",
                bottom: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                boundaryGap: false,
                data: chartData.map((d) => d.label),
                axisLine: { lineStyle: { color: "#334155" } },
                axisLabel: { color: "#94a3b8" },
            },
            yAxis: {
                type: "value",
                axisLine: { lineStyle: { color: "#334155" } },
                axisLabel: { color: "#94a3b8" },
                splitLine: {
                    lineStyle: {
                        color: "rgba(51, 65, 85, 0.3)",
                        type: "dashed",
                    },
                },
            },
            series: [
                {
                    name: "Total Databases",
                    type: "line",
                    smooth: true,
                    lineStyle: { width: 3, color: "#22d3ee" },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(34, 211, 238, 0.5)" },
                                {
                                    offset: 1,
                                    color: "rgba(34, 211, 238, 0.05)",
                                },
                            ],
                        },
                    },
                    itemStyle: {
                        color: "#22d3ee",
                        borderWidth: 2,
                        borderColor: "#fff",
                    },
                    data: chartData.map((d) => d.total),
                },
                {
                    name:
                        timeframe === "monthly"
                            ? "New Installations (Monthly)"
                            : "New Installations (Yearly)",
                    type: "bar",
                    barWidth: timeframe === "monthly" ? 10 : 20,
                    itemStyle: {
                        color: "rgba(34, 211, 238, 0.3)",
                        borderRadius: [5, 5, 0, 0],
                    },
                    data: chartData.map((d) => d.added),
                },
            ],
        });
    }

    onMount(() => {
        chart = echarts.init(chartContainer);
        updateChart();

        const resizeHandler = () => chart?.resize();
        window.addEventListener("resize", resizeHandler);
        return () => window.removeEventListener("resize", resizeHandler);
    });

    onDestroy(() => {
        chart?.dispose();
    });
</script>

<div class="chart-card full-width">
    <div class="chart-header">
        <h3>{title}</h3>
        <div class="toggle-group">
            <button
                class:active={timeframe === "monthly"}
                on:click={() => setTimeframe("monthly")}>Monthly</button
            >
            <button
                class:active={timeframe === "yearly"}
                on:click={() => setTimeframe("yearly")}>Yearly</button
            >
        </div>
    </div>
    <div bind:this={chartContainer} class="chart-container"></div>
</div>

<style>
    .chart-card {
        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.8),
            rgba(30, 41, 59, 0.6)
        );
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(47, 111, 126, 0.2);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
    }

    .full-width {
        grid-column: 1 / -1;
    }

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .chart-header h3 {
        color: #f8fafc;
        margin: 0;
        font-size: 16px;
        font-weight: 600;
    }

    .toggle-group {
        background: rgba(15, 23, 42, 0.5);
        padding: 4px;
        border-radius: 6px;
        border: 1px solid #1e293b;
    }

    .toggle-group button {
        background: transparent;
        color: #94a3b8;
        border: none;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .toggle-group button.active {
        background: #0ea5e9;
        color: white;
    }

    .chart-container {
        width: 100%;
        height: 320px;
    }

    @media (max-width: 480px) {
        .chart-card {
            padding: 15px;
            border-radius: 12px;
        }

        .chart-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }

        .chart-header h3 {
            font-size: 14px;
        }

        .toggle-group button {
            padding: 4px 10px;
            font-size: 11px;
        }

        .chart-container {
            height: 220px;
        }
    }
</style>
