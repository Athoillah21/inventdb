<script>
    import { onMount, onDestroy } from "svelte";
    import * as echarts from "echarts";

    export let data = [];
    export let title = "Master/Slave Distribution";

    const colors = ["#22c55e", "#f59e0b", "#2F6F7E", "#64748b"];

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
                trigger: "item",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "rgba(47, 111, 126, 0.5)",
                textStyle: { color: "#f8fafc" },
            },
            legend: { bottom: "5%", textStyle: { color: "#94a3b8" } },
            series: [
                {
                    type: "pie",
                    radius: ["45%", "70%"],
                    center: ["50%", "45%"],
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: "#0f172a",
                        borderWidth: 3,
                    },
                    label: {
                        show: true,
                        position: "outside",
                        color: "#94a3b8",
                        formatter: "{b}\n{d}%",
                    },
                    labelLine: { lineStyle: { color: "#475569" } },
                    emphasis: {
                        scale: true,
                        scaleSize: 12,
                        label: {
                            show: true,
                            fontSize: 16,
                            fontWeight: "bold",
                            color: "#f8fafc",
                        },
                        itemStyle: {
                            shadowBlur: 25,
                            shadowColor: "rgba(47, 111, 126, 0.5)",
                        },
                    },
                    data: data.map((d, i) => ({
                        value: d.count,
                        name: d.role || "Other",
                        itemStyle: { color: colors[i % colors.length] },
                    })),
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
</style>
