# Gloss

**Gloss** is a lightweight, agent-based vocabulary assistant designed for **intermediate to advanced English learners** who want to understand **real English as it is actually used**—not just textbook definitions.

Gloss helps you:

- understand unfamiliar or confusing words and phrases
- learn how they are used in real contexts
- resolve ambiguous meanings
- build a personal, long-term vocabulary knowledge base in Notion

This repository contains the **MVP implementation** of Gloss, including a **simple Web UI**.

---

## Live Demo (Current Status)

A live demo is available at **[https://gloss.xuyuanhui.org](https://gloss.xuyuanhui.org)**, and the system can also be run locally.

⚠️ **Important note**
The Notion integration used by the hosted web app is currently connected to **Yuanhui’s personal Notion database**.
Please do **not** rely on the hosted demo for shared or production usage.

User-specific Notion databases and credentials will be supported in a future version.

You are encouraged to run Gloss locally and connect it to your own Notion workspace.

---

## Key Features (MVP)

### 1. Smart Meaning Resolution

- Accepts a single word or short phrase as input
- Detects when a term is **ambiguous** (e.g. _shrink_)
- Prompts the user to select the intended meaning when necessary
- Produces one clear, decisive definition per lookup

---

### 2. Practical Usage Guidance

For each resolved meaning, Gloss provides:

- the _type of lexical difficulty_ involved (e.g. cultural literacy, slang, polysemous extension, or jargon)
- concise usage notes (register, common patterns, and misuse risks)
- one natural example sentence
- a small set of related words or phrases

The focus is on **how native speakers actually use the word**, rather than exhaustive dictionary coverage.

---

### 3. Automatic Vocabulary Memory (Notion)

- Every lookup is converted into a structured Notion page
- Stored fields include:

  - word / phrase
  - core meaning
  - meaning type (e.g. Cultural-Literacy, Polysemous Extension)
  - domain(s)
  - usage notes
  - example sentence
  - related words

This builds a growing, searchable personal vocabulary database over time.

---

### 4. Deterministic Agent Pipeline

The MVP uses a **Python-controlled pipeline**:

1. **Clarifying Agent** – handles ambiguity and meaning resolution
2. **Generator Agent** – produces usage notes, examples, and related words
3. **Python pipeline** – persists the result to Notion

This design avoids hidden agent behavior and keeps the system **predictable, debuggable, and extensible**.

---

## Running Gloss Locally

### Prerequisites

- Python 3.10+
- An OpenRouter API key
- A Notion integration token
- A Notion database configured with the expected properties

---

### 1. Clone the repository

```bash
git clone https://github.com/imyuanhui/gloss.git
cd gloss
```

---

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
NOTION_TOKEN=your-notion-token
NOTION_DATA_SOURCE_ID=your-notion-data-source-id
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODELS=your-preferred-llm-model
CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
MOCK_MODE=false
```

---

### 5. Run the application

```bash
uvicorn app:main --reload
```

You will see a greeting message similar to:

```
Hello, this is Gloss.
I help you understand and use real English vocabulary.
Enter a word or short phrase to look up. Context is optional.
Every lookup will be saved to your Notion vocabulary database.
```

Follow the prompts to:

- enter a word or phrase
- select a meaning if the term is ambiguous
- view the generated explanation and usage

---

## Example Workflow

1. User enters:

```
shrink
```

2. Gloss detects ambiguity and presents options:

```
1) slang for a therapist
2) to make or become smaller
```

3. User selects option `1`

4. Gloss returns:

- a clear meaning
- usage notes
- an example sentence

5. The entry is saved to Notion automatically.

---

## Current Limitations (MVP)

- Single-user only
- Notion database is hard-coded
- No user accounts or personalization yet

These limitations are intentional for the MVP.

---

## Next Development Plan

### 1. User Accounts (High Priority)

- Add user registration and login
- Each user will be able to:

  - connect their own Notion database
  - choose their preferred LLM provider and model

This enables true multi-tenant usage.

---

### 2. Credential Security & Encryption

- Encrypt user-provided credentials, including:

  - Notion tokens
  - OpenRouter (or other model provider) tokens

- Ensure secrets are never stored or transmitted in plaintext

---

### Future Ideas (Post-MVP)

- Improved Web UI
- Browser extension
- Usage validation (e.g. “Is this sentence natural?”)
- Vocabulary review and spaced repetition
- Cross-word semantic linking inside Notion

---

## Philosophy

Gloss is not a dictionary and not a flashcard app.

It is a **vocabulary intelligence system** designed to help learners:

- understand cultural and contextual meaning
- avoid subtle misuse
- build durable language knowledge over time
