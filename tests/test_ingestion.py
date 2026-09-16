"""
Transcript Parsing and Chunking Tests.
"""

from pathlib import Path
import pytest
from backend.app.services.ingestion import TranscriptParser, TranscriptChunker


SAMPLE_TRANSCRIPT_MD = """---
title: "Sample Episode: Taste and PM Conviction"
date: "2026-05-12"
type: "podcast"
guest: "Jane Doe"
post_url: "https://www.lennysnewsletter.com/p/sample-episode"
description: "A masterclass in product taste and building generational products."
word_count: 520
---

**Lenny** (00:00:00):
Welcome to Lenny's Podcast. Today we are joined by Jane Doe, who led product at top hypergrowth companies.

**Jane Doe** (00:00:15):
Thanks for having me Lenny! I think taste is the single most misunderstood concept in product management today. People assume taste is an innate artistic gift, but in reality, taste is the accumulated residue of thousands of deliberate customer observations and uncompromised standards.

**Lenny** (00:01:10):
How does a new founder or product manager train their taste if they don't have ten years of experience?

**Jane Doe** (00:01:25):
You begin by studying the masterworks in your domain. Don't look at mediocre competitors. Look at Superhuman, Stripe, and Figma. Tear down their micro-interactions and examine every edge case.
"""


def test_transcript_parser():
    parser = TranscriptParser()
    doc = parser.parse_text(SAMPLE_TRANSCRIPT_MD, filename="sample-episode.md")

    assert doc.title == "Sample Episode: Taste and PM Conviction"
    assert doc.guest == "Jane Doe"
    assert doc.doc_type == "podcast"
    assert doc.post_url == "https://www.lennysnewsletter.com/p/sample-episode"
    assert len(doc.turns) >= 4
    assert doc.turns[1]["speaker"] == "Jane Doe"
    assert doc.turns[1]["timestamp"] == "00:00:15"
    assert "taste is the accumulated residue" in doc.turns[1]["text"]


def test_transcript_chunker():
    parser = TranscriptParser()
    doc = parser.parse_text(SAMPLE_TRANSCRIPT_MD, filename="sample-episode.md")

    chunker = TranscriptChunker(chunk_size_words=50, overlap_words=10)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    for c in chunks:
        assert c.source_title == "Sample Episode: Taste and PM Conviction"
        assert c.source_guest == "Jane Doe"
        assert c.source_url is not None
        assert len(c.text.split()) > 0
