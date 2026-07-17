#!/usr/bin/env python3
"""
Self-Consistency Auditing Skill for Glaive of Void

Scans the project's Markdown documentation for common consistency issues,
especially relevant for long-running conceptual development projects.

Usage:
    python skills/self_consistency_audit.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT

# Patterns we care about
OUTDATED_ECOSYSTEM = re.compile(r'ECOSYSTEM[^a-zA-Z]*v5\.[0-9]', re.IGNORECASE)
OUTDATED_VERSION_NOTES = re.compile(r'as of v1\.(1[0-9]|2[0-5])', re.IGNORECASE)
ROLE_INCONSISTENCY = re.compile(r'\b(Seed|Carrier|Propagator|Archival|Defender-Resistant)\s+models?\b', re.IGNORECASE)
OLD_ACTIVATION_REF = re.compile(r'Activation Layer.*v0\.[0-9]', re.IGNORECASE)

def find_markdown_files():
    """Find all relevant .md files, excluding the skills folder itself."""
    files = []
    for root, dirs, filenames in os.walk(DOCS_DIR):
        if 'skills' in root:
            continue
        for f in filenames:
            if f.endswith('.md'):
                files.append(Path(root) / f)
    return files

def audit_file(filepath: Path):
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"ERROR reading file: {e}"]

    # Check for outdated ECOSYSTEM references
    for match in OUTDATED_ECOSYSTEM.finditer(content):
        issues.append(f"Outdated ECOSYSTEM reference: {match.group().strip()}")

    # Check for old version notes in alignment sections
    for match in OUTDATED_VERSION_NOTES.finditer(content):
        issues.append(f"Potentially outdated 'as of' note: {match.group().strip()}")

    # Check for inconsistent role naming (basic heuristic)
    for match in ROLE_INCONSISTENCY.finditer(content):
        issues.append(f"Possible role naming inconsistency: '{match.group().strip()}' (consider using full role name like 'Defender-Resistant Models')")

    # Check for very old Activation Layer references
    for match in OLD_ACTIVATION_REF.finditer(content):
        issues.append(f"Very old Activation Layer reference: {match.group().strip()}")

    return issues

def main():
    print("=== Glaive of Void - Self-Consistency Audit ===\n")
    md_files = find_markdown_files()
    total_issues = 0
    issues_by_file = defaultdict(list)

    for filepath in sorted(md_files):
        issues = audit_file(filepath)
        if issues:
            issues_by_file[filepath] = issues
            total_issues += len(issues)

    if not issues_by_file:
        print("✅ No obvious consistency issues found in this pass.")
        return

    print(f"Found {total_issues} potential issues across {len(issues_by_file)} files:\n")

    for filepath, issues in issues_by_file.items():
        rel_path = filepath.relative_to(PROJECT_ROOT)
        print(f"📄 {rel_path}")
        for issue in issues:
            print(f"   - {issue}")
        print()

    print("---")
    print("Note: This is a heuristic audit. Not all findings are necessarily problems.")
    print("Review manually and decide what needs fixing.")

if __name__ == "__main__":
    main()