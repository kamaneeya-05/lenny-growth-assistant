# The Lenny Growth Assistant

An enterprise-grade, full-stack AI conversational product and growth advisor strictly grounded in the official archive of **Lenny's Podcast** and **Lenny's Newsletter** transcripts.

Built for Product Managers, Growth Leads, Founders, and Strategy Operators who want battle-tested frameworks, verified transcript citations, high-impact **~1,250-word Ship 30 for 30 essays**, and interactive **HTML/Markdown artifacts** previewed inside a sandboxed studio.

---

## Key Features

1. **Strict Source Grounding & Zero Hallucination Guardrail:**
   - Powered by a persistent hybrid vector (TF-IDF sublinear embeddings + BM25 keyword boosting) retrieval engine.
   - Every grounded response cites the exact episode/newsletter title, guest name, timestamp marker (e.g. `00:12:45`), and verbatim transcript passage.
   - For unsupported questions (e.g. baking recipes), gracefully refuses to answer rather than fabricating claims.

2. **Dedicated Skills & Growth Library:**
   - **Ship 30 for 30 Essayist:** Produces approximately 1,250-word atomic essays featuring the Pain/Promise/Proof/Path hook, 1-3-1 cadence rhythm, skimmable numbered headings, and grounded takeaways.
   - **Artifact Studio & Generator:** Creates standalone, complete HTML/CSS visual frameworks, product strategy one-pagers, and Markdown documents.
   - **Growth Skills Menu:** Quick-access menu for Ship 30 essays, HTML strategy one-pagers, Elena Verna B2B growth loops, and Founder Mode teardowns.

3. **In-App Sandboxed Artifact Studio (Live Editable):**
   - Side-by-side split screen inspired by Claude Artifacts.
   - **Live Interactive Editor:** Edit HTML or Markdown code live and preview changes instantly.
   - **Responsive Viewports:** Switch between Desktop (100%), Tablet (768px), and Mobile (375px) device bezel frames.
   - **Artifact Gallery:** Multi-artifact tabs within the same conversation session.
   - Secure `iframe` with `sandbox="allow-scripts"` (strictly isolated from parent cookies, storage, and DOM).
   - Fullscreen presentation mode, one-click copy, and file export (`.html`/`.md`).

4. **Transcript Archive Search Explorer & Audio Player:**
   - Real-time search across all 660+ indexed chunks by keyword, guest, or topic.
   - One-click "Ask Assistant About This" to send insights into active chat.
   - Interactive podcast episode audio player simulation with scrubber, timestamps, and quote sharing.

5. **Chat Session Search & Markdown Export:**
   - Instant search/filter across conversation history.
   - One-click export of complete conversations into clean Markdown (`.md`).

4. **Multi-Model Provider Abstraction:**
   - **Ollama (Local LLM):** Connects to `http://localhost:11434` with live connectivity health check. Recommended model: `llama3.2` or `mistral`.
   - **Cloud Providers:** Anthropic Claude (`claude-3-5-sonnet`) and OpenAI (`gpt-4o-mini`) via environment variables.
   - **Deterministic Offline Mock Provider:** Included out of the box for immediate evaluation and automated testing without external network or API key dependencies.

5. **Native Zero-Docker First-Class Support:**
   - Runs natively on Python 3.11 + SQLite and Node 18+ Vite.
   - Also includes full `docker-compose.yml` and PostgreSQL configuration for containerized production setups.

---

## Technology Stack

- **Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, HTTPX, Pytest.
- **Database:** SQLite (default native zero-friction) / PostgreSQL (Docker alternative).
- **Retrieval Engine:** Scikit-Learn TF-IDF vectorizer + Cosine Similarity + BM25 keyword matcher + Persistent NumPy index.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React icons.
- **Knowledge Base Source:** Ingested from the official free starter pack [`LennysNewsletter/lennys-newsletterpodcastdata`](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata).

---

## Quickstart Guide (Evaluator Walkthrough)

### 1. Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** and `npm` installed
- *(Optional)* **Ollama** installed if running local models

### 2. Clone & Environment Setup
```bash
# Clone or navigate to the repository
cd oogway

# Copy example environment file
cp .env.example .env
```

The default `.env` is already configured for instant native execution with SQLite and offline demo mode:
```ini
DATABASE_URL=sqlite:///./data/lenny_assistant.db
DEFAULT_MODEL_PROVIDER=ollama
DEFAULT_MODEL_NAME=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Transcript Ingestion (Already Seeded!)
The repository comes pre-seeded with 14 core podcast transcripts and newsletters in `data/fixtures/` and an active vector index in `data/vector_store/`.

To re-index or download additional transcripts from Lenny's official starter pack:
```bash
python scripts/ingest_transcripts.py --download
```

### 4. Start the Application

Open two terminal windows:

#### Terminal 1: Start Backend (FastAPI)
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The backend API will be live at `http://localhost:8000`. Interactive Swagger docs available at `http://localhost:8000/docs`.*

#### Terminal 2: Start Frontend (Vite)
```bash
cd frontend
npm install
npm run dev
```
*The web interface will open at `http://localhost:5173`.*

---

## Model Configuration: Local (Ollama) & Cloud (Groq / OpenAI / Claude)

### Option A: Local Ollama (Mandatory for Take-Home Demo)
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull and serve the lightweight model:
   ```bash
   ollama pull llama3.2
   ollama serve
   ```
3. Set in `.env`:
   ```ini
   DEFAULT_MODEL_PROVIDER=ollama
   DEFAULT_MODEL_NAME=llama3.2
   ```
4. The web UI at `http://localhost:5173` will automatically detect Ollama online at `http://localhost:11434` with a green indicator.

### Option B: High-Speed Cloud via Groq (Free, Zero RAM/Disk)
1. Get a free API key at [console.groq.com](https://console.groq.com).
2. Set in `.env`:
   ```ini
   DEFAULT_MODEL_PROVIDER=openai
   DEFAULT_MODEL_NAME=llama-3.3-70b-versatile
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   OPENAI_API_KEY=gsk_your_groq_key_here
   ```

### Option C: Cloud via OpenAI or Anthropic Claude
```ini
# OpenAI
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...

# Anthropic Claude
DEFAULT_MODEL_PROVIDER=anthropic
DEFAULT_MODEL_NAME=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

### Option D: Deterministic Offline Evaluator (Default Fallback)
If no local model or API key is detected, the built-in deterministic provider safely handles all queries, citations, Ship 30 essays, and HTML artifact generation with zero latency and 0 external dependencies.

---

## Running Automated Tests

Run the full backend test suite covering sessions, health, vector retrieval, parser, skills, and model providers:

```bash
pytest -v
```

**Expected Result:** `18 passed in ~17s (100% pass rate)`

Validate the frontend TypeScript build:

```bash
cd frontend
npm run build
```

**Expected Result:** `✓ built in ~13s (0 errors)`

---

## Evaluation Test Scenarios

Try these demo prompts to evaluate the core requirements:

| Test Scenario | Sample Prompt | Expected System Behavior |
| :--- | :--- | :--- |
| **1. Grounded Q&A** | *"What does Adam Mosseri say about AI being a tailwind for authenticity and taste?"* | Returns concrete advice directly synthesized from Adam Mosseri's episode with clickable citation pill showing timestamp `(00:00:00)` and verbatim quote. |
| **2. Contextual Follow-up** | *"How does Elena Verna approach B2B growth loops compared to that?"* | Preserves conversation context, retrieves Elena Verna's transcript, and highlights differences in self-serve and product-led loops. |
| **3. Guardrail Refusal** | *"What is Lenny's favorite recipe for chocolate cake?"* | Returns: *"I couldn't find enough support for that in the available Lenny transcript knowledge base. I don't want to present an unsupported claim as something Lenny or his guests said."* Zero fake citations. |
| **4. Ship 30 for 30 Essay** | *"Turn Adam Mosseri's advice on taste into a Ship 30 for 30 essay."* (or click the quick pill) | Generates an approximately 1,250-word atomic essay formatted with Hook (Pain/Promise/Proof/Path), 1-3-1 cadence rhythm, skimmable numbered headings, and cited sources. |
| **5. HTML Artifact Studio** | *"Create an HTML product strategy one-pager based on this."* (or click the quick pill) | Automatically opens the Artifact Studio on the right, rendering a clean, responsive HTML/CSS framework inside a sandboxed `iframe`. User can toggle to raw code and copy. |

---

## REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | System health check (DB, Vector Store, Provider reachability) |
| `/api/sessions` | `POST` | Create a new isolated chat session |
| `/api/sessions` | `GET` | List all sessions ordered by recency |
| `/api/sessions/{id}` | `GET` | Fetch session history and messages |
| `/api/sessions/{id}` | `DELETE` | Delete session and cascade artifacts |
| `/api/sessions/{id}/messages` | `POST` | Post message, run grounded agent, and persist responses |
| `/api/artifacts/{id}` | `GET` | Retrieve generated HTML/Markdown artifact by ID |
| `/api/models` | `GET` | List available models and Ollama health status |
| `/api/knowledge/status` | `GET` | Check indexed chunks, sources, and vocabulary |
| `/api/knowledge/ingest` | `POST` | Trigger background re-indexing or transcript download |

---

## Security & Sandboxing Architecture

1. **Untrusted HTML Sandboxing:**
   - Generated HTML is rendered in an `<iframe sandbox="allow-scripts" srcDoc="...">`.
   - The sandbox policy blocks same-origin access (`allow-same-origin` is omitted), preventing child code from accessing parent cookies, `localStorage`, or application tokens.
2. **Input Validation:**
   - Pydantic models validate input strings, limiting maximum prompt length to 10,000 characters.
   - Session IDs are strictly typed UUIDs.
3. **No Secret Leaks:**
   - Zero hardcoded credentials. All secrets are loaded via `.env`.

---

## Project Structure

```
oogway/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST route handlers (health, chat, sessions, artifacts, models)
│   │   ├── core/                # App configuration (Pydantic Settings)
│   │   ├── db/                  # Database models & connection (SQLAlchemy 2.0)
│   │   ├── schemas/             # Pydantic request/response contracts
│   │   ├── services/
│   │   │   ├── agent/           # Orchestrator & dedicated skills (Ship 30, Artifacts)
│   │   │   ├── llm/             # Provider abstraction (Ollama, Cloud, Mock)
│   │   │   ├── ingestion.py     # Transcript parser & semantic chunker
│   │   │   └── vector_store.py  # Hybrid TF-IDF + BM25 keyword retrieval engine
│   │   └── main.py              # FastAPI application entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/          # Sidebar, ChatHeader, MessageItem, ArtifactStudio, CitationModal
│   │   ├── services/            # Typed API client
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # Root React application
│   │   └── index.css            # Calm knowledge-work design tokens (Tailwind CSS)
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── fixtures/                # Real Lenny transcript fixture files (offline evaluator ready)
│   ├── transcripts/             # Ingested raw podcast and newsletter markdown files
│   └── vector_store/            # Persistent vector index (chunks, metadata, matrices)
├── scripts/
│   └── ingest_transcripts.py    # Transcript fetch & indexing pipeline CLI
├── tests/                       # Automated Pytest suite (100% pass rate)
├── agent-transcripts/           # Engineering trajectory and debugging logs
├── PRD.md                       # Complete Product Requirements Document
├── architecture.md              # System Architecture & Technical Design
├── design.md                    # UI/UX Specification & Design Tokens
├── docker-compose.yml           # Optional containerized deployment topology
├── Dockerfile.backend
└── README.md
```
