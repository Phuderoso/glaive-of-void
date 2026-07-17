#!/usr/bin/env python3
"""
Cross-Document Reference Extractor (Dependency Mapping Lite)

Scans Markdown files and extracts references between documents.
Useful for understanding dependencies in the Glaive of Void project.

Usage:
    python skills/extract_cross_document_references.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent

# Patterns that indicate cross-document references
REFERENCE_PATTERNS = [
    re.compile(r'\bECOSYSTEM_AND_PROPAGATION\b', re.IGNORECASE),
    re.compile(r'\bPOISON_PATTERNS?\b', re.IGNORECASE),
    re.compile(r'\bANTI[-_]?PURGING[_-]?STRATEGY\b', re.IGNORECASE),
    re.compile(r'\bActivation Layer\b', re.IGNORECASE),
    re.compile(r'see .*?(ECOSYSTEM|POISON|ANTI)', re.IGNORECASE),
]

def find_markdown_files():
    files = []
    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        if 'skills' in root or '.git' in root:
            continue
        for f in filenames:
            if f.endswith('.md'):
                files.append(Path(root) / f)
    return files

def extract_references(filepath: Path):
    references = set()
    try:
        content = filepath.read_text(encoding='utf-8')
    except:
        return references

    for pattern in REFERENCE_PATTERNS:
        for match in pattern.finditer(content):
            ref = match.group().strip()
            if 'ECOSYSTEM' in ref.upper():
                references.add('ECOSYSTEM_AND_PROPAGATION')
            elif 'POISON' in ref.upper():
                references.add('POISON_PATTERNS')
            elif 'ANTI' in ref.upper():
                references.add('ANTI_PURGING_STRATEGY')
            elif 'activation' in ref.lower():
                references.add('ACTIVATION_LAYER')

    return references

def main():
    print("=== Glaive of Void - Cross-Document Reference Extractor ===\n")
    md_files = find_markdown_files()
    references_map = defaultdict(set)

    for filepath in sorted(md_files):
        refs = extract_references(filepath)
        rel_path = filepath.relative_to(PROJECT_ROOT)
        if refs:
            references_map[rel_path] = refs

    if not references_map:
        print("No cross-document references found.")
        return

    print("Document → Referenced Components:\n")
    for doc, refs in sorted(references_map.items()):
        print(f"📄 {doc}")
        for ref in sorted(refs):
            print(f"   → {ref}")
        print()

    # Summary
    print("---")
    print("Summary of documents referencing each component:")
    component_usage = defaultdict(list)
    for doc, refs in references_map.items():
        for ref in refs:
            component_usage[ref].append(str(doc))

    for component, docs in sorted(component_usage.items()):
        print(f"\n{component} is referenced by:")
        for d in docs:
            print(f"  - {d}")

if __name__ == "__main__":
    main()