# Manual UI Test Plan & Verification Checklist
# The Lenny Growth Assistant

This document provides a step-by-step manual test plan for evaluators and QA engineers to verify the application's user interface, interaction states, and grounding accuracy.

---

## Pre-Test Setup
1. Start backend server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```
2. Start frontend server:
   ```bash
   cd frontend && npm run dev
   ```
3. Open browser to `http://localhost:5173`.

---

## Test Suite Execution Matrix

| Test ID | Feature Area | Step-by-Step Actions | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | **Initial Load & Health** | 1. Open `http://localhost:5173`<br>2. Inspect header, sidebar, and welcome screen | - Application shell loads with dark slate aesthetic.<br>- Sidebar displays "Lenny Assistant AI PRO" with active conversation list.<br>- Knowledge base pill shows green pulsating dot and document count.<br>- Model selector displays active provider. | [Pass] |
| **TC-02** | **Grounded Q&A Flow** | 1. Click prompt card: *"What does Adam Mosseri say about AI being a tailwind for authenticity?"*<br>2. Submit query | - Assistant typing indicator activates.<br>- Response directly synthesizes Adam Mosseri's points on craft, taste, and speed.<br>- Inline citation pills appear with guest name and timestamp marker (e.g., `00:00:00`).<br>- Response renders with rich markdown headers, bullet points, and quotes. | [Pass] |
| **TC-03** | **Citation Inspection & Audio** | 1. Click on any citation pill `[1] Adam Mosseri`<br>2. Inspect modal content<br>3. Click Play on the simulated audio bar<br>4. Click "Copy Quote" | - Citation modal opens with episode title, guest, match percentage, and verbatim excerpt.<br>- Audio bar scrubber animates with timestamp.<br>- Toast confirms quote copied to clipboard.<br>- Substack external link is active. | [Pass] |
| **TC-04** | **Contextual Follow-up** | 1. Type: *"How does Elena Verna's approach to growth loops differ from that?"*<br>2. Press Enter | - Assistant preserves conversation context.<br>- Retrieves Elena Verna's transcript.<br>- Cites Elena Verna with appropriate episode excerpts without losing prior thread context. | [Pass] |
| **TC-05** | **Unsupported Query Guardrail** | 1. Type: *"What is Lenny's recipe for baking chocolate cake?"*<br>2. Press Enter | - System detects query terms are ungrounded in transcript knowledge base.<br>- Assistant responds: *"I couldn't find enough support for that in the available Lenny transcript knowledge base. I don't want to present an unsupported claim as something Lenny or his guests said."*<br>- Zero fake citations are returned. | [Pass] |
| **TC-06** | **Ship 30 for 30 Essay Skill** | 1. Click the "Ship 30 for 30 Essay" quick pill in composer<br>2. Submit query | - Dedicated skill triggers.<br>- Generates approximately 1,250 words formatted with:<br>  - Hook (Pain/Promise/Proof/Path)<br>  - 1-3-1 cadence rhythm<br>  - Benefit-driven numbered headings<br>  - Bullet points with bold lead-ins<br>  - Grounded source references. | [Pass] |
| **TC-07** | **HTML Artifact Studio** | 1. Click "HTML Strategy One-Pager" quick pill<br>2. Submit query | - Side-by-side Artifact Studio (560px) automatically slides open.<br>- Generated HTML renders in sandboxed `iframe`.<br>- User can toggle between Visual Preview and Live Code Editor.<br>- Modifying code in editor updates preview.<br>- "Copy Code" and "Download" buttons work cleanly. | [Pass] |
| **TC-08** | **Responsive Viewport Switcher** | 1. In Artifact Studio preview mode, click Tablet icon (768px), then Mobile icon (375px) | - Preview smoothly transitions between Desktop (100%), Tablet, and Mobile bezel frames with simulated device widths. | [Pass] |
| **TC-09** | **Archive Search Explorer** | 1. In sidebar, click "Transcript Archive"<br>2. Select "Archive Search Explorer" tab<br>3. Search for: *"taste"* or *"retention"* | - Modal lists verified transcript chunks matching the keyword with timestamps and relevance scores.<br>- Clicking "Ask Assistant About This" injects the insight into the chat composer. | [Pass] |
| **TC-10** | **Session Isolation & Export** | 1. Click "+ New Chat"<br>2. Verify message history is empty.<br>3. Switch back to first chat; verify all messages, citations, and artifacts are preserved.<br>4. Click Export button in sidebar. | - Independent context preserved per session.<br>- Formatted `.md` document downloads to user's computer. | [Pass] |
| **TC-11** | **Model Selector & Fallback** | 1. Click Model dropdown in top right.<br>2. Inspect Ollama status and Cloud providers.<br>3. Select Deterministic Mock Provider or Ollama. | - If Ollama is offline, system shows warning badge and automatically uses mock/cloud fallback without application crash. | [Pass] |
