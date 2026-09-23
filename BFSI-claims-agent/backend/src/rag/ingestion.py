"""
RAG ingestion: read the 15 policy PDFs, split each into section-based
chunks, embed them, and upsert into the ChromaDB collection.

This replaces chunk_policies.py's standalone JSON-file step -- instead of
writing policy_chunks.json for a second script to read, chunking and
vector-store writing now happen in one pipeline, backed by vector_store.py.

Why chunk by section instead of by fixed word count?
Our PDFs already have clear, consistent section headers (Coverage Details,
Inclusions, Exclusions, etc.), so splitting on those headers gives us
chunks that are naturally "about one thing" -- exactly what we want for
retrieval. A fixed-size chunk could cut a clause in half.

Run standalone:
    python -m src.rag.ingestion
Re-run any time a policy PDF changes -- it always wipes and rebuilds the
whole collection, so it's safe to re-run any time.
"""

import csv
import re
from pathlib import Path

import pdfplumber

from src.rag.vector_store import reset_collection
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Anchor every path to the project root so this runs the same whether it's
# invoked from backend/, from rag/, or by main.py on server startup.
# .../backend/src/rag/ingestion.py -> parents[3] is the project root
# (the folder containing backend/, frontend/ and data/).
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
POLICIES_CSV = DATA_DIR / "policies.csv"

# Exact section headings printed on every policy PDF -- text is split
# wherever one of these lines appears.
SECTION_HEADERS = [
    "Policy Information",
    "Motor Coverage Details",
    "Medical Coverage Details",
    "Life Coverage Details",
    "What This Policy Covers (Inclusions)",
    "What This Policy Does Not Cover (Exclusions)",
    "Claim Intimation & Documentation Requirements",
    "General Terms & Conditions",
]

# Letterhead/footer/signature lines that repeat on every page and carry no
# retrieval-useful information -- dropped before chunking.
BOILERPLATE_PATTERNS = [
    r"^Meridian Shield Insurance Co\. Ltd\.$",
    r"^Protection You Can Trust$",
    r"^5th Floor, Sentinel Business Park",
    r"^IRDAI Reg\. No\.",
    r"^Specimen document generated",
    r"^Authorized Signatory$",
    r"^Company Seal$",
    r"^_+\s+_+$",
    r"^M$",  # the single "M" letter drawn inside the logo shield
]


def is_boilerplate(line):
    """True if this line is letterhead/footer/signature text we should skip."""
    return any(re.match(pattern, line.strip()) for pattern in BOILERPLATE_PATTERNS)


def extract_clean_lines(pdf_path):
    """Read a PDF and return its text as a list of lines, boilerplate removed."""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            for line in page_text.split("\n"):
                if line.strip() and not is_boilerplate(line):
                    lines.append(line.strip())
    return lines


def split_into_sections(lines):
    """
    Group lines into (section_name, section_text) tuples using
    SECTION_HEADERS as split points. Anything before the first recognized
    header (the title + "Policy Type: ..." line) is folded into the first
    real section instead of kept as its own tiny chunk.
    """
    sections = []
    current_header = "Document Intro"
    current_lines = []

    for line in lines:
        if line in SECTION_HEADERS:
            if current_lines:
                sections.append((current_header, " ".join(current_lines)))
            current_header = line
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_header, " ".join(current_lines)))

    if sections and sections[0][0] == "Document Intro":
        intro_text = sections[0][1]
        next_header, next_text = sections[1]
        sections = [(next_header, intro_text + " " + next_text)] + sections[2:]

    return sections


def chunk_policy_pdf(pdf_path, policy_meta):
    """Build the list of chunk dicts for one policy PDF."""
    lines = extract_clean_lines(pdf_path)
    sections = split_into_sections(lines)

    chunks = []
    for i, (section_name, section_text) in enumerate(sections):
        chunks.append({
            # Deterministic id -> re-running ingestion upserts in place
            # instead of accumulating duplicate chunks per policy.
            "id": f'{policy_meta["policy_id"]}::{i:02d}',
            "policy_id": policy_meta["policy_id"],
            "policy_type": policy_meta["policy_type"],
            "sub_type": policy_meta["sub_type"],
            "section": section_name,
            "text": section_text,
        })
    return chunks


def load_policy_rows():
    """Read policies.csv -- the manifest of which PDF belongs to which policy_id."""
    with open(POLICIES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run():
    """Wipe and rebuild the vector store from every PDF listed in policies.csv."""
    collection = reset_collection()
    policies = load_policy_rows()

    total = 0
    for policy in policies:
        pdf_path = DATA_DIR / policy["policy_document"]
        chunks = chunk_policy_pdf(pdf_path, policy)

        collection.upsert(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[
                {
                    "policy_id": c["policy_id"],
                    "policy_type": c["policy_type"],
                    "sub_type": c["sub_type"],
                    "section": c["section"],
                }
                for c in chunks
            ],
        )
        total += len(chunks)
        logger.info(f'{policy["policy_id"]}: {len(chunks)} chunks ingested')

    logger.info(f"Ingestion complete -- {total} chunks across {len(policies)} policies")


if __name__ == "__main__":
    run()
