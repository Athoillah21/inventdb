<script>
    import { onMount, onDestroy } from "svelte";
    import * as echarts from "echarts";

    export let data = [];
    export let title = "Database Status Overview";

    const colors = [
        "#002561",
        "#2F6F7E",
        "#047C94",
        "#0891b2",
        "#06b6d4",
        "#22d3ee",
    ];

    let chartContainer;
    let chart;

    $: if (chart && data) {
        updateChart();
    }

    function updateChart() {
        if (!data.length) {
            chart.clear();
            return;
        }

        chart.setOption({
            backgroundColor: "transparent",
            tooltip: {
                trigger: "axis",
                axisPointer: { type: "shadow" },
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "rgba(47, 111, 126, 0.5)",
                textStyle: { color: "#f8fafc" },
            },
            grid: {
                left: "3%",
                right: "4%",
                top: "12%",
                bottom: "20%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: data.map((d) => d.database_status || "Unknown"),
                axisLine: { lineStyle: { color: "#334155" } },
                axisLabel: {
                    color: "#94a3b8",
                    fontSize: 10,
                    rotate: 25,
                    interval: 0,
                },
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
                    type: "bar",
                    data: data.map((d, i) => ({
                        value: d.count,
                        itemStyle: {
                            color: colors[i % colors.length],
                            borderRadius: [6, 6, 0, 0],
                            shadowBlur: 10,
                            shadowColor: "rgba(6, 182, 212, 0.3)",
                        },
                    })),
                    barWidth: "45%",
                    showBackground: true,
                    backgroundStyle: {
                        color: "rgba(47, 111, 126, 0.06)",
                        borderRadius: [6, 6, 0, 0],
                    },
                    label: {
                        show: true,
                        position: "top",
                        color: "#f8fafc",
                        fontSize: 11,
                        fontWeight: "bold",
                    },
                    animationDuration: 300,
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

<div class="chart-card">
    <h3>{title}</h3>
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

    @media (max-width: 480px) {
        .chart-card {
            padding: 15px;
            border-radius: 12px;
        }

        .chart-card h3 {
            font-size: 14px;
            margin-bottom: 10px;
        }

        .chart-container {
            height: 250px;
        }
    }
</style>
