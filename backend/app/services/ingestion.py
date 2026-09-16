"""
Transcript Ingestion and Parsing Services.
Extracts YAML frontmatter, detects speaker turns, and chunks documents semantically.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import yaml


@dataclass
class ParsedTranscript:
    title: str
    guest: Optional[str]
    doc_type: str  # "podcast" or "newsletter"
    post_url: Optional[str]
    word_count: int
    date: Optional[str]
    description: Optional[str]
    raw_content: str
    turns: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TranscriptChunkItem:
    source_title: str
    source_guest: Optional[str]
    source_type: str
    source_url: Optional[str]
    chunk_index: int
    speaker: Optional[str]
    timestamp_str: Optional[str]
    text: str
    word_count: int


class TranscriptParser:
    """Parses markdown files containing YAML frontmatter and speaker dialogues."""

    # Matches: **Speaker Name** (00:12:34): or **Speaker Name** (12:34):
    SPEAKER_TIMESTAMP_PATTERN = re.compile(
        r"^\*\*([^*]+)\*\*\s*\(([\d:]+)\):\s*(.*)$", re.MULTILINE
    )
    # Fallback matches: **Speaker Name**:
    SPEAKER_ONLY_PATTERN = re.compile(r"^\*\*([^*]+)\*\*:\s*(.*)$", re.MULTILINE)

    def parse_file(self, file_path: Path) -> ParsedTranscript:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return self.parse_text(text, filename=file_path.name)

    def parse_text(self, text: str, filename: str = "") -> ParsedTranscript:
        frontmatter = {}
        content = text

        # Extract YAML frontmatter
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                yaml_str = parts[1]
                content = parts[2].strip()
                try:
                    frontmatter = yaml.safe_load(yaml_str) or {}
                except Exception:
                    frontmatter = {}

        # Determine metadata with fallbacks
        title = frontmatter.get("title")
        if not title:
            first_line = content.split("\n")[0].strip("# ").strip()
            title = first_line if first_line else filename.replace(".md", "").replace("-", " ").title()

        guest = frontmatter.get("guest")
        doc_type = frontmatter.get("type", "podcast" if "podcasts" in filename else "newsletter")
        post_url = frontmatter.get("post_url") or frontmatter.get("url")
        date = str(frontmatter.get("date", ""))
        description = frontmatter.get("description", "")
        word_count = int(frontmatter.get("word_count", 0))

        if word_count == 0:
            word_count = len(content.split())

        turns = self._extract_turns(content)

        return ParsedTranscript(
            title=title,
            guest=guest,
            doc_type=doc_type,
            post_url=post_url,
            word_count=word_count,
            date=date,
            description=description,
            raw_content=content,
            turns=turns,
        )

    def _extract_turns(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured turns if dialogue markers exist."""
        turns = []
        lines = content.split("\n")
        current_speaker = None
        current_timestamp = None
        current_buffer = []

        for line in lines:
            line_str = line.strip()
            match_ts = self.SPEAKER_TIMESTAMP_PATTERN.match(line_str)
            match_spk = self.SPEAKER_ONLY_PATTERN.match(line_str) if not match_ts else None

            if match_ts:
                if current_buffer:
                    turns.append({
                        "speaker": current_speaker,
                        "timestamp": current_timestamp,
                        "text": " ".join(current_buffer).strip(),
                    })
                    current_buffer = []
                current_speaker = match_ts.group(1).strip()
                current_timestamp = match_ts.group(2).strip()
                rest = match_ts.group(3).strip()
                if rest:
                    current_buffer.append(rest)
            elif match_spk:
                if current_buffer:
                    turns.append({
                        "speaker": current_speaker,
                        "timestamp": current_timestamp,
                        "text": " ".join(current_buffer).strip(),
                    })
                    current_buffer = []
                current_speaker = match_spk.group(1).strip()
                current_timestamp = None
                rest = match_spk.group(2).strip()
                if rest:
                    current_buffer.append(rest)
            else:
                if line_str:
                    current_buffer.append(line_str)

        if current_buffer:
            turns.append({
                "speaker": current_speaker,
                "timestamp": current_timestamp,
                "text": " ".join(current_buffer).strip(),
            })

        return turns


class TranscriptChunker:
    """Splits transcripts into overlapping semantic chunks with metadata preservation."""

    def __init__(self, chunk_size_words: int = 380, overlap_words: int = 50):
        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words

    def chunk_document(self, doc: ParsedTranscript) -> List[TranscriptChunkItem]:
        chunks: List[TranscriptChunkItem] = []

        # If we have structured turns, build chunks respecting speaker boundaries
        if doc.turns:
            chunks = self._chunk_from_turns(doc)
        else:
            chunks = self._chunk_from_paragraphs(doc)

        return chunks

    def _chunk_from_turns(self, doc: ParsedTranscript) -> List[TranscriptChunkItem]:
        chunks = []
        current_words = []
        current_speaker = None
        current_timestamp = None
        chunk_idx = 0

        for turn in doc.turns:
            speaker = turn["speaker"] or "Unknown"
            ts = turn["timestamp"] or ""
            text = turn["text"]
            formatted_turn = f"**{speaker}**{f' ({ts})' if ts else ''}: {text}"
            words = formatted_turn.split()

            if not current_speaker:
                current_speaker = speaker
                current_timestamp = ts

            if len(current_words) + len(words) > self.chunk_size_words and current_words:
                chunk_text = " ".join(current_words)
                chunks.append(
                    TranscriptChunkItem(
                        source_title=doc.title,
                        source_guest=doc.guest,
                        source_type=doc.doc_type,
                        source_url=doc.post_url,
                        chunk_index=chunk_idx,
                        speaker=current_speaker,
                        timestamp_str=current_timestamp,
                        text=chunk_text,
                        word_count=len(current_words),
                    )
                )
                chunk_idx += 1
                # Retain overlap words
                overlap = current_words[-self.overlap_words:] if len(current_words) > self.overlap_words else []
                current_words = overlap + words
                current_speaker = speaker
                current_timestamp = ts
            else:
                current_words.extend(words)

        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append(
                TranscriptChunkItem(
                    source_title=doc.title,
                    source_guest=doc.guest,
                    source_type=doc.doc_type,
                    source_url=doc.post_url,
                    chunk_index=chunk_idx,
                    speaker=current_speaker,
                    timestamp_str=current_timestamp,
                    text=chunk_text,
                    word_count=len(current_words),
                )
            )

        return chunks

    def _chunk_from_paragraphs(self, doc: ParsedTranscript) -> List[TranscriptChunkItem]:
        chunks = []
        paragraphs = [p.strip() for p in doc.raw_content.split("\n\n") if p.strip()]
        current_words = []
        chunk_idx = 0

        for para in paragraphs:
            words = para.split()
            if len(current_words) + len(words) > self.chunk_size_words and current_words:
                chunk_text = " ".join(current_words)
                chunks.append(
                    TranscriptChunkItem(
                        source_title=doc.title,
                        source_guest=doc.guest,
                        source_type=doc.doc_type,
                        source_url=doc.post_url,
                        chunk_index=chunk_idx,
                        speaker=doc.guest or "Lenny",
                        timestamp_str=None,
                        text=chunk_text,
                        word_count=len(current_words),
                    )
                )
                chunk_idx += 1
                overlap = current_words[-self.overlap_words:] if len(current_words) > self.overlap_words else []
                current_words = overlap + words
            else:
                current_words.extend(words)

        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append(
                TranscriptChunkItem(
                    source_title=doc.title,
                    source_guest=doc.guest,
                    source_type=doc.doc_type,
                    source_url=doc.post_url,
                    chunk_index=chunk_idx,
                    speaker=doc.guest or "Lenny",
                    timestamp_str=None,
                    text=chunk_text,
                    word_count=len(current_words),
                )
            )

        return chunks
