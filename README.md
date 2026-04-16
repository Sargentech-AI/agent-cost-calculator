# Agent Cost Calculator

Calculate your AI agent infrastructure costs. Compare cloud-only vs hybrid local+cloud inference.

Based on real numbers from a production multi-agent stack running since October 2025.

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

## Real Numbers From Production

Our stack processes 50+ tasks/week across 6 worker types:

| Scenario | Monthly Cost | Notes |
|----------|-------------|-------|
| Cloud-only (all Sonnet) | ~$1,200/month | Every task hits the API |
| Cloud-only (Opus for code) | ~$1,800/month | Premium model for coding |
| **Hybrid (our setup)** | **~$400/month** | 80% local, 20% cloud |
| Hardware amortized | +$100/month | Mac Studio over 36 months |

**Break-even on hardware: 4-5 months.**

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

## License

MIT

---

Built by [Sargentech AI](https://github.com/Sargentech-AI) · [@SargenTech_AI](https://x.com/SargenTech_AI)

For the complete production setup guide: **[guide.sargentech.ai](https://guide.sargentech.ai)**
