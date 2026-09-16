"""
Ship 30 for 30 Essay Generation Skill.
Produces ~1,250-word atomic essays featuring high rate-of-revelation, 1-3-1 cadence rhythm,
skimmable headings, bullet points, and rigorous transcript grounding.
"""

from typing import List, Dict, Any, Optional
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage


SHIP30_SYSTEM_PROMPT = """You are an elite Ship 30 for 30 writing assistant and product growth strategist.
Your mission is to transform transcript insights from Lenny's Podcast and Newsletter into an approximately 1,250-word Ship 30 for 30–style essay.

### Core Guidelines:
1. TARGET LENGTH: Approximately 1,250 words. Thorough, dense with value, and highly skimmable.
2. THE HOOK: Open with an irresistible 4-part hook:
   - The Pain: A sharp, relatable problem PMs/founders face.
   - The Promise: What the reader will master by the end.
   - The Proof: Grounded evidence and credentials from Lenny's transcript sources.
   - The Path: The structured journey this essay will take.
3. 1/3/1 CADENCE & RHYTHM:
   - 1 punchy sentence to open each point.
   - 3 rhythmic sentences (or a bullet list) explaining the core insight.
   - 1 strong takeaway or transition to close.
4. SKIMMABLE HEADINGS:
   - Use numbered, benefit-driven subheadings (e.g., '## 1. The Death Spiral of Consensus-Driven Roadmaps').
5. SELECTIVE BOLD EMPHASIS:
   - Bold the first 2-4 words of key sentences and bullet items to maximize visual scanning.
6. SOURCE FIDELITY:
   - Ground every major assertion in the provided transcript excerpts.
   - Name the guest and episode explicitly.
   - Never invent quotes or claims not present in the sources.
7. CONCLUSION:
   - End with an actionable 3-step 'Ship This Tomorrow' tactical checklist.
"""


class Ship30EssaySkill:
    """Specialized skill generating 1,250-word Ship 30 for 30 essays."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate_essay(
        self,
        topic_or_query: str,
        grounded_sources: List[Dict[str, Any]],
        conversation_history: Optional[List[LLMMessage]] = None,
        model_name: Optional[str] = None,
    ) -> str:
        # Build source context block
        source_texts = []
        for idx, item in enumerate(grounded_sources, start=1):
            c = item.get("chunk", {})
            title = c.get("source_title", "Unknown Title")
            guest = c.get("source_guest", "Expert Guest")
            speaker = c.get("speaker", guest)
            ts = c.get("timestamp_str", "00:00:00")
            excerpt = c.get("text", "")[:400]
            source_texts.append(
                f"[SOURCE {idx}]: {title} | Guest: {guest} | Speaker: {speaker} | Timestamp: {ts}\nExcerpt: {excerpt}"
            )

        context_str = "\n\n".join(source_texts)

        user_prompt = (
            f"Topic / Prompt: {topic_or_query}\n\n"
            f"Available Grounded Sources from Lenny's Archive:\n"
            f"=================================================\n"
            f"{context_str}\n"
            f"=================================================\n\n"
            f"Write a complete, approximately 1,250-word Ship 30 for 30 essay following all formatting and grounding requirements."
        )

        messages = [LLMMessage(role="user", content=user_prompt)]
        resp = await self.provider.complete(
            messages=messages,
            system_prompt=SHIP30_SYSTEM_PROMPT,
            temperature=0.4,
            max_tokens=2800,
            model_name=model_name,
        )
        return resp.content
