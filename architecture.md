# Architecture & Technical Design
# The Lenny Growth Assistant

---

## 1. System Overview & Topology

The Lenny Growth Assistant is built as a modular client-server application optimized for both developer ergonomics and evaluator reliability.

```
+-------------------------------------------------------------------------------+
|                             CLIENT APPLICATION                                |
|   React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons                  |
|                                                                               |
|  +-----------------------+  +---------------------+  +---------------------+  |
|  |     Sidebar & Nav     |  |    Chat Interface   |  |   Artifact Viewer   |  |
|  | - Session Management  |  | - Message Feed      |  | - Sandboxed iframe  |  |
|  | - Model Switcher      |  | - Grounded Badges   |  | - Markdown Renderer|  |
|  | - KB Health Status    |  | - Citation Drawer   |  | - Raw Code Inspector|  |
|  +-----------------------+  +---------------------+  +---------------------+  |
+-------------------------------------------------------------------------------+
                                      |
                            HTTP / REST / SSE
                                      v
+-------------------------------------------------------------------------------+
|                              FASTAPI BACKEND                                  |
|   Python 3.11 + Pydantic v2 + SQLAlchemy 2.0 (Native SQLite / PostgreSQL)      |
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  |                          ROUTING & CONTROLLERS                          |  |
|  |  /api/health   /api/sessions   /api/chat   /api/artifacts   /api/models  |  |
|  +-------------------------------------------------------------------------+  |
|                                      |                                        |
|  +-----------------------------------+-------------------------------------+  |
|  |                                   |                                     |  |
|  v                                   v                                     v  |
| +-----------------+         +-----------------+         +-----------------+   |
| |   AGENT LAYER   |         | RETRIEVAL STORE |         | PERSISTENCE DB  |   |
| | - Orchestrator  |         | - Hybrid Cosine |         | - Sessions      |   |
| | - Ship 30 Skill |<------->|   + BM25 Search |         | - Messages      |   |
| | - Artifact Skill|         | - Chunk Metadata|         | - Artifacts     |   |
| +-----------------+         | - Fast NumPy    |         | - Ingestion Logs|   |
|          |                  +-----------------+         +-----------------+   |
|          v                                                                    |
| +-------------------------------------------------------------------------+   |
| |                        MODEL PROVIDER ABSTRACTION                       |   |
| |  Ollama (Local :11434)  |  Anthropic / OpenAI (Cloud)  |  Mock (Offline)|   |
| +-------------------------------------------------------------------------+   |
+-------------------------------------------------------------------------------+
                                       ^
                                       |
                              INGESTION WORKFLOW
                  (scripts/ingest_transcripts.py / API)
                                       |
                    +------------------------------------+
                    |  Lenny Transcript Public Repo      |
                    |  (50 Podcasts + 10 Newsletters)    |
                    +------------------------------------+
```

---

## 2. Component Boundaries & Responsibilities

### 2.1 Backend Core
- **`app/core/config.py`**: Centralized Pydantic `BaseSettings` object managing environment variables, model defaults, database connection strings, and search thresholds.
- **`app/db/`**: SQLAlchemy 2.0 declarative models, asynchronous/synchronous session engine factory supporting native SQLite for instant execution and PostgreSQL for containerized deployments.
- **`app/services/vector_store.py`**: Hybrid vector store maintaining in-memory / persistent vector index (using TF-IDF / sentence embeddings and cosine similarity) alongside an inverted token index for exact keyword matching (guests, companies, frameworks).
- **`app/services/ingestion.py`**: Pipeline parsing markdown files with YAML frontmatter, splitting speeches by speaker markers (`**Speaker** (HH:MM:SS)`), producing 350-500 word overlapping chunks with metadata preservation.
- **`app/services/llm/`**: Model provider layer exposing a unified `complete(messages, system_prompt, temperature)` interface across Ollama, Cloud, and Mock engines.
- **`app/services/agent/`**: The core domain orchestrator:
  - Detects user intent (Question & Answer vs. Ship 30 for 30 essay vs. Artifact generation).
  - Retrieves grounded passages from the vector store.
  - Formats grounded prompts with strict provenance directives.
  - Parses outputs into structured text, citations, and artifacts.

### 2.2 Frontend Architecture
- **React 18 & TypeScript**: Full type safety matching backend schemas.
- **Tailwind CSS**: Modern, calm design tokens (slate/zinc dark & light modes, subtle border radii, crisp typography).
- **Sandboxed Artifact Viewer**: Runs generated HTML inside an `<iframe sandbox="allow-scripts">` element with `srcDoc`, preventing child scripts from accessing `window.parent`, localStorage, or authentication cookies.

---

## 3. Database Schema

The database tracks sessions, messages, generated artifacts, transcript sources, and ingestion history.

```
       +-----------------------+              +-----------------------+
       |       sessions        |              |       artifacts       |
       +-----------------------+              +-----------------------+
       | id: UUID (PK)         |<---+         | id: UUID (PK)         |
       | title: VARCHAR(255)   |    |         | session_id: UUID (FK) |----+
       | model_provider: VARCHAR|   |         | message_id: UUID (FK) |    |
       | model_name: VARCHAR   |    |         | title: VARCHAR(255)   |    |
       | created_at: TIMESTAMP |    |         | artifact_type: VARCHAR|    |
       | updated_at: TIMESTAMP |    |         | content: TEXT         |    |
       +-----------------------+    |         | created_at: TIMESTAMP |    |
                   |                |         +-----------------------+    |
                   | 1              |                                      |
                   |                | 1                                    |
                   v *              |                                      |
       +-----------------------+    |                                      |
       |       messages        |----+                                      |
       +-----------------------+                                           |
       | id: UUID (PK)         |                                           |
       | session_id: UUID (FK) |-------------------------------------------+
       | role: VARCHAR(20)     |
       | content: TEXT         |
       | citations: JSON       |
       | artifact_id: UUID     |
       | created_at: TIMESTAMP |
       +-----------------------+

       +-----------------------+              +-----------------------+
       |   transcript_sources  |              |   transcript_chunks   |
       +-----------------------+              +-----------------------+
       | id: UUID (PK)         | 1          * | id: UUID (PK)         |
       | title: VARCHAR(255)   |------------->| source_id: UUID (FK)  |
       | guest: VARCHAR(255)   |              | chunk_index: INT      |
       | source_type: VARCHAR  |              | speaker: VARCHAR(100) |
       | url: VARCHAR(512)     |              | timestamp_str: VARCHAR|
       | word_count: INT       |              | text: TEXT            |
       | date: VARCHAR(50)     |              | token_count: INT      |
       +-----------------------+              +-----------------------+
```

---

## 4. Ingestion & Retrieval Mathematics

### 4.1 Chunking Strategy
- Transcripts are parsed to identify speaker turns: `**Speaker Name** (HH:MM:SS): Paragraph`.
- Text is grouped into semantic windows of $300 - 450$ words with $50$ words overlap, preserving speaker identity, timestamp, episode title, and source URL in every chunk.

### 4.2 Hybrid Retrieval Formula
To balance semantic relevance with high-precision keyword recall (such as acronyms "PMF", "CAC", or specific guest names like "Brian Chesky"):

$$\text{Score}(q, d) = \alpha \cdot \text{CosineSimilarity}(v_q, v_d) + (1 - \alpha) \cdot \text{BM25Norm}(q, d)$$

Where:
- $\alpha = 0.70$ (weight towards semantic embeddings).
- $v_q, v_d$ are vector representations of query $q$ and document chunk $d$.
- Document chunks with $\text{Score} < \tau_{\text{threshold}}$ ($0.22$) are classified as non-matching. If all retrieved candidates fall below threshold, the system triggers the unsupported-answer policy.

---

## 5. Agent Orchestration & Skills

```
User Message
    |
    v
Intent Classifier (Prompt + Regex / Routing Layer)
    |
    +---> [Ship 30 for 30 Essay Skill]
    |       - Inputs: Topic / Grounded Context from History / Vector Search
    |       - Output: ~1,250-word Atomic Deep Dive (Hook -> 1-3-1 -> Headings -> Citations)
    |
    +---> [Artifact Generation Skill]
    |       - Inputs: Specification (Markdown / HTML+CSS) + Grounded Insights
    |       - Output: Self-contained Renderable Document / Visual Framework
    |
    +---> [Grounded Q&A Orchestrator]
            - Performs hybrid vector retrieval
            - Ranks chunks & extracts top-K (default K=4)
            - Checks confidence threshold
            - Injects strict provenance system prompt
            - Synthesizes grounded answer + citations
```

---

## 6. Model Provider Abstraction

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2500,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def check_health(self) -> ProviderStatus:
        pass
```

1. **Ollama Provider:** Queries `POST http://localhost:11434/api/chat` with timeout protection (30s) and probes `GET http://localhost:11434/api/tags` to verify installed models (e.g. `llama3.2`, `mistral`, `phi3`).
2. **Cloud Provider:** Sends standard requests to Anthropic Claude (`/v1/messages`) or OpenAI (`/v1/chat/completions`) using the configured environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
3. **Mock / Evaluation Provider:** Deterministic offline generator that parses retrieved transcript chunks and produces complete, citation-backed answers, Ship 30 essays, and HTML artifacts without requiring external servers or credentials.

---

## 7. Security Architecture

1. **Untrusted HTML Sandboxing:**
   - HTML/CSS artifacts are delivered with an artifact ID.
   - Rendered in `<iframe sandbox="allow-scripts" srcdoc="...">`.
   - The iframe has a distinct null origin, disallowing access to `document.cookie`, `localStorage`, and `window.parent`.
2. **Input Validation & Sanitization:**
   - Pydantic models validate input strings, limiting message length to 10,000 characters.
   - Session IDs are strictly validated as valid UUIDs.
3. **Secret Isolation:**
   - Zero hardcoded keys or passwords.
   - Environment variables loaded via `.env` file excluded from version control.
