---
title: "Data Preparation Guide"
layout: single
permalink: /guides/data-preparation/
sidebar:
  nav: "docs"
toc: true
toc_label: "Data Preparation"
toc_icon: "database"
---

This optional pack lets you scrape web pages straight from the **Insight Ingenious** CLI.

---

## Installation (extras)

```bash
uv add ingenious[dataprep]  # Add dataprep capabilities to your project
# OR for development from source:
uv pip install -e ".[dataprep]"  # Install with dataprep extra
```

Requires a Scrapfly key (`SCRAPFLY_API_KEY`). Add it to your environment or a `.env` file.

---

## 3. Quick‑Start (CLI)

### 3.1. Single URL

```bash
# Pretty‑print a JSON envelope to stdout
SCRAPFLY_API_KEY=sk_live_… \
ingen dataprep crawl https://example.com
```

### 3.2. Batch Mode

```bash
# Scrape three URLs, write newline‑delimited JSON to a file
ingen dataprep batch \
  https://a.com https://b.com https://c.com \
  --out pages.ndjson --raw
```

### 3.3. Flag Reference

| Flag                   | Forwarded kwarg                | Description                                          |
| ---------------------- | ------------------------------ | ---------------------------------------------------- |
| `--api-key`            | `api_key`                      | Scrapfly key for *this* run (else env var)           |
| `--max-attempts`       | `max_attempts`                 | Total tries per URL (default **5**)                  |
| `--retry-code`         | `retry_on_status_code`         | Repeatable – add HTTP codes to retry list            |
| `--delay`              | `delay`                        | Initial back‑off in **seconds** (doubles each retry) |
| `--js / --no-js`       | `extra_scrapfly_cfg.render_js` | Toggle headless browser rendering                    |
| `--extra-scrapfly-cfg` | `extra_scrapfly_cfg`           | Raw JSON merged over default SDK config              |

Run `ingen dataprep crawl --help` to see the full Typer‑generated help screen.

### 3.4. Fresh‑Clone Walkthrough

> *Goal:* go from a **fresh clone** to running **unit tests, e2e tests, and the new CLI** in one continuous shell session.
>
> *Prerequisites:* [uv](https://github.com/astral-sh/uv) is installed • You are in the repo root (`ingenious/`).

```bash
# 1️⃣  Build an isolated virtual‑env and install extras
uv venv                # creates .venv/ and writes .python-version
source .venv/bin/activate
uv pip install --python .venv/bin/python -e ".[dataprep]"

# 2️⃣  Supply your Scrapfly key (required for live tests / CLI)
export SCRAPFLY_API_KEY="sk_live_your_real_key_here"
#   – or – add the same line to a .env at repo root

# 3️⃣  Run all tests for data prep
uv run pytest ingenious/dataprep/tests

# 4️⃣  Smoke‑test the new CLI commands

## 4.a  Single‑page scrape (pretty JSON)
ingen dataprep crawl \
  "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary"

## 4.c  Batch scrape two URLs (NDJSON → file)
ingen dataprep batch \
  "https://www.volparahealth.com/news/how-breast-density-impacts-lifetime-cancer-risk" \
  "https://www.medicalnewstoday.com/articles/tyrer-cuzick-score#summary" \
  --out pages.ndjson
```

These commands exercise **all public surfaces** added by the Dataprep pack: environment creation, tests, and both CLI commands.

---

**Need details?** See the flag reference above or call `ingen dataprep crawl --help`. Happy scraping!
