# Agent Cost Calculator

Calculate your AI agent infrastructure costs. Compare cloud-only vs hybrid local+cloud inference.

Based on real numbers from a production multi-agent stack running since October 2025.

## Why this exists

Most teams experimenting with AI agents underestimate two things:
- how fast premium-model costs stack up once tasks become multi-turn workflows
- how much margin improves when routine work shifts local while cloud models stay reserved for high-value reasoning

This calculator makes that trade-off visible in a few seconds.

## Quick Start

```bash
python3 cost_calculator.py
```

Or use the interactive mode:

```bash
python3 cost_calculator.py --interactive
```

## What It Calculates

- **Cloud-only cost** — running everything through API providers
- **Hybrid cost** — local models for routine work, cloud for complex tasks
- **Hardware break-even** — how many months until local hardware pays for itself
- **Per-task cost** — average cost per agent task by type

## Proof / example output

- Example JSON output: [`assets/example-output.json`](assets/example-output.json)
- Example comparison graphic: [`assets/cost-comparison.svg`](assets/cost-comparison.svg)

Typical comparison from the bundled defaults:

| Scenario | Monthly Cost | Notes |
|----------|-------------|-------|
| Cloud-only (all Sonnet) | ~$79/month | API only, no local compute |
| Cloud-only (Opus for code) | ~$142/month | Premium model for coding |
| **Hybrid (our setup)** | **~$134/month** | Includes $100/month hardware amortisation |
| Local-heavy | ~$100/month | Hardware amortisation dominates |

The numbers above are what the script currently outputs from the included assumptions. Change workload, routing, and task mix to fit your environment.

## Real Numbers From Production

Our broader operating stack processes 50+ tasks/week across 6 worker types.
The strategic takeaway is not “local is always cheaper.”
It is:
- route routine work to local/cheap models
- reserve premium inference for high-stakes tasks
- measure blended operating cost, not headline token price

## Model Pricing (April 2026)

| Model | Input $/MTok | Output $/MTok | Speed | Where |
|-------|-------------|--------------|-------|-------|
| Qwen 2.5 14B | $0 | $0 | ~100 tok/s | Local (Ollama) |
| Qwen 2.5 7B | $0 | $0 | ~200 tok/s | Local (Ollama) |
| Gemma 4 26B | $0 | $0 | ~85 tok/s | Local (Ollama) |
| Claude Haiku 4.5 | $0.80 | $4.00 | Fast | Anthropic API |
| Claude Sonnet 4.6 | $3.00 | $15.00 | Medium | Anthropic API |
| Claude Opus 4.6 | $15.00 | $75.00 | Slow | Anthropic API |
| GPT-5.4 | $2.50 | $10.00 | Fast | OpenAI API |

## Usage

```bash
# Default calculation (solo consultant, 50 tasks/week)
python3 cost_calculator.py

# Custom workload
python3 cost_calculator.py --tasks-per-week 100 --code-ratio 0.3

# Compare specific scenarios
python3 cost_calculator.py --scenario cloud-only
python3 cost_calculator.py --scenario hybrid
python3 cost_calculator.py --scenario local-heavy

# Export as JSON
python3 cost_calculator.py --format json > costs.json
```

## Requirements

- Python 3.9+
- No dependencies (stdlib only)

## Assumptions and limits

- This is a directional planning tool, not a billing reconciliation engine.
- Token assumptions are based on multi-turn agent workflows, not single prompt/response chats.
- Local-model cost is represented through hardware amortisation, not token accounting.
- You should update pricing if your provider costs or routing rules change.

## License

MIT

---

Built by [Sargentech AI](https://github.com/Sargentech-AI) · [@SargenTech_AI](https://x.com/SargenTech_AI)

For the complete production setup guide: **[guide.sargentech.ai](https://guide.sargentech.ai)**
