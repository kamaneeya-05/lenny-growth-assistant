#!/usr/bin/env python3
"""
Transcript Ingestion Pipeline for The Lenny Growth Assistant.

Downloads and parses transcripts from the official Lenny's Podcast and Newsletter
free starter pack (https://github.com/LennysNewsletter/lennys-newsletterpodcastdata),
chunks them into semantic segments preserving speaker markers, timestamps, and URLs,
and builds a persistent hybrid vector & keyword index for fast, zero-hallucination retrieval.
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.ingestion import TranscriptParser, TranscriptChunker
from backend.app.services.vector_store import HybridVectorStore

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/LennysNewsletter/lennys-newsletterpodcastdata/main"
GITHUB_API_BASE = "https://api.github.com/repos/LennysNewsletter/lennys-newsletterpodcastdata/contents"

# Core curated episodes to guarantee high-density product management and growth topics
CORE_EPISODES = [
    "adam-mosseri.md",
    "elena-verna-40.md",
    "marc-andreessen.md",
    "stewart-butterfield.md",
    "eric-ries-2.md",
    "keith-rabois.md",
    "claire-vo-openclaw.md",
    "molly-graham.md",
    "simon-willison.md",
    "tony-fadell.md",
]

CORE_NEWSLETTERS = [
    "beyond-vibe-checks-a-pms-complete-guide-to-evals.md",
    "a-guide-to-ai-prototyping-for-product-managers.md",
    "everyone-should-be-using-claude-code-more.md",
    "essential-reading-for-product-builders-part-1.md",
]


def download_file(url: str, dest_path: Path) -> bool:
    """Safely download a file with headers and error handling."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LennyGrowthAssistant-Ingestion/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read()
            dest_path.write_bytes(content)
        return True
    except Exception as e:
        print(f"[-] Failed to download {url}: {e}")
        return False


def fetch_remote_transcripts(data_dir: Path, max_episodes: int = 15) -> int:
    """Download key podcast transcripts and newsletters from GitHub."""
    print(f"[*] Fetching transcripts from {GITHUB_RAW_BASE}...")
    downloaded = 0

    podcasts_dir = data_dir / "podcasts"
    newsletters_dir = data_dir / "newsletters"
    podcasts_dir.mkdir(parents=True, exist_ok=True)
    newsletters_dir.mkdir(parents=True, exist_ok=True)

    # 1. Download core curated podcasts
    episodes_to_fetch = CORE_EPISODES[:max_episodes]
    for ep in episodes_to_fetch:
        dest = podcasts_dir / ep
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"[+] Already present: podcasts/{ep}")
            downloaded += 1
            continue
        url = f"{GITHUB_RAW_BASE}/podcasts/{ep}"
        print(f"[>] Downloading podcasts/{ep}...")
        if download_file(url, dest):
            downloaded += 1

    # 2. Download core newsletters
    for nl in CORE_NEWSLETTERS:
        dest = newsletters_dir / nl
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"[+] Already present: newsletters/{nl}")
            downloaded += 1
            continue
        url = f"{GITHUB_RAW_BASE}/newsletters/{nl}"
        print(f"[>] Downloading newsletters/{nl}...")
        if download_file(url, dest):
            downloaded += 1

    print(f"[+] Download complete: {downloaded} documents ready in {data_dir}")
    return downloaded


def run_ingestion(
    data_dir: Path,
    vector_store_dir: Path,
    fixtures_dir: Optional[Path] = None,
    chunk_size: int = 380,
    overlap: int = 50,
    force_reindex: bool = False,
) -> Dict[str, Any]:
    """Execute the full parsing, chunking, and vector indexing pipeline."""
    print("=" * 65)
    print(" LENNY GROWTH ASSISTANT - TRANSCRIPT INGESTION PIPELINE")
    print("=" * 65)
    print(f" Source Directory: {data_dir}")
    print(f" Vector Store Dir: {vector_store_dir}")
    print(f" Target Chunk Size: {chunk_size} words (Overlap: {overlap} words)")

    vector_store = HybridVectorStore(index_dir=str(vector_store_dir))
    if not force_reindex and vector_store.is_indexed():
        status = vector_store.get_status()
        print(f"[i] Vector store already indexed with {status['total_chunks']} chunks from {status['total_sources']} sources.")
        print("    Use --force-reindex to overwrite.")
        return status

    parser = TranscriptParser()
    chunker = TranscriptChunker(chunk_size_words=chunk_size, overlap_words=overlap)

    # Gather markdown files from data_dir and/or fixtures_dir
    search_dirs = [data_dir]
    if fixtures_dir and fixtures_dir.exists():
        search_dirs.append(fixtures_dir)

    md_files = []
    seen_names = set()
    for s_dir in search_dirs:
        for root, _, files in os.walk(s_dir):
            for file in files:
                if file.endswith(".md") and file not in seen_names and file != "README.md" and file != "LICENSE.md":
                    seen_names.add(file)
                    md_files.append(Path(root) / file)

    print(f"[*] Found {len(md_files)} markdown documents to parse.")
    if not md_files:
        print("[!] No transcript files found! Please run with --download to fetch transcripts.")
        return {"status": "error", "message": "No transcripts found"}

    all_chunks = []
    sources_summary = []

    for file_path in md_files:
        try:
            doc = parser.parse_file(file_path)
            chunks = chunker.chunk_document(doc)
            all_chunks.extend(chunks)
            sources_summary.append({
                "title": doc.title,
                "guest": doc.guest,
                "type": doc.doc_type,
                "url": doc.post_url,
                "word_count": doc.word_count,
                "chunks": len(chunks),
                "filename": file_path.name,
            })
            print(f"  [OK] {doc.title[:45]}... ({len(chunks)} chunks, {doc.word_count} words)")
        except Exception as e:
            print(f"  [ERR] Failed parsing {file_path.name}: {e}")

    print(f"\n[*] Total extracted chunks: {len(all_chunks)}")
    print("[*] Building hybrid vector & keyword index...")
    vector_store.build_index(all_chunks, sources_summary)

    status = vector_store.get_status()
    print("[+] Ingestion complete!")
    print(f"    Total Sources: {status['total_sources']}")
    print(f"    Total Chunks:  {status['total_chunks']}")
    print(f"    Vocabulary:    {status.get('vocab_size', 0)} terms")
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Lenny's transcripts into vector store")
    parser.add_argument("--download", action="store_true", help="Download core transcripts from Lenny's public repo")
    parser.add_argument("--download-all", action="store_true", help="Download all available transcripts")
    parser.add_argument("--force-reindex", action="store_true", help="Force rebuild of index even if already exists")
    parser.add_argument("--data-dir", default=str(PROJECT_ROOT / "data" / "transcripts"), help="Directory containing transcripts")
    parser.add_argument("--fixtures-dir", default=str(PROJECT_ROOT / "data" / "fixtures"), help="Directory containing fallback fixtures")
    parser.add_argument("--vector-store-dir", default=str(PROJECT_ROOT / "data" / "vector_store"), help="Directory to save index")

    args = parser.parse_args()

    data_path = Path(args.data_dir)
    fixtures_path = Path(args.fixtures_dir)
    vector_path = Path(args.vector_store_dir)

    if args.download or args.download_all:
        max_eps = 50 if args.download_all else 15
        fetch_remote_transcripts(data_path, max_episodes=max_eps)

    run_ingestion(
        data_dir=data_path,
        vector_store_dir=vector_path,
        fixtures_dir=fixtures_path,
        force_reindex=args.force_reindex,
    )
