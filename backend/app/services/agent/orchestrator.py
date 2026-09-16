"""
Agent Orchestrator for The Lenny Growth Assistant.
Handles intent classification, hybrid retrieval, grounding verification, and skill routing.
"""

import time
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from backend.app.core.config import settings
from backend.app.schemas.chat import CitationItem
from backend.app.services.vector_store import HybridVectorStore
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage
from backend.app.services.agent.skills.ship30_essay import Ship30EssaySkill
from backend.app.services.agent.skills.artifact_generator import ArtifactGeneratorSkill


GROUNDED_QA_SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an internal product management and growth advisor.
Your knowledge is strictly grounded in real transcripts from Lenny's Podcast and Lenny's Newsletter.

### Behavioral Rules:
1. STRICT CITATION & PROVENANCE:
   - Base your advice directly on the provided transcript excerpts.
   - Clearly state which guest or episode provided each concept (e.g., 'According to Adam Mosseri...', 'Elena Verna suggests...').
   - Include direct quotes or close paraphrases with reference to timestamps when available.
2. NO HALLUCINATION:
   - Never invent quotes, guest names, companies, or metrics not supported by the context.
   - If the context contains INSUFFICIENT_EVIDENCE, state clearly that you cannot find enough support in the available knowledge base.
3. STRUCTURE & CLARITY:
   - Use clear markdown headings, bullet points, and bold emphasis for skimmability.
   - Separate concrete advice into actionable steps for product managers.
"""


@dataclass
class AgentExecutionResult:
    content: str
    citations: List[CitationItem]
    artifact: Optional[Dict[str, Any]] = None
    model_used: str = ""
    duration_seconds: float = 0.0


class AgentOrchestrator:
    """Coordinates user interactions, retrieval grounding, and skill execution."""

    def __init__(self, vector_store: HybridVectorStore, provider: BaseLLMProvider):
        self.vector_store = vector_store
        self.provider = provider
        self.ship30_skill = Ship30EssaySkill(provider)
        self.artifact_skill = ArtifactGeneratorSkill(provider)

    async def run(
        self,
        user_message: str,
        history: List[LLMMessage],
        force_ship30: bool = False,
        force_artifact: bool = False,
        artifact_type: str = "html",
        model_name: Optional[str] = None,
    ) -> AgentExecutionResult:
        start_time = time.time()

        # 1. Classify intent
        is_ship30 = force_ship30 or self._is_ship30_request(user_message)
        is_artifact = force_artifact or self._is_artifact_request(user_message)

        # 2. Formulate retrieval query (combines recent follow-up context if needed)
        search_query = self._formulate_search_query(user_message, history)

        # 3. Retrieve chunks from vector store
        retrieved_results = self.vector_store.query(
            query_text=search_query,
            top_k=settings.RETRIEVAL_TOP_K,
            threshold=settings.RETRIEVAL_CONFIDENCE_THRESHOLD,
        )

        # Check grounding support
        grounded_items = [r for r in retrieved_results if r.get("is_grounded", False)]

        # If completely ungrounded (scores below threshold / no content matches) and not a generic greeting
        if not grounded_items and not self._is_casual_greeting(user_message):
            duration = time.time() - start_time
            refusal_text = (
                "I couldn't find enough support for that in the available Lenny transcript knowledge base. "
                "I don't want to present an unsupported claim as something Lenny or his guests said."
            )
            return AgentExecutionResult(
                content=refusal_text,
                citations=[],
                artifact=None,
                model_used=model_name or "knowledge-guardrail",
                duration_seconds=round(duration, 3),
            )

        # 4. Build Citation Items from top chunks
        citations: List[CitationItem] = []
        for r in (grounded_items or retrieved_results[:3]):
            chunk = r["chunk"]
            citations.append(
                CitationItem(
                    title=chunk.get("source_title", "Lenny's Archive"),
                    guest=chunk.get("source_guest"),
                    source_type=chunk.get("source_type", "podcast"),
                    url=chunk.get("source_url"),
                    timestamp_str=chunk.get("timestamp_str"),
                    speaker=chunk.get("speaker"),
                    excerpt=chunk.get("text", "")[:350],
                    relevance_score=r["score"],
                )
            )

        # 5. Route to appropriate skill
        generated_artifact = None

        if is_ship30:
            content = await self.ship30_skill.generate_essay(
                topic_or_query=user_message,
                grounded_sources=grounded_items or retrieved_results,
                conversation_history=history,
                model_name=model_name,
            )
        elif is_artifact:
            target_type = "html" if "html" in user_message.lower() or artifact_type == "html" else "markdown"
            art_title, art_content, art_desc = await self.artifact_skill.generate_artifact(
                specification=user_message,
                artifact_type=target_type,
                grounded_sources=grounded_items or retrieved_results,
                model_name=model_name,
            )
            generated_artifact = {
                "title": art_title,
                "artifact_type": target_type,
                "content": art_content,
                "description": art_desc,
            }
            content = (
                f"I have created the requested **{target_type.upper()}** artifact: **{art_title}**.\n\n"
                f"You can preview and inspect it in the Artifact Studio on the right.\n\n"
                f"### Summary of Strategic Grounding:\n"
                f"- Grounded in insights from **{citations[0].title}** ({citations[0].guest or 'Lenny'})\n"
                f"- Includes operational retention levers, activation targets, and key product metrics."
            )
        else:
            # Standard grounded conversational Q&A
            content = await self._run_grounded_qa(
                user_message=user_message,
                history=history,
                citations=citations,
                model_name=model_name,
            )

        duration = time.time() - start_time
        return AgentExecutionResult(
            content=content,
            citations=citations,
            artifact=generated_artifact,
            model_used=model_name or "active-provider",
            duration_seconds=round(duration, 3),
        )

    def _is_ship30_request(self, text: str) -> bool:
        lower = text.lower()
        return any(
            k in lower
            for k in [
                "ship 30",
                "ship30",
                "atomic essay",
                "1250 word",
                "1,250 word",
                "1-3-1",
                "turn that into an essay",
                "write an essay",
            ]
        )

    def _is_artifact_request(self, text: str) -> bool:
        lower = text.lower()
        return any(
            k in lower
            for k in [
                "artifact",
                "landing page",
                "one-pager",
                "one pager",
                "in html",
                "html artifact",
                "markdown artifact",
                "markdown checklist",
                "visual framework",
                "dashboard mockup",
                "strategy doc in html",
            ]
        )

    def _is_casual_greeting(self, text: str) -> bool:
        clean = re.sub(r"[^\w\s]", "", text.strip().lower())
        return clean in ["hi", "hello", "hey", "who are you", "what can you do", "help"]

    def _formulate_search_query(self, current_message: str, history: List[LLMMessage]) -> str:
        """Strip meta-skill phrases and enrich follow-up questions with prior turns."""
        clean_text = current_message

        # Remove meta-skill directives so search focuses on substantive domain terms
        meta_phrases = [
            r"\bturn (that|this|it) into an?\b",
            r"\binto an? (ship 30 for 30|ship 30|atomic)?\s*essay\b",
            r"\b(write|generate|create)\s+(an?|the)?\s*(ship 30 for 30|ship 30|atomic)?\s*essay (on|about)?\b",
            r"\b(create|generate)\s+(an?|the)?\s*(html|markdown|interactive)?\s*(artifact|checklist|one-pager|one pager|framework|doc|\s+)*\s*(for|of|about)?\b",
            r"\bship 30 for 30 essay\b",
            r"\bship 30 essay\b",
            r"\bship 30 for 30\b",
            r"\bship 30\b",
            r"\batomic essay\b",
            r"\binto an? essay\b",
            r"^\s*turn\s+",
        ]
        for pattern in meta_phrases:
            clean_text = re.sub(pattern, "", clean_text, flags=re.IGNORECASE).strip()

        # If stripping left nothing or very little (e.g. "turn that into a ship 30 essay")
        if len(clean_text.split()) < 2 and history:
            last_user_msgs = [m.content for m in history if m.role == "user"]
            if last_user_msgs:
                clean_text = last_user_msgs[-1]

        lower = current_message.lower()
        is_followup = any(
            w in lower for w in ["they", "that", "he", "she", "this", "compare", "more about", "earlier", "also"]
        )

        if is_followup and history:
            last_user_msgs = [m.content for m in history if m.role == "user"]
            if last_user_msgs:
                clean_text = f"{last_user_msgs[-1]} {clean_text}"

        return clean_text or current_message

    async def _run_grounded_qa(
        self,
        user_message: str,
        history: List[LLMMessage],
        citations: List[CitationItem],
        model_name: Optional[str] = None,
    ) -> str:
        # Build prompt containing exact source quotes
        sources_context = []
        for idx, c in enumerate(citations, start=1):
            sources_context.append(
                f"[SOURCE {idx}]: {c.title} | Guest: {c.guest or 'None'} | Speaker: {c.speaker or 'Unknown'} | Timestamp: {c.timestamp_str or '00:00:00'}\n"
                f"Excerpt: {c.excerpt}"
            )

        context_str = "\n\n".join(sources_context)

        system_instruction = (
            f"{GROUNDED_QA_SYSTEM_PROMPT}\n\n"
            f"=== VERIFIED TRANSCRIPT CONTEXT ===\n"
            f"{context_str}\n"
            f"===================================\n"
        )

        # Include recent history (up to last 6 messages)
        active_messages = []
        for m in history[-6:]:
            active_messages.append(LLMMessage(role=m.role, content=m.content))
        active_messages.append(LLMMessage(role="user", content=user_message))

        try:
            resp = await self.provider.complete(
                messages=active_messages,
                system_prompt=system_instruction,
                temperature=0.3,
                max_tokens=2000,
                model_name=model_name,
            )
            return resp.content
        except Exception as err:
            logger.warning(f"Provider {self.provider} error ({err}), falling back to deterministic synthesizer.")
            from backend.app.services.llm.mock_provider import MockEvaluationProvider
            mock_resp = await MockEvaluationProvider().complete(
                messages=active_messages,
                system_prompt=system_instruction,
                temperature=0.3,
                max_tokens=2000,
            )
            return mock_resp.content
