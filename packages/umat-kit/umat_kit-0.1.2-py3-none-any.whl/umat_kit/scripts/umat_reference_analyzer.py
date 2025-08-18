#!/usr/bin/env python3
"""
UMAT Student Reference Number Analyzer
Analyze the pattern of UMAT student reference numbers
"""

import re
from datetime import datetime

def analyze_reference_numbers():
    """Analyze the provided UMAT reference numbers to identify patterns"""

    # Provided valid reference numbers
    valid_refs = [
        "9012562822",
        "9012281822"
    ]

    print("=" * 60)
    print("UMAT STUDENT REFERENCE NUMBER PATTERN ANALYSIS")
    print("=" * 60)

    print(f"\nAnalyzing {len(valid_refs)} valid reference numbers:")
    for i, ref in enumerate(valid_refs, 1):
        print(f"  {i}. {ref}")

    print("\n" + "=" * 40)
    print("DETAILED ANALYSIS")
    print("=" * 40)

    # Basic analysis
    print(f"\nLength: {len(valid_refs[0])} digits (all numbers same length: {all(len(ref) == 10 for ref in valid_refs)})")

    # Position-by-position analysis
    print("\nPosition-by-position breakdown:")
    print("Position:  1 2 3 4 5 6 7 8 9 10")
    print("          " + "-" * 20)

    for i, ref in enumerate(valid_refs, 1):
        print(f"Ref {i}:     {' '.join(ref)}")

    # Pattern analysis
    print("\n" + "=" * 40)
    print("PATTERN IDENTIFICATION")
    print("=" * 40)

    # Check common prefixes
    common_prefix = ""
    for i in range(len(valid_refs[0])):
        if all(ref[i] == valid_refs[0][i] for ref in valid_refs):
            common_prefix += valid_refs[0][i]
        else:
            break

    print(f"\nCommon prefix: '{common_prefix}' (first {len(common_prefix)} digits)")

    # Analyze differences
    print("\nDifferences analysis:")
    ref1, ref2 = valid_refs[0], valid_refs[1]

    for i in range(len(ref1)):
        if ref1[i] != ref2[i]:
            print(f"  Position {i+1}: {ref1[i]} vs {ref2[i]} (difference: {abs(int(ref1[i]) - int(ref2[i]))})")

    # Possible interpretations
    print("\n" + "=" * 40)
    print("POSSIBLE PATTERN INTERPRETATIONS")
    print("=" * 40)

    print("\nBased on the analysis, possible patterns:")

    # Pattern 1: Year-based
    if "22" in common_prefix or ref1.endswith("22") or ref2.endswith("22"):
        print("1. Year-based pattern (2022 = '22')")
        if ref1.endswith("22") and ref2.endswith("22"):
            print("   - Last 2 digits: '22' (year 2022)")
            print("   - First 8 digits: unique identifier")

    # Pattern 2: Sequential
    print("2. Sequential numbering pattern")
    print(f"   - Base: {common_prefix}")
    print(f"   - Variable part: positions {len(common_prefix)+1}-10")

    # Pattern 3: Encoded information
    print("3. Encoded information pattern")
    print("   - Could contain: year, program code, sequence number")

    return {
        'common_prefix': common_prefix,
        'length': len(valid_refs[0]),
        'valid_refs': valid_refs,
        'differences': [(i, ref1[i], ref2[i]) for i in range(len(ref1)) if ref1[i] != ref2[i]]
    }

if __name__ == "__main__":
    analysis = analyze_reference_numbers()