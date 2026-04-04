"""Demo 3: INTERACTIVE TRAINER - Quiz Yourself on COLREGS"""
from seaforge_colregs import get_scenario, get_categories

print("\n" + "="*70)
print("  DEMO 3: INTERACTIVE COLREGS TRAINER")
print("="*70)

categories = get_categories()
print(f"\nAvailable categories: {', '.join(categories)}\n")
print("Let's test 5 random COLREGS scenarios!\n")

score = 0
for i in range(5):
    scenario = get_scenario(random=True)
    
    print(f"\n{'='*70}")
    print(f"[Question {i+1}/5] | {scenario['category'].upper()} | Difficulty: {'⭐'*scenario['difficulty']}")
    print(f"{'='*70}")
    print(f"\n📋 SCENARIO:\n   {scenario['scenario']}\n")
    
    input("👉 Press ENTER to reveal the answer... ")
    
    print(f"\n✓ ANSWER:\n   {scenario['answer']}")
    print(f"   Rule: {scenario['rule']}")
    
    score += 1

print(f"\n{'='*70}")
print(f"✅ Quiz Complete! Score: {score}/5 (100%)")
print(f"🎉 Excellent navigation skills!")
print(f"{'='*70}\n")
