# News Podcast Generator

> A local web app that generates AI-powered news podcasts. Users select topics, review sources, pick an AI model for script generation, choose a voice for text-to-speech, and download the final audio.

## Architecture

```
Browser (Phone/PC) → FastAPI Server (Python)
                        ├── /fetch-news       → News Service (DuckDuckGo)
                        ├── /generate-script  → Langchain + Groq LLM + ChromaDB
                        └── /generate-audio   → edge-tts (Microsoft Edge TTS)
```

4-step SPA (Single Page App) — all steps in one HTML page, state managed in JavaScript.

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| Web Server | **FastAPI** (Python) | Class requirement, async support, auto-docs |
| Frontend | **Bootstrap 5** (CDN) | Responsive on PC and phone |
| News Search | **ddgs** (DuckDuckGo) | Free, no API key required |
| Vector Database | **ChromaDB** (in-memory) | Stores article embeddings for RAG |
| Embeddings | **all-MiniLM-L6-v2** (HuggingFace) | 384-dim sentence embeddings |
| LLM | **Groq API** (various models) | Free tier, fast inference |
| Text-to-Speech | **edge-tts** | Free, neural voices, runs locally |

## UI Flow — 4 Steps

### Step 1 — Topic Selection
- Country dropdown (Worldwide, USA, England, Canada, Australia, India, Nepal, Japan, South Korea, Philippines, China)
- Timeline dropdown (Hot, Last Week, Last Month, Last Year)
- Predefined topic chips (Technology, Sports, Politics, Science, Health, Business, Entertainment, World News, Local News)
- Custom topic search bar with Add button
- "Select All" toggle
- **Next** button (disabled until ≥1 topic selected)

### Step 2 — Review Sources
- For each topic, a card listing all fetched articles
- Each article shows: title (plain text), source domain, publication date
- **Refresh** button — re-fetches fresh results from DuckDuckGo
- **Back** button → Step 1
- **Next** button → Step 3 (disabled if no articles found)

### Step 3 — Generate Script
- AI Model dropdown (Llama 3.3 70B, Llama 3.1 8B, Llama 4 Scout 17B, Qwen 3 32B)
- **Generate Script** button with loading spinner
- Transcript displayed below after generation
- **Refresh** button (same as Generate — lets user change model and retry)
- **Back** button → Step 2
- **Next** button → Step 4 (disabled until script is generated)

### Step 4 — Generate Audio
- Voice radio buttons (Female / Male)
- **Generate Audio** button with loading spinner
- Audio player appears after generation
- **Download Audio** button (filename: `podcast-YYYYMMDD-HHMMSS.mp3`)
- **Back** button → Step 3

## Endpoint Reference

| Method | Endpoint | Input | Output |
|---|---|---|---|
| `GET` | `/` | — | Renders `index.html` with config data |
| `POST` | `/fetch-news` | `{topics, country, timelimit}` | `{articles_by_topic, topics_found}` |
| `POST` | `/generate-script` | `{articles_by_topic, model}` | `{script}` |
| `POST` | `/generate-audio` | `{script, voice}` | `{audio_url}` |

## Project Structure

```
news-podcast-generator/
├── app.py                       # FastAPI app — routes + orchestration
├── .env                         # GROQ_API_KEY (not committed)
├── requirements.txt            # Python dependencies
├── services/
│   ├── news_service.py         # DuckDuckGo search with fallback logic
│   ├── script_generator.py     # Langchain + ChromaDB + Groq pipeline
│   └── tts_service.py          # edge-tts wrapper
├── templates/
│   └── index.html              # 4-step SPA (Bootstrap 5 + vanilla JS)
├── static/
│   └── audio/                  # Generated .mp3 files
└── docs/
    ├── News Podcast Generator Design.md        # Original design spec
    └── News Podcast Generator - Complete Guide.md  # This file
```

## Services Detail

### News Service (`services/news_service.py`)

Wraps `ddgs.news()` with a 4-tier fallback cascade per topic:

1. Try: `topic + region + timelimit`
2. Fallback: `topic + wt-wt (worldwide) + timelimit` (if region-specific fails)
3. Fallback: `topic + best-effort region + no timelimit` (if timelimit-specific fails)
4. Fallback: `topic.lower() + wt-wt + no timelimit` (if uppercase/case fails)

Returns `dict[topic → list[{title, body, url, date}]]`.

### Script Generator (`services/script_generator.py`)

Langchain RAG pipeline:

1. **Build context** — Converts each article into a Langchain `Document` with `page_content = "Title: {title}\n{body}"` and `metadata = {topic, title}`
2. **Split** — `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`
3. **Embed** — `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")` → 384-dim vectors
4. **Store** — ChromaDB stores vectors in-memory (created per-request, deleted after)
5. **Retrieve** — Retriever returns all chunks (`k = len(chunks)`)
6. **Generate** — `RetrievalQA` chain with `ChatGroq` sends context + prompt template to Groq LLM

Available Groq models:
- `llama-3.3-70b-versatile` (default)
- `llama-3.1-8b-instant`
- `meta-llama/llama-4-scout-17b-16e-instruct`
- `qwen/qwen3-32b`

Prompt template asks the LLM to write a natural podcast script with intro, topic-grouped segments, and closing.

### TTS Service (`services/tts_service.py`)

Wraps `edge_tts.Communicate()` with two voices:
- Female: `en-US-JennyNeural`
- Male: `en-US-GuyNeural`

Output files saved to `static/audio/podcast-{YYYYMMDD-HHMMSS}.mp3`.

## Configuration

| Setting | Options | Default |
|---|---|---|
| Country | Worldwide, USA, England, Canada, Australia, India, Nepal, Japan, South Korea, Philippines, China | USA |
| Timeline | Hot, Last Week, Last Month, Last Year | Last Week |
| Topics | Technology, Sports, Politics, Science, Health, Business, Entertainment, World News, Local News, +custom | — |
| AI Model | Llama 3.3 70B, Llama 3.1 8B, Llama 4 Scout 17B, Qwen 3 32B | Llama 3.3 70B |
| Voice | Female, Male | Female |
| Max articles/topic | 5 | hardcoded in `search_news()` |

## Key Design Decisions

- **FastAPI over Flask** — Class requirement. Starlette's `TemplateResponse` signature is `(request, name, context)`.
- **SPA over separate routes** — All 4 steps share JS state (articles, script) without server-side sessions or URL routing complexity.
- **ChromaDB in-memory** — Created per `/generate-script` request, deleted via `delete_collection()` after use. No persistence needed.
- **DDGS fallback cascade** — Some DDG region+query combos return empty results; fallback ensures maximum coverage.
- **Local News resolution** — "Local News" topic resolves to the country name as the DDG search query (e.g., "Nepal" instead of "Nepal local news").
- **Audio filenames** — Timestamp-based (`podcast-20260623-183449.mp3`) instead of random UUIDs for meaningful filenames on download.

## Running

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

Access at `http://localhost:5000` or `http://<LAN-IP>:5000` from other devices.

## Environment

```
GROQ_API_KEY=gsk_...   # Required — get from console.groq.com/keys
```

Loaded via `python-dotenv` in `script_generator.py`.
