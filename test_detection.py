# -*- coding: utf-8 -*-
"""Test detection fix for v4.0"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from blueprint_schema import get_blueprint_for_command

tests = [
    # Simple matches - should find preset
    ("בנה כדור", "Ball", "simple ball"),
    ("בנה רקטה", "Rocket", "simple rocket"),
    ("בנה כלב", "Dog", "simple dog"),
    ("בנה בית", "House", "simple house"),
    ("בנה חתול", "Cat", "simple cat"),
    ("בנה חללית", "Spaceship", "simple spaceship"),
    # Complex commands with 2+ commas - should return None (go to LLM)
    ("בנה תחנת חלל עם חללית, כוכבים, כדור הארץ", None, "space station complex"),
    ("בנה פארק מים עם בריכה, מגלשות, כיסאות", None, "water park complex"),
    ("בנה טירה עם 4 מגדלים, חומות, שער", None, "castle complex"),
    # Compound exclusion - should NOT match ball for "כדור הארץ"
    ("בנה כדור הארץ", None, "earth should not match ball"),
    # Multi-word match priority - longest match wins
    ("בנה מגרש כדורגל", "SoccerField", "soccer field multi-word"),
    ("בנה בריכת שחייה", "Pool", "pool multi-word"),
]

print("Detection Fix Tests:")
print("=" * 50)
passed = 0
failed = 0
for cmd, expected, desc in tests:
    result = get_blueprint_for_command(cmd)
    got = result.name if result else None
    ok = got == expected
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"  [{status}] {desc}: expected={expected}, got={got}")

print(f"\nResults: {passed}/{passed+failed} passed")
if failed:
    sys.exit(1)
