# UI/UX Design System & Experience Specification
# The Lenny Growth Assistant

---

## 1. Design Philosophy: Calm Knowledge-Work Interface

The Lenny Growth Assistant is designed as a focused, premium internal workspace for product leaders and operators.

### Core Principles
1. **Content First, Chrome Second:** Interface elements use muted borders (`border-slate-800`/`border-slate-200`) and soft contrasts so that long-form analytical writing, frameworks, and transcripts are the primary visual focus.
2. **Transparent Provenance:** Every claim derived from Lenny's transcripts features an interactive citation pill. Evaluators and users can inspect quotes and timestamps without context switching.
3. **Artifact Centricity:** Generated documents and interactive frameworks are elevated from inline chat clutter into a dedicated side-by-side Artifact Studio.
4. **Resilient Feedback:** Every network or model state (Ollama health, ingestion progress, streaming generation, error recovery) is visually signaled with clear status badges and helpful recovery tips.

---

## 2. Color Palette & Design Tokens

```
Surface Neutral:
  - Canvas Dark:       #090d16 (Slate 950 deep)
  - Surface Dark:      #0f172a (Slate 900)
  - Surface Card:      #1e293b (Slate 800)
  - Surface Highlight: #334155 (Slate 700)
  - Border Subdued:    #1e293b (Slate 800 / Alpha 60%)

Brand & Accents:
  - Brand Primary:     #6366f1 (Indigo 500)
  - Brand Hover:       #4f46e5 (Indigo 600)
  - Brand Subtle:      #312e81 (Indigo 900 / Alpha 40%)
  - Accent Amber:      #f59e0b (Citation Pills & Insights)
  - Success Green:     #10b981 (Knowledge Base & Ollama Online)
  - Destructive Red:   #ef4444 (Errors & Session Deletion)

Typography:
  - Display & Headings: Inter, system-ui, -apple-system, sans-serif (Font weights: 600, 700)
  - Body & Reading:     Inter, sans-serif (Font weights: 400, 500, line-height: 1.6)
  - Monospace / Code:   JetBrains Mono, Fira Code, monospace
```

---

## 3. Information Architecture & Layout Hierarchy

```
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION SHELL                                    |
+-------------------+-------------------------------------------+-------------------------+
|  SIDEBAR (260px)  |             CHAT FEED (Flex)              |  ARTIFACT STUDIO (500px)|
|                   |                                           |                         |
| [New Chat +]      | Header: Session Title + Model Badge       | Header: Artifact Title  |
|                   | ----------------------------------------- | [Preview] [Code] [Copy] |
| Session List:     | Messages:                                 | ----------------------- |
| - Finding PMF     | [User Bubble]                             | Rendered Output:        |
| - Mosseri AI      |                                           | - Sandboxed iframe      |
| - Growth Loops    | [Assistant Bubble]                        |   (HTML/CSS)            |
|                   |  - Analytical Synthesis                   | - Markdown preview      |
| ----------------- |  - [Citation: Mosseri (00:01:23)]         |                         |
| Knowledge Base:   |                                           |                         |
|  - 14 Transcripts | Composer:                                 |                         |
|  - 660 Chunks     |  [ Ask a growth question...       [Send] ]|                         |
| Model: Ollama/Groq|                                           |                         |
+-------------------+-------------------------------------------+-------------------------+
```

---

## 4. Artifact Studio Ergonomics & Safety

The Artifact Viewer provides a seamless workspace for viewing, editing, and exporting assets:
1. **Tabs:**
   - **Visual Preview:** Interactive live preview. Markdown renders with typography styling; HTML/CSS renders inside a sandboxed `iframe`.
   - **Source Code:** Formatted, syntax-highlighted code editor view with line numbers.
2. **Actions:**
   - **Copy Source:** One-click clipboard copy with toast confirmation.
   - **Download:** Download as `.html` or `.md` file directly to the user's computer.
   - **Close / Collapse:** Allows full-width chat when not inspecting artifacts.

---

## 5. Responsive Behavior & Accessibility

- **Desktop ($\ge 1280px$):** 3-pane layout (Sidebar + Chat + Artifact Studio side-by-side).
- **Tablet ($768px - 1279px$):** Collapsible sidebar drawer + Chat with sliding Artifact drawer.
- **Mobile ($< 768px$):** Single pane with bottom navigation sheet for sessions and full-screen modal for artifacts.
- **Keyboard Navigation:**
  - `Enter`: Send message
  - `Shift + Enter`: Newline in composer
  - `Esc`: Close citation modal or artifact drawer
  - Accessible `aria-labels` and focus rings on all interactive elements.
