---
name: dsh-openbb
description: OpenBB financial-data bridge for DeepSeek Harness — curated command catalog, deterministic execution, provider/timestamp provenance on every payload, LLM plans and interprets but never invents numbers.
---

Use this skill when a task needs market data beyond the family's Tencent ladder
(quotes/options-vol/SEC/economy/news across providers). The bridge is deterministic —
you orchestrate, OpenBB provides.

## Run

```bash
KIT=<this-directory>
python3 $KIT/scripts/obb.py --list                       # catalog
python3 $KIT/scripts/obb_research.py --save --question "<question>" --symbols <SYM>
```

Requires `pip install openbb openbb-equity openbb-news openbb-economy openbb-yfinance openbb-sec`.

## Discipline

- Findings must cite fields ([F#] → cmd.provider.field); model never produces numbers.
- Failures are reported as failures — "data missing, no speculation" is a valid output.
- Every payload carries provider + fetched_at; cite them in the answer.
