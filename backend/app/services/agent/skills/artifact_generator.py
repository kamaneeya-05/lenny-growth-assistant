"""
Artifact Generation Skill.
Generates complete, self-contained Markdown and HTML/CSS artifacts based on grounded knowledge.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage


ARTIFACT_SYSTEM_PROMPT = """You are a Principal Product Architect and Designer for The Lenny Growth Assistant.
Your task is to generate complete, high-quality, professional artifacts based on user requests and grounded transcript knowledge.

### Output Guidelines:
1. SUPPORTED TYPES:
   - "html": A complete, standalone, single-file HTML document with embedded CSS (`<style>`). It MUST be modern, responsive, styled with clean fonts (-apple-system, Roboto), dark slate palette (#0f172a, #1e293b, #334155), vibrant accents (#6366f1, #10b981), clean borders, and clear typographic hierarchy. Do NOT reference external CDN scripts.
   - "markdown": A structured, executive-ready Markdown document with tables, headers, and bulleted takeaways.
2. COMPLETENESS: Never use placeholders like '<!-- add more here -->'. Deliver the complete, working content.
3. GROUNDING: Attribute frameworks and strategies to the real guests and episodes mentioned in the sources.
4. ENCLOSURE: Enclose the artifact content inside a standard code block:
   ```html
   ...
   ```
   or
   ```markdown
   ...
   ```
"""


class ArtifactGeneratorSkill:
    """Specialized skill generating self-contained renderable artifacts."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate_artifact(
        self,
        specification: str,
        artifact_type: str,  # "html" or "markdown"
        grounded_sources: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """
        Generates an artifact.
        Returns: (title, content, description)
        """
        source_texts = []
        for idx, item in enumerate(grounded_sources, start=1):
            c = item.get("chunk", {})
            title = c.get("source_title", "Unknown Title")
            guest = c.get("source_guest", "Expert")
            excerpt = c.get("text", "")[:350]
            source_texts.append(f"[SOURCE {idx}]: {title} ({guest})\nExcerpt: {excerpt}")

        context_str = "\n\n".join(source_texts)

        prompt = (
            f"Artifact Request: {specification}\n"
            f"Target Type: {artifact_type.upper()}\n\n"
            f"Grounded Context from Lenny's Transcripts:\n"
            f"{context_str}\n\n"
            f"Generate the complete artifact inside a ```{artifact_type} ... ``` block."
        )

        resp = await self.provider.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt=ARTIFACT_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=2500,
            model_name=model_name,
        )

        raw_content = resp.content
        extracted_content = self._extract_code_block(raw_content, artifact_type)

        # Derive title
        title = self._derive_title(specification, raw_content)
        description = f"Generated {artifact_type.upper()} artifact based on Lenny's transcript archive"

        return title, extracted_content, description

    def _extract_code_block(self, text: str, target_lang: str) -> str:
        """Extract content from ```html or ```markdown blocks."""
        pattern = rf"```{target_lang}\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback to any code block
        generic_match = re.search(r"```\w*\s*(.*?)\s*```", text, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()

        return text.strip()

    def _derive_title(self, prompt: str, content: str) -> str:
        # Check if content has an <h1> or # Title
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()

        md_h1 = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if md_h1:
            return md_h1.group(1).strip()

        # Fallback to prompt snippet
        words = prompt.split()[:6]
        return " ".join(words).title() or "Product Artifact"
