"""Demo 2: SCENARIO DATABASE - Explore 95 COLREGS Training Scenarios"""
from seaforge_colregs import (
    load_scenarios, 
    get_scenario, 
    get_scenarios_by_category, 
    get_categories,
    get_difficulty_breakdown
)

print("\n" + "="*70)
print("  DEMO 2: COLREGS TRAINING DATABASE")
print("="*70)

print("\n📚 DATABASE OVERVIEW:")
all_scenarios = load_scenarios()
print(f"   Total scenarios: {len(all_scenarios)}")

cats = get_categories()
print(f"   Categories ({len(cats)}): {', '.join(cats)}\n")

print("🎲 RANDOM SCENARIO:")
scenario = get_scenario(random=True)
print(f"   Category: {scenario['category']}")
print(f"   Difficulty: {'⭐'*scenario['difficulty']}")
print(f"   Q: {scenario['scenario']}")
print(f"   A: {scenario['answer']}")
print(f"   Rule: {scenario['rule']}\n")

print("💡 LIGHTS CATEGORY:")
lights = get_scenarios_by_category("lights")
print(f"   Found {len(lights)} lights scenarios")
for i, s in enumerate(lights[:3], 1):
    print(f"   {i}. {s['rule']}: {s['scenario'][:55]}...")

print("\n📊 ENCOUNTER SCENARIOS BY DIFFICULTY:")
breakdown = get_difficulty_breakdown("encounters")
print(f"   Easy (1 star):   {breakdown.get(1, 0)} scenarios")
print(f"   Medium (2 star): {breakdown.get(2, 0)} scenarios")
print(f"   Hard (3 star):   {breakdown.get(3, 0)} scenarios")

print("\n" + "="*70)
print("✅ Demo 2 Complete: Database fully accessible, 95 scenarios loaded\n")
