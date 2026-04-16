#!/usr/bin/env python3
"""
Agent Cost Calculator — Compare cloud-only vs hybrid local+cloud inference costs.

Based on real production numbers from a multi-agent stack (6 worker types, 50+ tasks/week).

Usage:
    python3 cost_calculator.py
    python3 cost_calculator.py --interactive
    python3 cost_calculator.py --tasks-per-week 100 --code-ratio 0.3
    python3 cost_calculator.py --format json
"""

import argparse
import json
import sys

# Model pricing (April 2026, per million tokens)
MODELS = {
    # Local models (Ollama) — $0 cost, hardware amortized separately
    "qwen2.5:14b": {"input": 0, "output": 0, "speed_tps": 100, "location": "local", "label": "Qwen 2.5 14B"},
    "qwen2.5:7b": {"input": 0, "output": 0, "speed_tps": 200, "location": "local", "label": "Qwen 2.5 7B"},
    "gemma4:26b": {"input": 0, "output": 0, "speed_tps": 85, "location": "local", "label": "Gemma 4 26B"},

    # Cloud models — API pricing
    "claude-haiku-4.5": {"input": 0.80, "output": 4.00, "speed_tps": 300, "location": "cloud", "label": "Claude Haiku 4.5"},
    "claude-sonnet-4.6": {"input": 3.00, "output": 15.00, "speed_tps": 150, "location": "cloud", "label": "Claude Sonnet 4.6"},
    "claude-opus-4.6": {"input": 15.00, "output": 75.00, "speed_tps": 50, "location": "cloud", "label": "Claude Opus 4.6"},
    "gpt-5.4": {"input": 2.50, "output": 10.00, "speed_tps": 200, "location": "cloud", "label": "GPT-5.4"},
}

# Task types and their typical token usage (cumulative across multi-turn sessions)
# These reflect real production numbers — agent sessions are multi-turn with tool use
TASK_TYPES = {
    "research": {"input_tokens": 80000, "output_tokens": 15000, "label": "Research/Analysis"},
    "writing": {"input_tokens": 50000, "output_tokens": 20000, "label": "Content Writing"},
    "code": {"input_tokens": 150000, "output_tokens": 30000, "label": "Coding/Review"},
    "qa": {"input_tokens": 40000, "output_tokens": 5000, "label": "Quality Assurance"},
    "triage": {"input_tokens": 15000, "output_tokens": 2000, "label": "Triage/Routing"},
    "monitoring": {"input_tokens": 10000, "output_tokens": 1000, "label": "Health Monitoring"},
}

# Scenario definitions — which model handles which task type
SCENARIOS = {
    "cloud-only-sonnet": {
        "label": "Cloud Only (Sonnet for everything)",
        "routing": {t: "claude-sonnet-4.6" for t in TASK_TYPES},
    },
    "cloud-only-premium": {
        "label": "Cloud Only (Opus for code, Sonnet for rest)",
        "routing": {
            **{t: "claude-sonnet-4.6" for t in TASK_TYPES},
            "code": "claude-opus-4.6",
        },
    },
    "hybrid": {
        "label": "Hybrid (80% local, cloud for complex work)",
        "routing": {
            "research": "qwen2.5:14b",
            "writing": "qwen2.5:14b",
            "code": "claude-opus-4.6",
            "qa": "qwen2.5:14b",
            "triage": "qwen2.5:14b",
            "monitoring": "qwen2.5:7b",
        },
    },
    "hybrid-balanced": {
        "label": "Hybrid Balanced (local + Sonnet for research/writing)",
        "routing": {
            "research": "claude-sonnet-4.6",
            "writing": "claude-sonnet-4.6",
            "code": "claude-opus-4.6",
            "qa": "qwen2.5:14b",
            "triage": "qwen2.5:14b",
            "monitoring": "qwen2.5:7b",
        },
    },
    "local-heavy": {
        "label": "Local Heavy (everything local, cloud fallback only)",
        "routing": {t: "qwen2.5:14b" for t in TASK_TYPES},
    },
}

# Default workload distribution (percentage of tasks per type)
DEFAULT_WORKLOAD = {
    "research": 0.20,
    "writing": 0.20,
    "code": 0.15,
    "qa": 0.15,
    "triage": 0.15,
    "monitoring": 0.15,
}


def calculate_cost(scenario_name, tasks_per_week, workload=None, hardware_cost_monthly=100):
    """Calculate monthly cost for a given scenario."""
    workload = workload or DEFAULT_WORKLOAD
    scenario = SCENARIOS[scenario_name]
    tasks_per_month = tasks_per_week * 4.33  # avg weeks per month

    total_cost = 0
    breakdown = {}

    for task_type, ratio in workload.items():
        task_count = tasks_per_month * ratio
        model_name = scenario["routing"][task_type]
        model = MODELS[model_name]
        task = TASK_TYPES[task_type]

        input_cost = (task["input_tokens"] / 1_000_000) * model["input"] * task_count
        output_cost = (task["output_tokens"] / 1_000_000) * model["output"] * task_count
        task_total = input_cost + output_cost

        breakdown[task_type] = {
            "model": model["label"],
            "location": model["location"],
            "tasks_per_month": round(task_count, 1),
            "cost": round(task_total, 2),
            "per_task": round(task_total / max(task_count, 1), 4),
        }
        total_cost += task_total

    local_tasks = sum(1 for t in scenario["routing"].values() if MODELS[t]["location"] == "local")
    cloud_tasks = len(scenario["routing"]) - local_tasks
    local_ratio = local_tasks / len(scenario["routing"])

    return {
        "scenario": scenario["label"],
        "tasks_per_week": tasks_per_week,
        "tasks_per_month": round(tasks_per_month, 0),
        "api_cost_monthly": round(total_cost, 2),
        "hardware_amortized": hardware_cost_monthly if local_ratio > 0 else 0,
        "total_monthly": round(total_cost + (hardware_cost_monthly if local_ratio > 0 else 0), 2),
        "local_ratio": f"{local_ratio:.0%}",
        "breakdown": breakdown,
    }


def print_comparison(tasks_per_week, workload=None, format_type="text"):
    """Print cost comparison across all scenarios."""
    results = {}
    for name in SCENARIOS:
        results[name] = calculate_cost(name, tasks_per_week, workload)

    if format_type == "json":
        print(json.dumps(results, indent=2))
        return

    print(f"\n{'=' * 70}")
    print(f"  AGENT COST CALCULATOR — {tasks_per_week} tasks/week")
    print(f"{'=' * 70}\n")

    for name, r in results.items():
        marker = " ★" if name == "hybrid" else ""
        print(f"  {r['scenario']}{marker}")
        print(f"  {'─' * 50}")
        print(f"  API cost:      ${r['api_cost_monthly']:>8.2f}/month")
        if r["hardware_amortized"] > 0:
            print(f"  Hardware:      ${r['hardware_amortized']:>8.2f}/month (amortized)")
        print(f"  Total:         ${r['total_monthly']:>8.2f}/month")
        print(f"  Local ratio:   {r['local_ratio']}")
        print()

        for task_type, b in r["breakdown"].items():
            if b["cost"] > 0:
                print(f"    {TASK_TYPES[task_type]['label']:20s} → {b['model']:20s} ${b['cost']:>7.2f} (${b['per_task']:.4f}/task)")
        print()

    # Break-even calculation
    cloud_only = results["cloud-only-sonnet"]["api_cost_monthly"]
    hybrid = results["hybrid"]["total_monthly"]
    savings = cloud_only - hybrid
    hardware_investment = 3600  # Mac Studio M4 base

    if savings > 0:
        breakeven_months = hardware_investment / savings
        print(f"  {'─' * 50}")
        print(f"  💰 Hybrid saves ${savings:.0f}/month vs cloud-only Sonnet")
        print(f"  🖥️  Hardware break-even: {breakeven_months:.1f} months")
        print(f"     (assuming ${hardware_investment:,} Mac Studio)")
    print()


def interactive_mode():
    """Interactive Q&A to build a custom estimate."""
    print("\n  Agent Cost Calculator — Interactive Mode\n")

    try:
        tasks = int(input("  Tasks per week [50]: ") or 50)
    except ValueError:
        tasks = 50

    print("\n  Task mix (enter percentages, must sum to 100):")
    workload = {}
    remaining = 100
    for task_type, info in TASK_TYPES.items():
        default = int(DEFAULT_WORKLOAD[task_type] * 100)
        try:
            pct = int(input(f"    {info['label']} [{default}%]: ") or default)
        except ValueError:
            pct = default
        workload[task_type] = pct / 100
        remaining -= pct

    if abs(sum(workload.values()) - 1.0) > 0.05:
        print("\n  ⚠️ Percentages don't sum to 100, normalizing...")
        total = sum(workload.values())
        workload = {k: v / total for k, v in workload.items()}

    print_comparison(tasks, workload)


def main():
    parser = argparse.ArgumentParser(description="Agent Cost Calculator")
    parser.add_argument("--tasks-per-week", type=int, default=50, help="Tasks per week (default: 50)")
    parser.add_argument("--code-ratio", type=float, help="Override coding task ratio (0-1)")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()), help="Show only one scenario")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list-models", action="store_true", help="List available models and pricing")

    args = parser.parse_args()

    if args.list_models:
        print(f"\n  {'Model':<25s} {'Input $/MTok':>12s} {'Output $/MTok':>13s} {'Speed':>10s} {'Location':>8s}")
        print(f"  {'─' * 70}")
        for name, m in MODELS.items():
            print(f"  {m['label']:<25s} ${m['input']:>10.2f} ${m['output']:>11.2f} {m['speed_tps']:>7d} t/s {m['location']:>8s}")
        print()
        return

    if args.interactive:
        interactive_mode()
        return

    workload = None
    if args.code_ratio:
        workload = dict(DEFAULT_WORKLOAD)
        old_code = workload["code"]
        workload["code"] = args.code_ratio
        # redistribute the difference
        diff = args.code_ratio - old_code
        for k in workload:
            if k != "code":
                workload[k] -= diff / (len(workload) - 1)

    print_comparison(args.tasks_per_week, workload, args.format)


if __name__ == "__main__":
    main()
