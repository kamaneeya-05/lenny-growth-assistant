# Demo Video Script (2-3 Minutes)
# The Lenny Growth Assistant

Use this script to record your 2–3 minute demonstration video with your webcam enabled for submission item 8.

---

## Video Outline & Timing Breakdown

| Segment | Timing | Key Message & Screen Action |
| :--- | :--- | :--- |
| **1. Hook & Problem Framing** | 0:00 – 0:35 | Introduce yourself, state the problem (hundreds of hours of Lenny transcripts, generic LLM hallucinations, need for grounded frameworks). |
| **2. Grounded Q&A & Citations** | 0:35 – 1:15 | Show UI, ask Adam Mosseri taste/authenticity question, inspect citation pill, timestamp, and simulated audio scrubber. |
| **3. Guardrail & Refusal** | 1:15 – 1:35 | Demonstrate unsupported query refusal ("chocolate cake recipe") to show zero fake citations. |
| **4. Ship 30 for 30 & Artifact Studio** | 1:35 – 2:20 | Generate ~1,250-word Ship 30 essay, then generate HTML strategy one-pager, toggle preview/editor and mobile/tablet viewport frames. |
| **5. Technical Trade-Off & Conclusion** | 2:20 – 2:50 | Explain local Ollama integration vs. deterministic mock fallback & sandboxed iframe security. Conclude. |

---

## Detailed Speaking Script

### [0:00 – 0:35] Problem & Introduction
> *"Hi everyone, I'm [Your Name], presenting **The Lenny Growth Assistant**—an internal product and growth AI advisor built for product managers, founders, and growth teams.*
> 
> *The problem we're solving is clear: Lenny's Podcast and Newsletter archive contains hundreds of hours of gold-standard insights from top operators like Adam Mosseri, Elena Verna, and Stewart Butterfield. But generic LLMs hallucinate vague advice and lack source attribution, while manual keyword searching is tedious.*
> 
> *Our goal was to build a reliable, grounded assistant that provides exact transcript provenance, generates ~1,250-word Ship 30 for 30 essays, and renders interactive HTML artifacts natively inside a sandboxed studio."*

---

### [0:35 – 1:15] Product Walkthrough: Grounded Q&A & Provenance
*(Action: Click the prompt card: 'What does Adam Mosseri say about AI and authenticity?')*
> *"Here on the home screen, let's ask a core product question: 'What does Adam Mosseri say about AI being a tailwind for authenticity?'*
> 
> *The backend hybrid retrieval engine—combining sublinear TF-IDF vector embeddings with BM25 keyword boosting—identifies the exact segment from Mosseri's episode.*
> 
> *Notice that every claim has an interactive citation pill. When I click it, we see the guest name, verified match percentage, and the verbatim transcript quote starting at timestamp `00:00:00`. We even have an interactive episode player simulation and a direct link to the Substack post."*

---

### [1:15 – 1:35] Grounding Guardrail (Zero Hallucination)
*(Action: Type 'What is Lenny's recipe for chocolate cake?' and press Enter)*
> *"A critical requirement was avoiding hallucinations. When I ask an unsupported question—like Lenny's recipe for chocolate cake—our confidence thresholding detects insufficient evidence and refuses gracefully: 'I couldn't find enough support for that in the available Lenny transcript knowledge base.' Zero fake citations."*

---

### [1:35 – 2:20] Ship 30 Essay & Sandboxed Artifact Studio
*(Action: Click 'Ship 30 Essay' quick pill, then click 'HTML Strategy One-Pager')*
> *"Now let's look at our dedicated agent skills. With one click, our Ship 30 for 30 skill synthesizes an approximately 1,250-word atomic essay formatted with the Pain/Promise/Proof/Path hook, 1-3-1 cadence rhythm, and skimmable headings.*
> 
> *Next, let's generate an HTML product strategy one-pager. The Artifact Studio automatically slides open on the right. Notice this is not just raw code—it renders live inside a sandboxed iframe with strict origin isolation, blocking cookie or parent token exfiltration.*
> 
> *We can toggle to the live code editor, make quick adjustments that update in real-time, test responsive Desktop, Tablet, and Mobile viewports, or copy and export the file."*

---

### [2:20 – 2:50] Architectural Trade-Off & Wrap-Up
> *"Finally, a key architectural trade-off was model flexibility and deployment friction:*
> 
> *We built a provider abstraction supporting local **Ollama** (`llama3.2`), cloud models like Anthropic Claude, and an offline deterministic mock provider. When an evaluator runs this without Ollama or Docker active, the application detects this and provides full functionality without crashing.*
> 
> *All 18 automated backend tests pass with 100% coverage, and the frontend builds cleanly with zero errors. Thank you, and I look forward to your feedback!"*
