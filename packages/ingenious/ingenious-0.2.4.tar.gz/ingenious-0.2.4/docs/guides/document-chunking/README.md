# 🧠 Insight Ingenious – Document Chunking

A robust, extensible service **and** CLI for splitting documents into precise, context‑aware chunks—perfect for Retrieval‑Augmented Generation (RAG) pipelines.

---

## Overview

The **`chunk`** module provides the core text‑splitting capabilities within the Insight Ingenious framework. It transforms large source documents (Text, Markdown, JSON, JSONL) into smaller segments that balance semantic coherence with Large Language Model token limits.

**Ideal for:**

* Preparing data for vector databases and embedding models.
* Consistent, token‑aware splitting across mixed document types.
* Bidirectional context overlap between chunks to boost retrieval quality.

---

## Features

* ✨ **Multiple Strategies** – recursive, markdown, token, and semantic splitting.
* 📏 **Precise Budgeting** – configure `chunk_size` & `chunk_overlap` in tokens (via *tiktoken*) **or** characters.
* 🔗 **Bidirectional Overlap** – overlap before *and* after each chunk for maximum context preservation.
* 🌍 **Unicode Safe** – token strategy respects grapheme boundaries, protecting complex characters & emojis.
* 🧠 **Semantic Splitting** – OpenAI / Azure OpenAI embeddings find natural semantic breaks.
* ⚡ **Efficient Loading** – streams large JSON via *ijson* to minimise memory.
* 🆔 **Stable IDs** – deterministic, globally‑unique chunk IDs with configurable path encoding.

---

## Installation

The chunking capabilities are an **optional extra**.

```bash
# Install the core Ingenious package with the chunking extra—assuming you’ve already run pip install uv, created your environment with uv venv, and activated it.
uv pip install -e ".[chunk]"
```

> **Note**  Semantic splitting requires access to OpenAI or Azure OpenAI embeddings.

---

## Quick Start (CLI)

The primary entry‑point is `ingen chunk run`.

### Basic Recursive Splitting

Split a text file into 100‑token chunks with a 10‑token overlap:

```bash
ingen chunk run test_files/git_repo_docs.txt --strategy token --overlap-unit tokens --chunk-size 100 --chunk-overlap 10 --encoding-name cl100k_base --output test_integration_chunking_folder_2/git_repo_docs-token-tokens.jsonl
```

### Processing JSONL Input

Chunk each record from a JSON Lines file (e.g. output from *ingen document‑processing*):

```bash
ingen chunk run test_files/pages_pdfminer_local_patientbrochure.jsonl --strategy token --overlap-unit tokens --chunk-size 100 --chunk-overlap 10 --encoding-name cl100k_base --output test_integration_chunking_folder_2/pages_pdfminer_local_patientbrochure-token-tokens.jsonl
```

### Semantic Splitting the Azure variables below or, alternatively, *(requires `OPENAI_API_KEY`)*

#### Azure OpenAI Service

```bash
export AZURE_OPENAI_API_KEY="ae7a5e4566yheayse5y754223ryaergarg"
export AZURE_OPENAI_ENDPOINT="https://testsemanticchunking.openai.azure.com/"
export AZURE_EMBEDDING_DEPLOYMENT="text-embedding-3-small"
```

#### Standard OpenAI Key (alternative)

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Example command:

```bash
ingen chunk run test_files/git_repo_docs.txt \
  --strategy semantic \
  --overlap-unit tokens \
  --chunk-size 100 \
  --chunk-overlap 10 \
  --encoding-name cl100k_base \
  --output test_integration_chunking_folder_2/git_repo_docs-semantic-tokens.jsonl
```
---

## Python API

```python
from ingenious.chunk import ChunkConfig, build_splitter

# 1 · Define configuration
config = ChunkConfig(
    strategy="token",
    chunk_size=256,
    chunk_overlap=32,
    overlap_unit="tokens"
)

# 2 · Build the splitter instance
splitter = build_splitter(config)

# 3 · Split text
text = "Your long document content goes here..."
chunks = splitter.split_text(text)

print(f"Generated {len(chunks)} chunks.")
# print(chunks[0])
```

---

## Configuration & Strategies

Behaviour is controlled via CLI flags that map 1‑to‑1 with the `ChunkConfig` model.

### Available Strategies

| Strategy    | Description                                                        | Key Configuration                                                        |
| ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `recursive` | Hierarchical splits (paragraph→sentence→word). Fast and versatile. | `--chunk-size`, `--chunk-overlap`, `--separators`                        |
| `markdown`  | Aware of Markdown structure (headers, lists).                      | `--chunk-size`, `--chunk-overlap`                                        |
| `token`     | Splits on token boundaries, Unicode‑safe.                          | `--chunk-size`, `--chunk-overlap`, `--encoding-name`                     |
| `semantic`  | Uses embeddings to split at semantic breaks.                       | `--embed-model`, `--azure-deployment`, `--semantic-threshold-percentile` |

### Core Options

| Flag              | Description                                      | Default       |
| ----------------- | ------------------------------------------------ | ------------- |
| `--strategy`      | Splitting algorithm.                             | `recursive`   |
| `--chunk-size`    | Max size of each chunk (tokens/chars).           | `1024`        |
| `--chunk-overlap` | Overlap between adjacent chunks.                 | `128`         |
| `--overlap-unit`  | Unit for size/overlap: `tokens` or `characters`. | `tokens`      |
| `--encoding-name` | *tiktoken* encoding for token counting.          | `cl100k_base` |

---

## Input File Contract

| Format                     | Handling                                                                         |
| -------------------------- | -------------------------------------------------------------------------------- |
| `.txt`, `.md`, `.markdown` | Entire file treated as one document.                                             |
| `.json`                    | Object or array; each object must include `text`, `page_content`, **or** `body`. |
| `.jsonl`, `.ndjson`        | One JSON object per line with the keys above.                                    |

---

## Advanced · Stable Chunk IDs

CLI generates deterministic IDs: `<prefix>#p<page>.<pos>-<hash>` where `<prefix>` is set by `--id-path-mode`.

* **`rel`** *(default)* – path relative to CWD (or `--id-base`). Falls back to hashed abs‑path when outside base.
* **`hash`** – always truncated SHA‑256 of abs‑path. Good for privacy / cross‑machine stability.
* **`abs`** – absolute file system path (may leak info). Requires `--force-abs-path`.

```bash
# Example: use hashing for the ID prefix
ingen chunk run my_document.txt --id-path-mode hash
```

---

## Development & Testing

```bash
# Install testing dependencies
uv pip install -e ".[chunk,test]"

# Run the test suite
uv run pytest ingenious/chunk/tests
```
