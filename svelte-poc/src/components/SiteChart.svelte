<script>
    import { onMount, onDestroy } from "svelte";
    import * as echarts from "echarts";

    export let data = [];
    export let title = "Site Distribution";

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
                trigger: "item",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "rgba(47, 111, 126, 0.5)",
                textStyle: { color: "#f8fafc" },
                formatter: "{b}: {c} ({d}%)",
            },
            legend: { bottom: "5%", textStyle: { color: "#94a3b8" } },
            series: [
                {
                    type: "pie",
                    radius: "65%",
                    center: ["50%", "45%"],
                    label: {
                        color: "#f8fafc",
                        fontSize: 13,
                        formatter: "{b}\n{c}",
                    },
                    labelLine: {
                        length: 15,
                        length2: 10,
                        lineStyle: { color: "#475569" },
                    },
                    itemStyle: {
                        borderRadius: 6,
                        borderColor: "#0f172a",
                        borderWidth: 2,
                    },
                    emphasis: {
                        scale: true,
                        scaleSize: 10,
                        itemStyle: {
                            shadowBlur: 40,
                            shadowColor: "rgba(47, 111, 126, 0.8)",
                        },
                    },
                    data: data.map((d, i) => ({
                        value: d.count,
                        name: d.site || "Unknown",
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
