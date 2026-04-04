"""Demo 1: HEAD-ON ENCOUNTER - COLREGS Engine + Collision Risk"""
from seaforge_colregs import classify_encounter, compute_cpa_tcpa, bearing_to

print("\n" + "="*70)
print("  DEMO 1: HEAD-ON ENCOUNTER - COLREGS ENGINE")
print("="*70)

print("\n📍 SCENARIO: Two vessels approaching head-on")
print("   Own vessel: Heading North (COG 0°), Speed 12 knots")
print("   Target vessel: Heading South (COG 180°), Speed 10 knots")
print("   Position: 600m apart (Greenwich area)\n")

own_cog = 0      
target_cog = 180 
rel_bearing = 180 

situation, role, rule, action = classify_encounter(own_cog, target_cog, rel_bearing)
print(f"⚡ COLREGS CLASSIFICATION:")
print(f"   Situation: {situation}")
print(f"   Your role: {role}")
print(f"   Apply: {rule}")
print(f"   Action: {action}\n")

print("📊 COLLISION RISK ANALYSIS:")
own_lat, own_lon = 51.4769, -0.0005  
own_sog = 12  
target_lat, target_lon = 51.4769, 0.0005  
target_sog = 10  

cpa, tcpa, _, _ = compute_cpa_tcpa(own_lat, own_lon, own_cog, own_sog,
                                    target_lat, target_lon, target_cog, target_sog)
brg = bearing_to(own_lat, own_lon, target_lat, target_lon)

print(f"   Bearing to target: {brg}°")
print(f"   Closest Point of Approach (CPA): {cpa}nm")
print(f"   Time to CPA (TCPA): {tcpa}min")
if cpa < 0.5:
    print(f"\n   ⚠️  COLLISION RISK ALERT - CPA < 0.5nm!")
    print(f"   Action required IMMEDIATELY!\n")

print("="*70)
print("✅ Demo 1 Complete: Engine working, collision risk calculated\n")
