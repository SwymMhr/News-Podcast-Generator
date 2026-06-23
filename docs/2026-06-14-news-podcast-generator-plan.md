# News Podcast Generator Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local web app that lets users select topics, fetches recent news, generates a podcast script, and converts it to speech.

**Architecture:** Flask backend orchestrates a 3-step pipeline (search → script → TTS). Single-page Bootstrap frontend handles topic selection, progress display, and audio playback. All services run locally with free tools.

**Tech Stack:** Python 3.12, Flask, Bootstrap 5, duckduckgo_search, edge-tts

---

### Task 1: requirements.txt and project setup

**Files:**
- Create: `D:\My projects\News Podcast Generator\requirements.txt`

- [ ] **Step 1: Create requirements.txt**

```txt
flask>=3.0
duckduckgo_search>=8.0
edge-tts>=7.0
```

---

### Task 2: News Service

**Files:**
- Create: `D:\My projects\News Podcast Generator\services\__init__.py`
- Create: `D:\My projects\News Podcast Generator\services\news_service.py`

- [ ] **Step 1: Create services __init__.py**

Empty file to make it a package.

- [ ] **Step 2: Create news_service.py**

```python
from duckduckgo_search import DDGS
from datetime import datetime, timedelta


def search_news(topics, max_results=5):
    news_by_topic = {}
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    for topic in topics:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    keywords=topic,
                    region="wt-wt",
                    timelimit="w",
                    max_results=max_results,
                ))
            articles = [
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("url", ""),
                    "date": r.get("date", ""),
                }
                for r in results
            ]
            if articles:
                news_by_topic[topic] = articles
        except Exception as e:
            news_by_topic[topic] = []
    return news_by_topic
```

---

### Task 3: Script Generator

**Files:**
- Create: `D:\My projects\News Podcast Generator\services\script_generator.py`

- [ ] **Step 1: Create script_generator.py**

```python
def generate_script(news_by_topic):
    lines = []
    topics = [t for t, articles in news_by_topic.items() if articles]
    article_count = sum(len(a) for a in news_by_topic.values())

    if not topics:
        return "No news found for the selected topics."

    lines.append(f"Welcome to your AI-generated news podcast.")
    lines.append(f"Today we have {article_count} stories across {len(topics)} topics.\n")

    for topic in topics:
        articles = news_by_topic[topic]
        lines.append(f"--- {topic.upper()} ---\n")
        for i, article in enumerate(articles, 1):
            title = article.get("title", "Untitled")
            body = article.get("body", "")
            lines.append(f"{i}. {title}")
            if body:
                lines.append(f"   {body}")
            lines.append("")

    lines.append("That wraps up today's news podcast. Thanks for listening!")
    return "\n".join(lines)
```

---

### Task 4: TTS Service

**Files:**
- Create: `D:\My projects\News Podcast Generator\services\tts_service.py`

- [ ] **Step 1: Create tts_service.py**

```python
import edge_tts
import uuid
import os

VOICE = "en-US-JennyNeural"  # Natural female voice
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")


async def text_to_speech(script):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    communicate = edge_tts.Communicate(script, VOICE)
    await communicate.save(filepath)

    return filename
```

---

### Task 5: Flask App

**Files:**
- Create: `D:\My projects\News Podcast Generator\app.py`

- [ ] **Step 1: Create app.py**

```python
import asyncio
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from services.news_service import search_news
from services.script_generator import generate_script
from services.tts_service import text_to_speech

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

PREDEFINED_TOPICS = [
    "Technology", "Sports", "Politics", "Science",
    "Health", "Business", "Entertainment", "World News",
]


@app.route("/")
def index():
    return render_template("index.html", topics=PREDEFINED_TOPICS)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    topics = data.get("topics", [])

    if not topics:
        return jsonify({"error": "Select at least one topic"}), 400

    news_by_topic = search_news(topics)
    script = generate_script(news_by_topic)

    audio_filename = asyncio.run(text_to_speech(script))

    return jsonify({
        "script": script,
        "audio_url": f"/audio/{audio_filename}",
        "topics_found": {
            t: len(articles)
            for t, articles in news_by_topic.items()
        },
    })


@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(
        os.path.join(app.root_path, "static", "audio"), filename
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

---

### Task 6: HTML Template

**Files:**
- Create: `D:\My projects\News Podcast Generator\templates\index.html`

- [ ] **Step 1: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Podcast Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-4" style="max-width: 720px;">
        <h1 class="mb-1">News Podcast Generator</h1>
        <p class="text-muted mb-4">Select topics to generate a custom news podcast from this week's headlines.</p>

        <!-- Screen 1: Topic Selection -->
        <div id="screen-topics">
            <div class="mb-3">
                <label class="form-label fw-semibold">Choose topics:</label>
                <div id="topic-chips" class="d-flex flex-wrap gap-2 mb-3">
                    {% for topic in topics %}
                    <button class="btn btn-outline-primary topic-chip" data-topic="{{ topic }}"
                            onclick="toggleTopic(this)">{{ topic }}</button>
                    {% endfor %}
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label fw-semibold">Search custom topic:</label>
                <div class="input-group">
                    <input type="text" id="custom-topic-input" class="form-control"
                           placeholder="Type a topic and press Add..." maxlength="50">
                    <button class="btn btn-primary" onclick="addCustomTopic()">Add</button>
                </div>
            </div>
            <div id="selected-topics" class="d-flex flex-wrap gap-2 mb-3"></div>
            <button class="btn btn-success btn-lg w-100" onclick="generatePodcast()">Generate Podcast</button>
        </div>

        <!-- Screen 2: Progress -->
        <div id="screen-progress" class="d-none text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <p id="progress-text" class="fs-5">Searching news...</p>
        </div>

        <!-- Screen 3: Player -->
        <div id="screen-player" class="d-none">
            <audio id="audio-player" controls class="w-100 mb-3"></audio>
            <div class="d-flex gap-2 mb-3">
                <button class="btn btn-outline-secondary" onclick="resetAll()">Generate New</button>
            </div>
            <label class="fw-semibold mb-2">Transcript:</label>
            <pre id="script-display" class="bg-white border rounded p-3"
                 style="white-space: pre-wrap; max-height: 60vh; overflow-y: auto;"></pre>
        </div>
    </div>

    <script>
        const selectedTopics = new Set();

        function toggleTopic(btn) {
            const topic = btn.dataset.topic;
            if (selectedTopics.has(topic)) {
                selectedTopics.delete(topic);
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline-primary");
            } else {
                selectedTopics.add(topic);
                btn.classList.remove("btn-outline-primary");
                btn.classList.add("btn-primary");
            }
            renderSelected();
        }

        function addCustomTopic() {
            const input = document.getElementById("custom-topic-input");
            const topic = input.value.trim();
            if (!topic || selectedTopics.has(topic)) return;
            selectedTopics.add(topic);
            input.value = "";
            renderSelected();
            // Also add a chip in the predefined area if not already there
            const existing = document.querySelector(`.topic-chip[data-topic="${topic}"]`);
            if (existing) {
                existing.classList.remove("btn-outline-primary");
                existing.classList.add("btn-primary");
            }
        }

        function renderSelected() {
            const container = document.getElementById("selected-topics");
            if (selectedTopics.size === 0) {
                container.innerHTML = '<span class="text-muted small">No topics selected yet.</span>';
                return;
            }
            container.innerHTML = "";
            selectedTopics.forEach(topic => {
                const chip = document.createElement("span");
                chip.className = "badge bg-primary fs-6 d-inline-flex align-items-center gap-1";
                chip.innerHTML = `${topic} <span style="cursor:pointer" onclick="removeTopic('${topic}')">&times;</span>`;
                container.appendChild(chip);
            });
        }

        function removeTopic(topic) {
            selectedTopics.delete(topic);
            const btn = document.querySelector(`.topic-chip[data-topic="${topic}"]`);
            if (btn) {
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline-primary");
            }
            renderSelected();
        }

        function showScreen(id) {
            document.querySelectorAll("[id^=screen-]").forEach(s => s.classList.add("d-none"));
            document.getElementById(id).classList.remove("d-none");
        }

        async function generatePodcast() {
            if (selectedTopics.size === 0) {
                alert("Please select at least one topic.");
                return;
            }

            showScreen("screen-progress");
            document.getElementById("progress-text").textContent = "Searching news...";

            try {
                const res = await fetch("/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ topics: Array.from(selectedTopics) }),
                });
                const data = await res.json();

                if (data.error) {
                    alert(data.error);
                    showScreen("screen-topics");
                    return;
                }

                document.getElementById("progress-text").textContent = "Generating audio...";
                await new Promise(r => setTimeout(r, 500));

                document.getElementById("script-display").textContent = data.script;
                const player = document.getElementById("audio-player");
                player.src = data.audio_url;
                player.load();

                showScreen("screen-player");
            } catch (err) {
                alert("Something went wrong. Check the server console.");
                showScreen("screen-topics");
            }
        }

        function resetAll() {
            selectedTopics.clear();
            document.querySelectorAll(".topic-chip").forEach(btn => {
                btn.classList.remove("btn-primary");
                btn.classList.add("btn-outline-primary");
            });
            renderSelected();
            showScreen("screen-topics");
        }
    </script>
</body>
</html>
```

---

### Task 7: Run and verify

- [ ] **Step 1: Start the Flask app**

```powershell
cd "D:\My projects\News Podcast Generator"
python app.py
```

Expected: Server starts on `http://0.0.0.0:5000`

- [ ] **Step 2: Open browser**

Open `http://localhost:5000` — should see topic selection page.
Select a few topics, click "Generate Podcast", verify progress → audio player → transcript flow works.

- [ ] **Step 3: Test on phone**

On same WiFi, open `<YOUR_LOCAL_IP>:5000` in phone browser. Verify responsive layout and full flow.
