import re
import pdfplumber

from config import POLICIES_DIR

PART_HEADINGS = [
    "PART I - DECLARATIONS",
    "PART II - SCHEDULE OF COVERAGE",
    "PART III - EXCLUSIONS",
    "PART IV - CONDITIONS",
    "PART V - ENDORSEMENTS",
]

def format_table(table_rows, has_header):
    """
    Turns a pdfplumber table (a list of lists of cell strings) into one
    readable text block, joining each row's cells with " | ".
    """
    lines = []
    rows = table_rows[1:] if has_header else table_rows
    header = table_rows[0] if has_header else None

    if header:
        lines.append(" | ".join(cell.strip() if cell else "" for cell in header))
        lines.append("-" * 40)

    for row in rows:
        clean_cells = [cell.strip().replace("\n", " ") if cell else "" for cell in row]
        lines.append(" | ".join(clean_cells))

    return "\n".join(lines)


def extract_policy_id(all_text):
    """Pulls the policy number (e.g. POL-1007) out of the document text."""
    match = re.search(r"POL-\d{4}", all_text)
    return match.group(0) if match else "UNKNOWN"


def extract_tier(all_text):
    """Pulls the 'Policy Tier: ...' line out of the document text."""
    match = re.search(r"Policy Tier:\s*(.+)", all_text)
    return match.group(1).strip() if match else "UNKNOWN"


def split_into_parts(all_text):
    """
    Splits the full document text into 5 pieces, one per PART heading. Returns a dict like {"PART I - DECLARATIONS": "...text...", ...}
    """
    positions = []
    for heading in PART_HEADINGS:
        idx = all_text.find(heading)
        if idx != -1:
            positions.append((idx, heading))
    positions.sort()

    parts = {}
    for i, (start_idx, heading) in enumerate(positions):
        text_start = start_idx + len(heading)
        text_end = positions[i + 1][0] if i + 1 < len(positions) else len(all_text)
        parts[heading] = all_text[text_start:text_end].strip()

    return parts

def extract_full_field(all_text, field_name, next_field_name):
    """
    pdfplumber's extract_tables() clips cell text to the table's drawn
    column width, which truncates long values like a lapsed-policy
    status message. This recovers the full value from the plain-text
    layer instead, where it isn't clipped, by capturing everything
    between this field's label and the next one.
    """
    pattern = re.escape(field_name) + r"\s*(.*?)\s*" + re.escape(next_field_name)
    match = re.search(pattern, all_text, re.DOTALL)
    if match:
        return " ".join(match.group(1).split())
    return None

def process_one_policy(pdf_path):
    """
    Reads one policy PDF and returns a list of 5 chunk dicts (one per
    Part). Each dict carries policy_id/tier metadata alongside the text,
    which is what lets rag.py later filter search results by policy,
    not just search by meaning.
    """
    with pdfplumber.open(pdf_path) as pdf:
        page1 = pdf.pages[0]
        tables = page1.extract_tables()

        # Join text from every page so we can find the Part headings and
        # pull the plain-text Parts (III, IV, V).
        full_text = "\n".join(page.extract_text() for page in pdf.pages)

        declarations_table = format_table(tables[0], has_header=False)
        coverage_table = format_table(tables[1], has_header=True)

        full_status = extract_full_field(full_text, "Policy Status", "Geographical Scope")
        if full_status and full_status not in declarations_table:
            declarations_table = re.sub(
                r"Policy Status \|.*",
                f"Policy Status | {full_status}",
                declarations_table,
            )
            
    policy_id = extract_policy_id(full_text)
    tier = extract_tier(full_text)
    raw_parts = split_into_parts(full_text)

    chunks = [
        {
            "policy_id": policy_id,
            "tier": tier,
            "part": "PART I - DECLARATIONS",
            "text": "PART I - DECLARATIONS\n" + declarations_table,
        },
        {
            "policy_id": policy_id,
            "tier": tier,
            "part": "PART II - SCHEDULE OF COVERAGE",
            "text": "PART II - SCHEDULE OF COVERAGE\n" + coverage_table,
        },
        {
            "policy_id": policy_id,
            "tier": tier,
            "part": "PART III - EXCLUSIONS",
            "text": "PART III - EXCLUSIONS\n" + raw_parts.get("PART III - EXCLUSIONS", ""),
        },
        {
            "policy_id": policy_id,
            "tier": tier,
            "part": "PART IV - CONDITIONS",
            "text": "PART IV - CONDITIONS\n" + raw_parts.get("PART IV - CONDITIONS", ""),
        },
        {
            "policy_id": policy_id,
            "tier": tier,
            "part": "PART V - ENDORSEMENTS",
            "text": "PART V - ENDORSEMENTS\n" + raw_parts.get("PART V - ENDORSEMENTS", ""),
        },
    ]
    return chunks


def load_all_policy_chunks():
    """
    Main entry point for this file. Reads every PDF in data/policies/
    and returns one big list of chunk dicts, ready to be embedded by
    rag.py. This is the function other files should import and call.
    """
    all_chunks = []
    pdf_paths = sorted(POLICIES_DIR.glob("*.pdf"))

    for path in pdf_paths:
        all_chunks.extend(process_one_policy(path))

    return all_chunks


if __name__ == "__main__":
    # Quick manual test: run this file directly to check chunking works
    # before wiring it into rag.py.
    chunks = load_all_policy_chunks()
    print(f"Loaded {len(chunks)} chunks from {len(chunks) // 5} policies.")
    print("\nSample chunk (first one):")
    print(chunks[0]["policy_id"], "-", chunks[0]["part"])
    print(chunks[0]["text"][:200])