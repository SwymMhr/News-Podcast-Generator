# News Podcast Generator

> A local web app that generates AI-powered news podcasts from user-selected topics.

## Architecture

```
Browser (Phone/PC) → Flask Server (Python)
                        ├── News Service (duckduckgo_search)
                        ├── Script Generator (template-based)
                        └── TTS Service (edge-tts)
```

3-tier architecture: browser talks to Flask, Flask orchestrates the pipeline step by step. No database needed — audio files stored temporarily in memory/disk.

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| Web Server | **Flask** (Python) | Lightweight, simple to deploy locally |
| Frontend | **Bootstrap 5** (CDN) | Responsive by default — works on PC and phone |
| News Search | **duckduckgo_search** | Free, no API key required |
| Script Generation | **Template-based** (Python string formatting) | No LLM API needed — pure logic |
| Text-to-Speech | **edge-tts** | Free, neural voices, runs locally |

## UI Flow

### Screen 1 — Topic Selection

- Predefined topic chips (Technology, Sports, Politics, Science, Health, Business, Entertainment, World News)
- Search bar to type any custom topic
- Selected topics displayed as removable chips
- "Generate Podcast" button

### Screen 2 — Generation Progress

- Status updates: "Searching news...", "Writing script...", "Generating audio..."
- Auto-advances when pipeline completes

### Screen 3 — Podcast Player

- Audio player with play/pause/seek
- Full scrollable transcript/script
- "Generate New" button to restart

## Pipeline

1. User selects topics → clicks "Generate"
2. Backend searches each topic via `duckduckgo_search` (last week's news)
3. Raw articles are collected, deduplicated, and sorted by topic
4. Script Generator formats articles into a cohesive podcast script:
   - Introduction
   - Per-topic segments (headlines → brief summaries)
   - Closing
5. Script text sent to `edge-tts` for neural speech generation
6. Audio file returned to browser with full transcript

## Project Structure

```
news-podcast-generator/
├── app.py                  # Flask main app (routes + pipeline orchestration)
├── services/
│   ├── news_service.py     # DuckDuckGo search wrapper
│   ├── script_generator.py # Template-based script builder
│   └── tts_service.py      # Edge-TTS wrapper
├── templates/
│   └── index.html          # Single-page responsive UI (Bootstrap)
├── static/
│   └── audio/              # Generated audio files
└── requirements.txt
```

## Error Handling

- Search fails → skip topic, show friendly message
- No results → "No recent news found for [topic]"
- TTS fails → show script without audio
- Empty selection → prompt to select at least one topic

## Future Ideas (out of scope for now)

- Different TTS voices / languages
- Podcast download as MP3
- Scheduled automatic generation
- History of past podcasts
