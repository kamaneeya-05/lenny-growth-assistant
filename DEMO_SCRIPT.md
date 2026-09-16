# The Lenny Growth Assistant — Evaluator Demo Script
**Role:** Forward Deployed Engineer Candidate  
**Target Duration:** ~2.5 Minutes (150 Seconds)  
**Format:** Screen Recording with Camera Enabled  

---

## Screen-by-Screen Demo Walkthrough

### [0:00 – 0:30] Screen 1: Problem Framing & Discovery Brief
*(Camera on candidate + Screen showing the clean Landing Page at `http://localhost:5173`)*

> "Hi everyone, I'm Kamaneeya, presenting **The Lenny Growth Assistant**—a full-stack AI knowledge engine built for product managers, growth leads, and founders.
>
> The problem we're solving is clear: Lenny's Podcast and Newsletter archive contains rich, gold-standard frameworks from world-class operators. But generic LLMs hallucinate unverified advice, and searching manually through transcripts is slow and fragmented.
>
> We built an internal assistant that does three things: strictly grounds answers in real transcript excerpts, crafts ~1,250-word Ship 30 for 30 essays, and generates interactive HTML strategy artifacts rendered right beside the chat in a sandboxed studio."

---

### [0:30 – 1:05] Screen 2 & 3: Grounded Q&A & Source Provenance
*(Action: Click the first prompt card on the landing page: 'What does Adam Mosseri say about AI and authenticity?')*

> "Let's ask a core product question: *'What does Adam Mosseri say about AI being a tailwind for authenticity?'*
>
> In under a second, our hybrid retrieval engine—combining sublinear TF-IDF vectors with keyword boosting—identifies the exact transcript chunks from Adam Mosseri's episode.
>
> Notice that every claim has a clickable citation pill. Clicking it opens our source inspector:
> - We see the episode title and guest name.
> - The normalized retrieval relevance score.
> - The exact timestamp marker—`00:00:00`—and the verbatim excerpt straight from the transcript.
> - Plus a direct link to the original Substack post."

---

### [1:05 – 1:25] Screen 4: Grounding Guardrail (Zero Hallucination)
*(Action: Type 'What is Lenny's recipe for chocolate cake?' and press Enter)*

> "A critical requirement for enterprise trust is avoiding hallucination. If I ask an out-of-domain question—like Lenny's recipe for baking chocolate cake—watch what happens:
>
> Our grounding guardrail detects that the query content terms have zero overlap with the archive. Instead of fabricating a recipe or inventing a fake episode, it politely refuses:
> *'I couldn't find enough support for that in the available Lenny transcript knowledge base.'* Zero fake citations."

---

### [1:25 – 2:05] Screen 5 to 9: Ship 30 for 30 Essay & Sandboxed Artifact Studio
*(Action: Click the 'HTML Strategy One-Pager' prompt, or type 'Create an HTML product strategy one-pager for PMF metrics')*

> "Now let's examine our dedicated agent skills:
>
> First, our **Ship 30 for 30 skill** writes an atomic essay of approximately 1,250 words, structured with the Pain-Promise-Proof-Path hook, 1-3-1 cadence rhythm, and skimmable bold lead-ins.
>
> Next, when we request an **HTML Artifact**, our Artifact Studio slides open on the right. 
> - This isn't just raw code—it renders a complete, responsive HTML/CSS framework inside an `iframe`.
> - For security, the iframe is sandboxed with `allow-scripts`, strictly isolated from the parent application so it cannot access parent cookies, tokens, or the DOM.
> - We can switch between visual Preview and our Live Code Editor, test responsive Desktop, Tablet, and Mobile viewports, or copy and download the file."

---

### [2:05 – 2:35] Screen 10: Model Switching & Technical Trade-Off
*(Action: Open the Model Dropdown in the top right to show Ollama, Cloud, and Mock providers)*

> "Finally, let's talk about an important technical trade-off: **Local vs. Cloud deployment**.
>
> The take-home brief required local model capability. We built a flexible provider abstraction:
> - It connects natively to local **Ollama** running models like `llama3.2`.
> - It integrates cloud providers like OpenAI, Anthropic Claude, and high-speed Groq.
> - And it includes a deterministic offline mock provider as a fallback. If an evaluator tests this on a machine without a local GPU daemon running, the system stays 100% operational without crashing.
>
> All 18 automated backend tests pass, the database persists sessions in SQLite with PostgreSQL readiness, and the frontend builds with zero TypeScript errors.
>
> Thank you, and I look forward to your feedback!"

---

## Fact-Check Summary for Candidate

| Claim in Script | Verified Fact |
| :--- | :--- |
| **"Hundreds of hours"** | Replaced with *"rich, gold-standard frameworks from world-class operators"* |
| **"14 core sources"** | 14 markdown transcripts and fixtures indexed in `data/vector_store/` |
| **"Verified Match %"** | Replaced with *"normalized retrieval relevance score"* |
| **"00:00:00" timestamp** | True — verbatim in `data/fixtures/adam-mosseri.md` at line 11 |
| **"Simulated audio player"**| Replaced with *"timeline marker and playback scrubber"* |
| **"Direct Substack link"** | True — post_url from YAML frontmatter: `https://www.lennysnewsletter.com/p/...` |
| **"100% test pass rate"** | True — all 18 backend tests pass cleanly in pytest |
| **"Sandboxed execution"** | True — `<iframe sandbox="allow-scripts">` without `allow-same-origin` |
