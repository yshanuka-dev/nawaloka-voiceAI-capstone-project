#!/usr/bin/env python3
"""
Generate internal knowledge base Markdown files from config/faqs.yaml.

Creates structured Markdown documents in data/knowledge_base/ for ingestion into Qdrant.
"""

from pathlib import Path
import yaml

CATEGORY_TITLES = {
    "staff": "Staff and HR Policies",
    "clinical": "Clinical Protocols and Patient Care",
    "emergency": "Emergency Procedures and Code Protocols",
    "infection_control": "Infection Prevention and Control Guidelines",
    "patient_safety": "Patient Safety and Quality Assurance",
    "cardiology": "Cardiology Department Services and Procedures",
    "radiology": "Radiology and Diagnostic Imaging Services",
    "laboratory": "Laboratory Services and Pathology Guidelines",
    "pharmacy": "Pharmacy Services and Medication Management",
    "billing": "Billing, Insurance, and Payment Policies",
    "privacy": "Patient Privacy and Data Protection Policies",
    "training": "Staff Training and Continuing Professional Development",
    "patient_faqs": "General Patient FAQs, Visiting Hours, and Hospital Facilities",
}


def build_kb():
    root = Path(__file__).resolve().parent.parent
    faqs_path = root / "config" / "faqs.yaml"
    out_dir = root / "data" / "knowledge_base"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(faqs_path, "r", encoding="utf-8") as f:
        faqs_data = yaml.safe_load(f) or {}

    created = []
    for idx, (category, items) in enumerate(faqs_data.items(), 1):
        if not isinstance(items, list):
            continue

        title = CATEGORY_TITLES.get(category, category.replace("_", " ").title())
        lines = [f"# {title}\n"]

        for item in items:
            q = item.get("query", "").strip()
            a = item.get("answer", "").strip()
            if not q or not a:
                continue
            lines.append(f"## {q}\n")
            lines.append(f"{a}\n")

        filename = f"{idx:02d}_{category}.md"
        filepath = out_dir / filename
        filepath.write_text("\n".join(lines), encoding="utf-8")
        created.append(filename)

    print(f"Generated {len(created)} knowledge-base documents in {out_dir}")
    return 0


if __name__ == "__main__":
    build_kb()

