"""
Deterministic High-Fidelity Mock & Evaluation Provider.
Provides deterministic, high-quality grounded completions, Ship 30 essays, and artifacts
directly utilizing the grounded context. Ideal for automated testing and offline demos.
"""

import re
from typing import List, Optional
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, ProviderStatus


class MockEvaluationProvider(BaseLLMProvider):
    """Deterministic offline provider grounded in transcript context."""

    def __init__(self, model_name: str = "mock-grounded-pm"):
        self.model_name = model_name

    async def check_health(self) -> ProviderStatus:
        return ProviderStatus(
            is_available=True,
            provider="mock",
            message="Deterministic Offline Provider ready (no external dependencies required).",
            models=["mock-grounded-pm", "mock-evaluator"],
        )

    async def complete(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2500,
        model_name: Optional[str] = None,
    ) -> LLMResponse:
        user_msg = messages[-1].content if messages else ""
        sys_prompt = system_prompt or ""

        # 1. Check if the prompt explicitly marks insufficient evidence
        if "=== STATUS: INSUFFICIENT_EVIDENCE ===" in sys_prompt:
            content = (
                "I couldn't find enough support for that in the available Lenny transcript knowledge base. "
                "I don't want to present an unsupported claim as something Lenny or his guests said."
            )
            return LLMResponse(content=content, model_name=self.model_name, provider="mock", total_tokens=45)

        # 2. Check if Ship 30 for 30 essay is requested
        if "Ship 30" in user_msg or "ship 30" in user_msg.lower() or "atomic essay" in user_msg.lower():
            content = self._generate_mock_ship30_essay(user_msg, sys_prompt)
            return LLMResponse(content=content, model_name=self.model_name, provider="mock", total_tokens=1250)

        # 3. Check if Artifact is requested
        if any(w in user_msg.lower() for w in ["artifact", "html", "landing page", "one-pager", "framework"]):
            content = self._generate_mock_artifact(user_msg, sys_prompt)
            return LLMResponse(content=content, model_name=self.model_name, provider="mock", total_tokens=850)

        # 4. Standard Grounded Response
        content = self._generate_mock_grounded_answer(user_msg, sys_prompt)
        return LLMResponse(content=content, model_name=self.model_name, provider="mock", total_tokens=350)

    def _extract_sources_from_prompt(self, sys_prompt: str) -> List[dict]:
        """Parse source annotations passed into the system prompt."""
        sources = []
        matches = re.findall(r"\[SOURCE (\d+)\]:\s*(.*?)\s*\|\s*Guest:\s*(.*?)\s*\|\s*Speaker:\s*(.*?)\s*\|\s*Timestamp:\s*(.*?)\s*\nExcerpt:\s*(.*?)(?=\n\[SOURCE|\n===|\Z)", sys_prompt, re.DOTALL)
        for m in matches:
            sources.append({
                "index": m[0],
                "title": m[1].strip(),
                "guest": m[2].strip(),
                "speaker": m[3].strip(),
                "timestamp": m[4].strip(),
                "excerpt": m[5].strip(),
            })
        return sources

    def _generate_mock_grounded_answer(self, user_msg: str, sys_prompt: str) -> str:
        sources = self._extract_sources_from_prompt(sys_prompt)
        if not sources:
            return (
                "Based on the transcript knowledge base, Lenny and his guests frequently discuss this topic. "
                "However, no direct verbatim match met the confidence threshold for this specific question."
            )

        top = sources[0]
        guest = top["guest"] if top["guest"] and top["guest"] != "None" else top["speaker"]
        title = top["title"]
        timestamp = top["timestamp"]
        excerpt = top["excerpt"][:280]

        return (
            f"Based on **{title}** with **{guest}**:\n\n"
            f"{guest} emphasizes that when approaching this challenge, traditional playbooks often fail because teams prioritize speed over deliberate craft and validation.\n\n"
            f"Specifically, {guest} points out:\n"
            f"> \"{excerpt}...\"\n\n"
            f"### Key Takeaways from the Conversation:\n"
            f"1. **Focus on High-Leverage Craft:** In an era where building software has become commoditized, differentiation comes from taste, deep user empathy, and authentic execution.\n"
            f"2. **Validate Before Scaling:** Don't scale distribution until your core retention loop and qualitative signals confirm genuine customer delight.\n"
            f"3. **Clear Ownership:** Keep decision rights sharp across product, engineering, and design to avoid consensus-driven mediocrity.\n\n"
            f"*Source: [{title}] ({f'Guest: {guest}, ' if guest else ''}Timestamp: {timestamp})*"
        )

    def _generate_mock_ship30_essay(self, user_msg: str, sys_prompt: str) -> str:
        sources = self._extract_sources_from_prompt(sys_prompt)
        lead_guest = sources[0]["guest"] if sources and sources[0]["guest"] != "None" else "Top Product Leaders"
        title_ref = sources[0]["title"] if sources else "Lenny's Podcast Archive"
        top_excerpt = sources[0]["excerpt"][:300] if sources else "Taste matters a ton in product craft."

        sections = [
            f"# The Counterintuitive Blueprint for Modern Product Growth: What {lead_guest} Taught Me",
            "",
            "Most product teams build features backward.",
            "They optimize for delivery speed instead of strategic conviction. They confuse shipping software output with delivering measurable customer outcome. And then they wonder why cohort retention flatlines after month three.",
            f"Here is the counterintuitive operating blueprint shared on Lenny's Podcast by {lead_guest} that changes everything.",
            "",
            "---",
            "",
            "## The Hook: Why Conventional Product Management Is Broken",
            "",
            "Product management has entered a crisis of consensus.",
            "For the past decade, teams were taught that following the standard agile playbook—two-week sprints, backlog grooming, velocity tracking, and A/B testing minor button colors—would reliably produce generational products.",
            "It doesn't.",
            "",
            f"As {lead_guest} pointed out in **{title_ref}**:",
            f"> \"{top_excerpt}...\"",
            "",
            "When software creation becomes cheaper and faster thanks to modern AI tooling, raw engineering throughput ceases to be a competitive moat.",
            "The real bottleneck shifts from *how fast you can build* to *whether you have the taste and judgment to know what is worth building in the first place*.",
            "",
            "---",
            "",
            "## 1. The Death Spiral of Consensus-Driven Roadmaps",
            "",
            "When everyone has an equal say, nobody has an authentic vision.",
            "In conventional technology companies, product roadmaps are negotiated peace treaties between competing internal departments. Sales demands bespoke enterprise integration hooks, customer success demands bug fixes for vocal minority accounts, design demands pixel-perfect consistency, and executives demand arbitrary quarterly milestone delivery.",
            "The tragic result is an average product that satisfies everyone internally but delights nobody in the real world.",
            "",
            "High-performing product teams avoid this trap by adopting **single-threaded ownership**.",
            "A single-threaded owner is an individual with deep domain context, exceptional taste, and direct customer proximity who holds ultimate decision rights.",
            "",
            "* **The Consensus Warning Sign:** Every roadmap item is an incremental compromise that avoids offending anyone.",
            "* **The Velocity Illusion:** The engineering team hits 100% of their sprint points, yet user activation and net retention fail to inflect upward.",
            "* **The Post-Mortem Trap:** Post-mortems obsess over why delivery dates were missed rather than examining whether the shipped feature actually solved the underlying human problem.",
            "",
            "Break the death spiral by giving one operator complete agency and holding them accountable for customer delight rather than delivery compliance.",
            "",
            "---",
            "",
            "## 2. The 3-Pillar Framework for True Product-Market Conviction",
            "",
            "Finding product conviction is not an algebraic formula.",
            "It is the systematic elimination of existential market risk through rapid, deliberate qualitative discovery.",
            "Across hundreds of conversations on Lenny's Podcast, the most successful founders and product leaders converge on three foundational pillars:",
            "",
            "### Pillar I: Qualitative Intimacy Before Premature Quantitative Optimization",
            "Metrics tell you what is happening; only intimate human conversation tells you why.",
            "Before writing a single line of production code or commissioning high-fidelity Figma mockups, spend hours watching real users struggle through their existing workflows.",
            "Pay close attention to what users do when they think nobody is watching. Listen for the visceral sighs of frustration, the spreadsheets they maintain on the side, and the makeshift workarounds they invent.",
            "If your product does not eliminate an existing, painful habit, users will not endure the cognitive switching cost required to adopt your new solution.",
            "",
            "### Pillar II: The 10x Single-Feature Value Wedge",
            "Iconic products never win by doing twenty things marginally better.",
            "They win by doing exactly one critical, emotionally resonant action ten times better than the status quo.",
            "Think of Slack: it wasn't just another IRC client; it eliminated asynchronous team communication silos through instantaneous search, channels, and rich link previews.",
            "Think of Figma: it didn't just replicate Sketch; it moved design into the multiplayer browser canvas, turning solitary work into a real-time collaborative whiteboarding session.",
            "Identify your singular value wedge. Double down on that core interaction until it feels magical, and ruthlessly cut peripheral feature distractions.",
            "",
            "### Pillar III: Organic Retention as the Only Authentic North Star",
            "User acquisition is vanity; retention is sanity; monetization is reality.",
            "If your week-8 retention cohort curves do not flatten into an asymptotic horizontal line, every marketing dollar and sales commission you spend is like pouring water into a leaky bucket.",
            "The top quartile of software products retain at least 40% of their activated users across months 3, 6, and 12.",
            "Until your retention curve flattens organically, halt paid marketing acquisition and focus all product energy on fixing onboarding drop-offs and clarifying your core value proposition.",
            "",
            "---",
            "",
            "## 3. The 1/3/1 Operating Rhythm for High-Velocity Execution",
            "",
            "How do you instill this philosophy into a product squad without introducing paralyzing bureaucratic overhead?",
            "You implement a strict 1/3/1 weekly operating rhythm:",
            "",
            "* **1 Primary Metric Objective (Monday Morning):** On Monday, the entire squad aligns on the single quantitative metric needle that must move by Friday afternoon (e.g., 'reduce onboarding friction from 4 minutes to 90 seconds').",
            "* **3 Daily Micro-Experiments (Tuesday through Thursday):** Empower product managers, designers, and engineers to ship three small, unblocked qualitative tests or customer feedback loops each day without requiring management sign-off.",
            "* **1 Friday Synthesis Session (Friday Afternoon):** Gather the team for 45 minutes. Ruthlessly review experiment results, kill ideas that produced mediocre signals, celebrate customer breakthroughs, and document key learnings.",
            "",
            "True organizational velocity is not about typing code faster. Velocity is about reducing the time it takes to discard invalidated hypotheses.",
            "",
            "---",
            "",
            "## 4. The Three Deadly Traps That Kill Scaling Products",
            "",
            "Even experienced growth leaders frequently fall into these three fatal traps:",
            "",
            "1. **The 'One More Feature' Fallacy:** Believing that your struggling activation rate will magically be rescued by shipping another integration, another export button, or an analytics dashboard. In reality, struggling conversion is almost always a positioning and clarity problem, not a feature shortage.",
            "2. **Outsourcing Customer Empathy:** Delegating user research to external agencies or separate market research departments. When product engineers and designers do not speak directly with paying customers, they lose the intuitive empathy required to craft great user experiences.",
            "3. **Confusing Activity with Impact:** Celebrating pull requests merged and tickets closed instead of customer problems solved. Your users do not care how many story points your engineering sprint burned; they only care whether their workflow got easier.",
            "",
            "---",
            "",
            "## 5. Tactical Implementation: What to Ship Tomorrow Morning",
            "",
            "You do not need approval from an executive steering committee to start building with taste and conviction.",
            "Begin tomorrow morning with these three concrete, actionable steps:",
            "",
            "1. **Audit Your Current Sprint Backlog:** Review every user story scheduled for the current sprint. Ruthlessly remove or defer the bottom 30% of tickets that do not directly contribute to user activation or cohort retention.",
            "2. **Conduct Three 20-Minute Unguided User Observation Sessions:** Reach out to three recent signups who dropped off during onboarding. Ask them to share their screen and walk through their setup while thinking aloud. Do not defend the UI; simply observe where they hesitate.",
            "3. **Rewrite Your Value Proposition in the Customer's Exact Words:** Strip away corporate jargon like 'synergistic productivity enhancement.' Replace it with the exact emotional phrases your most passionate users used during customer interviews.",
            "",
            "Exceptional software is never the output of an indifferent consensus. It is the result of dedicated product builders who possess clear taste, deep empathy, and the courage to build with conviction.",
            "",
            f"*(Grounded in insights from Lenny's Podcast archive: {title_ref}, featuring {lead_guest})*"
        ]
        return "\n".join(sections)

    def _generate_mock_artifact(self, user_msg: str, sys_prompt: str) -> str:
        sources = self._extract_sources_from_prompt(sys_prompt)
        guest = sources[0]["guest"] if sources and sources[0]["guest"] != "None" else "Lenny's Podcast"
        title = sources[0]["title"] if sources else "Growth Strategy"

        if "markdown" in user_msg.lower():
            return f"""# Executive Product Strategy One-Pager
**Framework:** Growth & Retention Architecture
**Source Grounding:** {title} ({guest})

## 1. Executive Summary
Modern product development requires tight coupling between user empathy and viral loops. This strategy doc outlines the core operational loop for Q3.

| Component | Objective | Key Metric | Target |
| :--- | :--- | :--- | :--- |
| **Activation** | Time to First Value (TTFV) | < 3 minutes | 85% of signups |
| **Retention** | Day-30 Habitual Usage | WAU / MAU | > 42% |
| **Expansion** | Team Invites & Virality | K-factor | > 0.45 |

## 2. Strategic Pillars
1. **Zero-Friction Onboarding:** Cut 4 onboarding form steps into a single magic link.
2. **Contextual Collaboration:** Bring multiplayer commenting to the core canvas.
3. **Automated Insights:** Deliver weekly value digest emails summarizing team productivity.
"""

        # HTML/CSS Artifact
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product Strategy Framework</title>
  <style>
    :root {{
      --primary: #4f46e5;
      --surface: #0f172a;
      --card: #1e293b;
      --text: #f8fafc;
      --subtext: #94a3b8;
      --accent: #10b981;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--surface); color: var(--text); padding: 32px; }}
    .header {{ border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 28px; }}
    .badge {{ display: inline-block; background: rgba(79, 70, 229, 0.2); color: #818cf8; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
    h1 {{ font-size: 24px; margin: 12px 0 6px; font-weight: 700; }}
    p.subtitle {{ color: var(--subtext); font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 24px; }}
    .card {{ background: var(--card); border: 1px solid #334155; border-radius: 12px; padding: 24px; transition: transform 0.2s, border-color 0.2s; }}
    .card:hover {{ transform: translateY(-2px); border-color: var(--primary); }}
    .card-title {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }}
    .metric {{ font-size: 28px; font-weight: 700; color: var(--accent); margin: 12px 0 4px; }}
    .metric-label {{ font-size: 12px; color: var(--subtext); text-transform: uppercase; }}
    .list {{ margin-top: 16px; font-size: 14px; color: #cbd5e1; line-height: 1.6; list-style-position: inside; }}
    .footer {{ margin-top: 36px; padding-top: 20px; border-top: 1px solid #334155; font-size: 12px; color: var(--subtext); display: flex; justify-content: space-between; }}
  </style>
</head>
<body>
  <div class="header">
    <span class="badge">Lenny Framework • {guest}</span>
    <h1>Growth & Retention Engine Architecture</h1>
    <p class="subtitle">Actionable product loop grounded in insights from {title}</p>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-title">Pillar 1: Discovery & Taste</div>
      <div class="metric">85%</div>
      <div class="metric-label">Conviction Confidence Score</div>
      <ul class="list">
        <li>Direct user interviews prior to coding</li>
        <li>Elimination of consensus-driven compromise</li>
        <li>Single-threaded product ownership</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">Pillar 2: Retention Loop</div>
      <div class="metric">48%</div>
      <div class="metric-label">Target Day-30 Sticky Ratio</div>
      <ul class="list">
        <li>Sub-3-minute time-to-first-value</li>
        <li>Core unscalable magic moment</li>
        <li>Daily engagement triggers</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">Pillar 3: Expansion & Virality</div>
      <div class="metric">0.65</div>
      <div class="metric-label">Organic K-Factor</div>
      <ul class="list">
        <li>In-product collaborative multiplayer hooks</li>
        <li>Public artifact sharing loops</li>
        <li>Word-of-mouth advocacy</li>
      </ul>
    </div>
  </div>

  <div class="footer">
    <span>The Lenny Growth Assistant</span>
    <span>Source Grounding: {title}</span>
  </div>
</body>
</html>"""
