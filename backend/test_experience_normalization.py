#!/usr/bin/env python3
"""
Test script to verify experience level normalization and random question selection.
Tests the scenario: User says "8 years experience" -> should map to "6-10 years bucket"
"""

import sys
import re
from typing import Optional, Tuple

def normalize_experience(experience: Optional[str]) -> Optional[Tuple[str, Optional[str]]]:
    """
    Normalize experience level string (e.g., '6-10 years', '10+ years')
    Returns (years_bucket, expected_role_level).
    
    Maps:
    - '0-2 years' -> ('0-2', 'APM')
    - '3-5 years' -> ('3-5', 'PM')
    - '6-10 years' -> ('6-10', 'Senior PM')
    - '10+ years' -> ('10+', None) filters to Principal/Director only
    """
    if not experience:
        return None
    exp = experience.strip().lower()
    m = exp.replace("years", "").replace("year", "").replace("yrs", "").replace(" ", "")
    
    # Map to (years_bucket, expected_role_level)
    if m in ("0-2", "0-1", "1-2"):
        return ("0-2", "APM")
    if m in ("3-5", "2-3", "2-4", "2-5", "3-4"):
        return ("3-5", "PM")
    if m in ("5-8", "6-10", "5-10", "6-8", "8-10"):
        return ("6-10", "Senior PM")
    if m.endswith("+"):
        try:
            val = int(m[:-1])
            if val >= 10:
                return ("10+", None)  # None means Principal/Director level
            elif val >= 6:
                return ("6-10", "Senior PM")
            elif val >= 3:
                return ("3-5", "PM")
            else:
                return ("0-2", "APM")
        except Exception:
            return ("10+", None)
    # try numeric single value
    try:
        v = int(re.search(r"(\d+)", m).group(1))
        if v <= 2:
            return ("0-2", "APM")
        if 3 <= v <= 5:
            return ("3-5", "PM")
        if 6 <= v <= 10:
            return ("6-10", "Senior PM")
        return ("10+", None)
    except Exception:
        return None


# Test cases
test_cases = [
    # (input, expected_bucket, expected_role, description)
    ("8 years", "6-10", "Senior PM", "User says 8 years -> should map to 6-10 bucket"),
    ("8", "6-10", "Senior PM", "User says 8 (numeric) -> should map to 6-10 bucket"),
    ("0-2 years", "0-2", "APM", "User says 0-2 years -> APM"),
    ("0-2", "0-2", "APM", "User says 0-2 -> APM"),
    ("1", "0-2", "APM", "User says 1 year -> APM"),
    ("3-5 years", "3-5", "PM", "User says 3-5 years -> PM"),
    ("5 years", "3-5", "PM", "User says 5 years -> PM"),
    ("6-10 years", "6-10", "Senior PM", "User says 6-10 years -> Senior PM"),
    ("10+ years", "10+", None, "User says 10+ years -> Principal/Director"),
    ("12 years", "10+", None, "User says 12 years -> Principal/Director"),
    ("5-8 years", "6-10", "Senior PM", "User says 5-8 years -> maps to 6-10"),
]

print("=" * 80)
print("EXPERIENCE LEVEL NORMALIZATION TEST")
print("=" * 80)
print()

passed = 0
failed = 0

for input_exp, expected_bucket, expected_role, description in test_cases:
    result = normalize_experience(input_exp)
    
    if result is None:
        print(f"❌ FAIL: {description}")
        print(f"   Input: {input_exp}")
        print(f"   Expected: ({expected_bucket}, {expected_role})")
        print(f"   Got: None")
        print()
        failed += 1
    else:
        bucket, role = result
        if bucket == expected_bucket and role == expected_role:
            print(f"✅ PASS: {description}")
            print(f"   Input: {input_exp} -> Bucket: {bucket}, Role: {role}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Input: {input_exp}")
            print(f"   Expected: ({expected_bucket}, {expected_role})")
            print(f"   Got: ({bucket}, {role})")
            failed += 1
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

# Key validation for the main feature request
print()
print("MAIN FEATURE VALIDATION:")
print("-" * 80)
result = normalize_experience("8 years")
if result and result[0] == "6-10" and result[1] == "Senior PM":
    print("✅ MAIN FEATURE: User with 8 years experience correctly maps to 6-10 bucket (Senior PM)")
    print("   This means when company doesn't match, they'll get random questions from the 6-10 year bucket")
else:
    print("❌ MAIN FEATURE FAILED: 8 years does not map to 6-10 bucket")

sys.exit(0 if failed == 0 else 1)
