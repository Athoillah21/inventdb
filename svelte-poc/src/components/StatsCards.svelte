<script>
    import { stats } from "../stores.js";
    import { fly } from "svelte/transition";
    import { quintOut, cubicOut } from "svelte/easing";
    import { tweened } from "svelte/motion";

    // Tweened stores for smooth number transitions
    const total = tweened(0, { duration: 600, easing: cubicOut });
    const production = tweened(0, { duration: 600, easing: cubicOut });
    const development = tweened(0, { duration: 600, easing: cubicOut });
    const preprod = tweened(0, { duration: 600, easing: cubicOut });

    // Reactively update tweens when stats change
    $: total.set($stats.total);
    $: production.set($stats.production);
    $: development.set($stats.development);
    $: preprod.set($stats.preprod);
</script>

<div class="stats-grid">
    <div
        class="stat-card"
        in:fly={{ y: 50, duration: 1000, delay: 0, easing: quintOut }}
    >
        <div class="icon primary">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
        </div>
        <div class="value">{Math.round($total)}</div>
        <div class="label">Total Databases</div>
    </div>

    <div
        class="stat-card"
        in:fly={{ y: 50, duration: 1000, delay: 150, easing: quintOut }}
    >
        <div class="icon success">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22,4 12,14.01 9,11.01"></polyline>
            </svg>
        </div>
        <div class="value">{Math.round($production)}</div>
        <div class="label">Production</div>
    </div>

    <div
        class="stat-card"
        in:fly={{ y: 50, duration: 1000, delay: 300, easing: quintOut }}
    >
        <div class="icon warning">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <path
                    d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
                ></path>
            </svg>
        </div>
        <div class="value">{Math.round($development)}</div>
        <div class="label">Development</div>
    </div>

    <div
        class="stat-card"
        in:fly={{ y: 50, duration: 1000, delay: 450, easing: quintOut }}
    >
        <div class="icon info">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            >
                <path
                    d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"
                ></path>
                <path d="M8.5 2h7"></path>
                <path d="M7 16h10"></path>
            </svg>
        </div>
        <div class="value">{Math.round($preprod)}</div>
        <div class="label">Pre-Production</div>
    </div>
</div>

<style>
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .stat-card {
        background: linear-gradient(
            135deg,
            rgba(15, 23, 42, 0.8) 0%,
            rgba(30, 41, 59, 0.6) 100%
        );
        border-radius: 16px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        border: 1px solid rgba(47, 111, 126, 0.2);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        transition:
            transform 0.3s ease,
            box-shadow 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
    }

    .icon.primary {
        background: linear-gradient(
            135deg,
            rgba(0, 37, 97, 0.3) 0%,
            rgba(4, 124, 148, 0.3) 100%
        );
        color: #06b6d4;
    }

    .icon.success {
        background: linear-gradient(
            135deg,
            rgba(34, 197, 94, 0.2) 0%,
            rgba(34, 197, 94, 0.1) 100%
        );
        color: #22c55e;
    }

    .icon.warning {
        background: linear-gradient(
            135deg,
            rgba(245, 158, 11, 0.2) 0%,
            rgba(245, 158, 11, 0.1) 100%
        );
        color: #f59e0b;
    }

    .icon.info {
        background: linear-gradient(
            135deg,
            rgba(6, 182, 212, 0.2) 0%,
            rgba(6, 182, 212, 0.1) 100%
        );
        color: #06b6d4;
    }

    .value {
        font-size: 32px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .label {
        font-size: 14px;
        color: #94a3b8;
    }

    /* Tablet Responsive */
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        .stat-card {
            padding: 18px;
        }

        .value {
            font-size: 26px;
        }

        .label {
            font-size: 13px;
        }
    }

    /* Mobile Responsive */
    @media (max-width: 480px) {
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 10px;
            margin-bottom: 15px;
        }

        .stat-card {
            padding: 12px 10px;
            border-radius: 10px;
        }

        .stat-card:hover {
            transform: none;
            box-shadow: none;
        }

        .icon {
            width: 36px;
            height: 36px;
            margin-bottom: 8px;
            border-radius: 8px;
        }

        .icon svg {
            width: 18px;
            height: 18px;
        }

        .value {
            font-size: 20px;
            margin-bottom: 2px;
        }

        .label {
            font-size: 10px;
        }
    }
</style>
