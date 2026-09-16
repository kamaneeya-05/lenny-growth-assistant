# Product Requirements Document (PRD)
# The Lenny Growth Assistant

**Status:** Approved / Active  
**Version:** 1.0.0  
**Target Audience:** Product Managers, Growth Leads, Founders, Product Team Members  
**Deployment Target:** Native Local (Python 3.11 + Vite/React 18), Optional Docker  

---

## 1. Executive Summary & Problem Statement

### 1.1 Primary User
Product Managers (PMs), Growth Practitioners, Founders, and Strategy Operators who rely on trusted, battle-tested advice from top technology leaders featured on *Lenny’s Podcast* and *Lenny’s Newsletter*.

### 1.2 User Job-to-be-Done (JTBD)
> "When I am wrestling with complex product management, growth, retention, or team leadership decisions, I want to interrogate Lenny’s extensive archive of conversations with world-class practitioners, so that I receive concrete, grounded frameworks, real-world examples, and actionable write-ups without spending hours manually listening to hundreds of podcast episodes."

### 1.3 Current Pain Points
1. **Unmanageable Content Volume:** Hundreds of hours of audio and newsletters make keyword searching tedious and context-free.
2. **Generic LLM Hallucinations:** Vanilla ChatGPT/Claude invent generic platitudes ("focus on user needs") instead of the specific, contrarian insights shared by guests like Shreyas Doshi, Adam Mosseri, Elena Verna, or Brian Chesky.
3. **Lack of Source Traceability:** Users cannot verify whether advice was actually said on the podcast or fabricated.
4. **Friction in Asset Creation:** Translating raw insights into executive one-pagers, strategy docs, or high-engagement Ship 30 for 30 essays requires tedious prompt engineering.

### 1.4 How The Assistant Solves This
- **Grounded RAG Engine:** Retrieves exact passages from real Lenny transcript archives.
- **Strict Source Fidelity:** Every response cites the episode title, guest name, timestamp, and source URL. Unsupported queries explicitly declare insufficient evidence rather than hallucinating.
- **Dedicated Skills:**
  - **Ship 30 for 30 Essayist:** Produces ~1,250-word atomic essays featuring the 1-3-1 rhythm, hook (Pain/Promise/Proof/Path), skimmable subheadings, and actionable takeaways.
  - **Artifact Generator:** Creates production-ready Markdown documents and sandboxed HTML/CSS deliverables (strategy one-pagers, growth loops, comparison tables).
- **In-App Artifact Viewer:** Interactive side-by-side preview with secure iframe sandboxing, raw code inspection, and one-click copy.
- **Flexible Model Selection:** Runs locally on Ollama (no cloud API keys required for local demos) and supports cloud providers (Anthropic Claude, OpenAI).

---

## 2. Success Metrics

| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Retrieval-Grounded Answer Rate** | $\ge 95\%$ | Queries backed by knowledge base contain at least 1 verified citation |
| **Citation Source Coverage** | $100\%$ of grounded answers | All citations include Title, Guest, Timestamp, and Excerpt |
| **Unsupported Query Handling** | $100\%$ | Zero fabricated claims on unrepresented topics (returns graceful refusal) |
| **Ship 30 Essay Word Count** | $1,250 \pm 150$ words | Word counter on generated essay skill output |
| **Time to First Token / Response (Local)** | $< 3.5$ s (Local) / $< 1.5$ s (Cloud) | Server latency logs |
| **Artifact Generation Success Rate** | $\ge 98\%$ | Valid HTML/Markdown generated without parsing or rendering errors |
| **Zero-Docker Local Setup** | $< 3$ minutes | Fresh clone run via native Python and Vite scripts |
| **Automated Test Pass Rate** | $100\%$ | Pytest backend suite + Vite frontend build |

---

## 3. Assumptions & Environment Constraints

1. **Transcript Source:** Ingested from the official free public starter pack (`LennysNewsletter/lennys-newsletterpodcastdata`), featuring 50 podcast episodes and 10 newsletters.
2. **Local Machine Hardware:** Evaluators may run on machines without active Docker daemons or dedicated GPUs. Therefore, direct native execution (SQLite + Python 3.11 + Node Vite) must be the primary zero-friction path.
3. **Ollama Availability:** Evaluators may or may not have Ollama installed or running. The system must probe `http://localhost:11434`, report live status in the UI, and provide a deterministic test/mock provider fallback so the UI never breaks.
4. **Security & Artifacts:** Generated HTML is untrusted user-prompted code. It must render in a sandboxed iframe with strict Content Security Policy (`sandbox="allow-scripts"` without `allow-same-origin`) to prevent session hijack or parent DOM access.
5. **No Secret Leaks:** No API keys are committed. All secrets are loaded via `.env` with fallback to local mock/Ollama modes.

---

## 4. Scope

### 4.1 In Scope (MVP Deliverables)
- Full conversation UI with sidebar, session list, new chat, and message feed.
- Persistent session storage in PostgreSQL / SQLite.
- Hybrid semantic & keyword retrieval over Lenny's transcript archive.
- Inline citation badges linking to detailed source drawer (episode, guest, timestamp, quote).
- Ship 30 for 30 essay generation skill (~1,250 words, hook, 1-3-1 rhythm, subheadings).
- Artifact generation skill producing complete Markdown and HTML/CSS.
- Split-screen Artifact Viewer with sandboxed iframe, raw code toggle, and copy button.
- Model provider switching: Ollama (local) + Anthropic/OpenAI (cloud) + Deterministic Mock.
- Ingestion pipeline script (`scripts/ingest_transcripts.py`) with bundled seed fixtures.
- Automated test suite (Pytest + HTTPX).
- Complete documentation (`README.md`, `architecture.md`, `design.md`, `agent-transcripts/`).

### 4.2 Out of Scope (Explicit Exclusions)
- Multi-tenant enterprise SSO (OAuth / SAML) – MVP uses local session management.
- Direct audio waveform playback – MVP indexes text transcripts with timestamps.
- Cloud hosting deployment pipeline – MVP focuses on evaluator-friendly local reproducibility.

---

## 5. User Flows & Acceptance Criteria

### Flow 1: Ask a Grounded Question
- **Action:** User asks "What did Adam Mosseri say about AI and authenticity?"
- **Acceptance Criteria:**
  - Assistant retrieves relevant chunks from the Adam Mosseri episode.
  - Response directly synthesizes Mosseri's points on taste, craft, and authenticity.
  - Citation pills appear showing "Adam Mosseri: AI is a tailwind for authenticity", guest "Adam Mosseri", timestamp `(00:00:00)`, and verbatim excerpt.
  - No unsupported claims are added.

### Flow 2: Follow-up in Context
- **Action:** User asks "How does that compare to what Shreyas Doshi says about product sense?"
- **Acceptance Criteria:**
  - Session history is preserved; the model understands "that" refers to Mosseri's view.
  - System retrieves Shreyas Doshi chunks and produces a comparative response.
  - Separate citations for both guests are provided.

### Flow 3: Unsupported Question Graceful Handling
- **Action:** User asks "What is Lenny's recipe for beef bourguignon?"
- **Acceptance Criteria:**
  - Retrieval yields scores below confidence threshold.
  - Assistant responds: *"I couldn't find enough support for that in the available Lenny transcript knowledge base. I don't want to present an unsupported claim as something Lenny or his guests said."*
  - Zero fake citations are returned.

### Flow 4: Generate a Ship 30 for 30 Essay
- **Action:** User asks "Turn that into a Ship 30 for 30 essay."
- **Acceptance Criteria:**
  - Dedicated writing skill activates.
  - Outputs approximately 1,250 words.
  - Formatted with:
    - Compelling Headline with outcome promise.
    - Hook: Pain, Promise, Proof, Path.
    - 1-3-1 rhythm cadence.
    - Skimmable subheadings.
    - Bullet points with bold lead-ins.
    - Core takeaways and cited sources.

### Flow 5: Generate & Inspect an HTML/CSS Artifact
- **Action:** User asks "Create a product strategy one-pager in HTML based on this."
- **Acceptance Criteria:**
  - Dedicated artifact skill generates valid HTML/CSS.
  - Artifact Viewer automatically opens in split-screen mode.
  - Content renders inside a sandboxed `iframe`.
  - User can toggle between Visual Preview and Source Code.
  - "Copy Code" button copies code to clipboard.

### Flow 6: Switch Model Providers
- **Action:** User selects Ollama from the dropdown, then Cloud Provider.
- **Acceptance Criteria:**
  - UI updates active provider pill.
  - If Ollama is offline, system displays warning badge and seamlessly falls back to mock/cloud without app crash.
