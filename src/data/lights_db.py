"""COLREGS training database — all 10 categories for STCW Table A-II/1 coverage.

Categories: lights, day_shapes, encounters, sound_signals_maneuvering,
sound_signals_fog, restricted_visibility, tss, narrow_channels,
general_rules, responsibilities

Sources: Popeye OOW/SAR workspace — COLREGS.md, GMDSS reference,
IMO COLREGs Consolidated 2026, IAMSAR Vol. III
"""

LIGHTS_DB = [
    # ── LIGHTS (Rules 20-31) ──────────────────────────────────────────

    {"scenario": "You see TWO masthead lights (vertical), sidelights, and a sternlight.",
     "answer": "Power-driven vessel underway, length 50m or more (Rule 23a).",
     "rule": "Rule 23(a)", "category": "lights", "difficulty": 1},

    {"scenario": "You see ONE masthead light, sidelights, and a sternlight.",
     "answer": "Power-driven vessel underway, length less than 50m (Rule 23a).",
     "rule": "Rule 23(a)", "category": "lights", "difficulty": 1},

    {"scenario": "You see THREE all-round lights in a vertical line: RED, WHITE, RED.",
     "answer": "Vessel Restricted in Ability to Manoeuvre (RAM). Keep clear per Rule 18.",
     "rule": "Rule 27(b)", "category": "lights", "difficulty": 1},

    {"scenario": "You see TWO all-round RED lights in a vertical line.",
     "answer": "Vessel Not Under Command (NUC). Keep clear per Rule 18.",
     "rule": "Rule 27(a)", "category": "lights", "difficulty": 1},

    {"scenario": "You see a GREEN over WHITE all-round light.",
     "answer": "Vessel engaged in trawling (Rule 26a). Making way if also showing sidelights + sternlight.",
     "rule": "Rule 26(a)", "category": "lights", "difficulty": 1},

    {"scenario": "You see a RED over WHITE all-round light.",
     "answer": "Vessel engaged in fishing other than trawling (Rule 26b). Gear extending >150m: additional white light in direction of gear.",
     "rule": "Rule 26(b)", "category": "lights", "difficulty": 2},

    {"scenario": "You see a RED over GREEN all-round light, plus sidelights.",
     "answer": "Sailing vessel underway, showing optional lights (Rule 25c). Red over green = 'sailing machine'.",
     "rule": "Rule 25(c)", "category": "lights", "difficulty": 2},

    {"scenario": "You see THREE all-round GREEN lights in a triangle (one top, two bottom) plus masthead and sidelights.",
     "answer": "Vessel engaged in mine clearance operations. Keep >1000m clear (Rule 27f).",
     "rule": "Rule 27(f)", "category": "lights", "difficulty": 3},

    {"scenario": "You see TWO all-round RED lights, vertical, plus anchor lights.",
     "answer": "Vessel NUC, at anchor. Not making way (Rule 27a + 30).",
     "rule": "Rule 27(a)/30", "category": "lights", "difficulty": 2},

    {"scenario": "You see a single WHITE all-round light.",
     "answer": "Vessel at anchor, less than 50m (Rule 30a). OR vessel under 7m/12m using simplified lights (Rule 23d/25d).",
     "rule": "Rule 30(a)", "category": "lights", "difficulty": 1},

    {"scenario": "You see TWO WHITE all-round lights, vertical, fore and aft (aft higher).",
     "answer": "Vessel at anchor, 50m or more (Rule 30a). Must also illuminate decks.",
     "rule": "Rule 30(a)", "category": "lights", "difficulty": 2},

    {"scenario": "You see a YELLOW flashing light (50-70 flashes/min).",
     "answer": "Hovercraft in non-displacement mode. Additional to normal power-driven lights (Rule 23b).",
     "rule": "Rule 23(b)", "category": "lights", "difficulty": 3},

    {"scenario": "You see a WHITE over RED all-round light.",
     "answer": "Pilot vessel on duty (Rule 29). White hat, red face.",
     "rule": "Rule 29", "category": "lights", "difficulty": 2},

    {"scenario": "You see TWO anchor lights plus TWO all-round RED lights in a vertical line.",
     "answer": "Vessel aground (Rule 30d). The two red lights are in addition to anchor lights.",
     "rule": "Rule 30(d)", "category": "lights", "difficulty": 2},

    {"scenario": "You see a YELLOW towing light above the sternlight, plus two masthead lights, sidelights.",
     "answer": "Power-driven vessel towing astern, tow length 200m or less (Rule 24a).",
     "rule": "Rule 24(a)", "category": "lights", "difficulty": 2},

    {"scenario": "You see THREE masthead lights (vertical), a yellow towing light, sidelights, and a sternlight.",
     "answer": "Power-driven vessel towing astern, tow length exceeds 200m (Rule 24a). Three masthead lights in a vertical line.",
     "rule": "Rule 24(a)", "category": "lights", "difficulty": 3},

    {"scenario": "You see a tricolour lantern at the masthead of a small vessel.",
     "answer": "Sailing vessel under 20m showing combined lantern (red/green/white) at masthead (Rule 25b). Cannot be used with separate sidelights.",
     "rule": "Rule 25(b)", "category": "lights", "difficulty": 2},

    {"scenario": "You see RED over WHITE over RED all-round lights, plus masthead and sidelights.",
     "answer": "RAM vessel making way (Rule 27b). The red-white-red lights plus normal steaming lights indicate the vessel is making way through the water.",
     "rule": "Rule 27(b)", "category": "lights", "difficulty": 3},

    {"scenario": "At what range should you see the masthead light of a vessel 50m or more in length?",
     "answer": "6 nautical miles minimum (Rule 22). Sidelights, sternlight, and towing light: 3nm.",
     "rule": "Rule 22", "category": "lights", "difficulty": 2},

    {"scenario": "You see a vessel showing only sidelights and a sternlight — no masthead light.",
     "answer": "Sailing vessel underway (Rule 25a). No masthead light distinguishes her from a power-driven vessel.",
     "rule": "Rule 25(a)", "category": "lights", "difficulty": 1},

    # ── DAY SHAPES (Rules 20-31) ─────────────────────────────────────

    {"scenario": "By day: you see a BALL shape on a vessel.",
     "answer": "Vessel at anchor (Rule 30). Forward part, visible all round.",
     "rule": "Rule 30(a)", "category": "day_shapes", "difficulty": 1},

    {"scenario": "By day: you see a DIAMOND shape on a vessel being towed.",
     "answer": "Vessel being towed, tow length exceeds 200m. Diamond shape displayed (Rule 24d).",
     "rule": "Rule 24(d)", "category": "day_shapes", "difficulty": 2},

    {"scenario": "By day: BALL-DIAMOND-BALL vertical on a vessel.",
     "answer": "Vessel Restricted in Ability to Manoeuvre (RAM) (Rule 27b day signal).",
     "rule": "Rule 27(b)", "category": "day_shapes", "difficulty": 1},

    {"scenario": "By day: TWO BALLS in a vertical line.",
     "answer": "Vessel Not Under Command (NUC) (Rule 27a day signal).",
     "rule": "Rule 27(a)", "category": "day_shapes", "difficulty": 1},

    {"scenario": "By day: a CYLINDER shape on a vessel.",
     "answer": "Vessel Constrained by her Draught (CBD) (Rule 28). Only applicable in certain waters.",
     "rule": "Rule 28", "category": "day_shapes", "difficulty": 2},

    {"scenario": "By day: a CONE point downward on a vessel.",
     "answer": "Sailing vessel under sail using engine (motorsailing). Must display cone point-down (Rule 25e).",
     "rule": "Rule 25(e)", "category": "day_shapes", "difficulty": 2},

    {"scenario": "By day: TWO CONES point-to-point (diamond shape) on a vessel.",
     "answer": "Vessel engaged in fishing (Rule 26). If gear extends >150m, additional cone in that direction.",
     "rule": "Rule 26", "category": "day_shapes", "difficulty": 2},

    {"scenario": "By day: THREE BALLS in a vertical line.",
     "answer": "Vessel aground (Rule 30d day signal).",
     "rule": "Rule 30(d)", "category": "day_shapes", "difficulty": 2},

    {"scenario": "By day: a BASKET shape on a vessel.",
     "answer": "Vessel engaged in fishing with gear extending less than 150m (Rule 26). Alternative to two cones for vessels under 20m.",
     "rule": "Rule 26", "category": "day_shapes", "difficulty": 3},

    # ── ENCOUNTERS (Rules 13-15) ──────────────────────────────────────

    {"scenario": "You see a GREEN sidelight only.",
     "answer": "You are seeing the starboard side. Target is crossing from your port to starboard, or heading away on a roughly parallel course. You are likely the STAND-ON vessel.",
     "rule": "Rule 21(b)", "category": "encounters", "difficulty": 1},

    {"scenario": "You see a RED sidelight only.",
     "answer": "You are seeing the port side. Target is crossing from your starboard. You may be the GIVE-WAY vessel (Rule 15). Assess risk of collision.",
     "rule": "Rule 15", "category": "encounters", "difficulty": 1},

    {"scenario": "You see BOTH red and green sidelights and a masthead light.",
     "answer": "Vessel heading directly toward you — HEAD-ON situation. Both vessels alter to STARBOARD (Rule 14).",
     "rule": "Rule 14", "category": "encounters", "difficulty": 1},

    {"scenario": "You see a sternlight (white) only.",
     "answer": "You are overtaking this vessel from astern. You are the GIVE-WAY vessel. Keep clear (Rule 13).",
     "rule": "Rule 13", "category": "encounters", "difficulty": 1},

    {"scenario": "Target vessel bearing 010° relative, similar speed, nearly reciprocal course. What situation and action?",
     "answer": "Head-on situation (Rule 14). Both vessels alter course to STARBOARD to pass port-to-port. If in any doubt, assume head-on.",
     "rule": "Rule 14", "category": "encounters", "difficulty": 1},

    {"scenario": "Target vessel bearing 045° relative (starboard bow), steady bearing, closing range. What situation and action?",
     "answer": "Crossing situation. Target is on your starboard side — you are the GIVE-WAY vessel (Rule 15). Alter to starboard, reduce speed, or both. Avoid crossing ahead of the other vessel.",
     "rule": "Rule 15", "category": "encounters", "difficulty": 2},

    {"scenario": "Target vessel bearing 315° relative (port bow), steady bearing, closing range. What situation and action?",
     "answer": "Crossing situation. Target is on your port side — you are the STAND-ON vessel (Rule 17). Maintain course and speed. Be prepared to take action if the give-way vessel does not act.",
     "rule": "Rule 17", "category": "encounters", "difficulty": 2},

    {"scenario": "You are approaching a vessel from 160° relative to its heading. What situation?",
     "answer": "You are OVERTAKING (Rule 13). More than 22.5° abaft the beam = overtaking. You are the give-way vessel. Once overtaking, always overtaking until past and clear.",
     "rule": "Rule 13", "category": "encounters", "difficulty": 2},

    {"scenario": "You are the stand-on vessel. The give-way vessel is not taking action. CPA is decreasing. What do you do?",
     "answer": "Rule 17(a)(ii): You MAY take action to avoid collision. If collision cannot be avoided by give-way alone, you SHALL take action (Rule 17(b)). Avoid altering to port for a vessel on your port side.",
     "rule": "Rule 17", "category": "encounters", "difficulty": 3},

    {"scenario": "Two sailing vessels approach each other. Vessel A has wind on the port side, vessel B has wind on the starboard side. Who gives way?",
     "answer": "Vessel A (wind on port side) gives way to Vessel B (wind on starboard side) (Rule 12a(i)). Port tack gives way to starboard tack.",
     "rule": "Rule 12(a)", "category": "encounters", "difficulty": 2},

    {"scenario": "You see a masthead light, red sidelight, and a yellow towing light above a sternlight. Bearing steady. What situation?",
     "answer": "Vessel towing — crossing situation. Assess the tow length (look for diamond shape or three masthead lights). Apply Rule 15 if target on starboard side. The tow may extend well behind the towing vessel.",
     "rule": "Rule 15/24", "category": "encounters", "difficulty": 3},

    # ── SOUND SIGNALS — MANEUVERING (Rule 34) ────────────────────────

    {"scenario": "You hear ONE SHORT blast from a vessel in sight.",
     "answer": "I am altering my course to STARBOARD (Rule 34a).",
     "rule": "Rule 34(a)", "category": "sound_signals_maneuvering", "difficulty": 1},

    {"scenario": "You hear TWO SHORT blasts from a vessel in sight.",
     "answer": "I am altering my course to PORT (Rule 34a).",
     "rule": "Rule 34(a)", "category": "sound_signals_maneuvering", "difficulty": 1},

    {"scenario": "You hear THREE SHORT blasts from a vessel in sight.",
     "answer": "I am operating ASTERN propulsion (Rule 34a). Note: this does not necessarily mean the vessel is moving astern.",
     "rule": "Rule 34(a)", "category": "sound_signals_maneuvering", "difficulty": 1},

    {"scenario": "You hear FIVE or more SHORT RAPID blasts.",
     "answer": "DANGER signal (Rule 34d). The signalling vessel doubts whether sufficient action is being taken to avoid collision. Use it earlier than you think.",
     "rule": "Rule 34(d)", "category": "sound_signals_maneuvering", "difficulty": 1},

    {"scenario": "In a narrow channel, you hear TWO PROLONGED + ONE SHORT blast from a vessel astern.",
     "answer": "I intend to overtake you on YOUR STARBOARD side (Rule 34c(i)). If you agree, sound one prolonged + one short + one prolonged + one short.",
     "rule": "Rule 34(c)", "category": "sound_signals_maneuvering", "difficulty": 2},

    {"scenario": "In a narrow channel, you hear TWO PROLONGED + TWO SHORT blasts from a vessel astern.",
     "answer": "I intend to overtake you on YOUR PORT side (Rule 34c(i)). If you agree, sound one prolonged + one short + one prolonged + one short.",
     "rule": "Rule 34(c)", "category": "sound_signals_maneuvering", "difficulty": 2},

    {"scenario": "A vessel approaching a bend in a narrow channel where she cannot see oncoming traffic sounds what signal?",
     "answer": "ONE PROLONGED blast (Rule 34e). Any approaching vessel that hears the signal around the bend must respond with one prolonged blast.",
     "rule": "Rule 34(e)", "category": "sound_signals_maneuvering", "difficulty": 2},

    {"scenario": "What is the definition of a 'short blast' and a 'prolonged blast'?",
     "answer": "Short blast: about 1 second duration. Prolonged blast: 4 to 6 seconds duration (Rule 32).",
     "rule": "Rule 32", "category": "sound_signals_maneuvering", "difficulty": 1},

    # ── SOUND SIGNALS — FOG (Rule 35) ────────────────────────────────

    {"scenario": "In fog, you hear ONE PROLONGED blast every 2 minutes.",
     "answer": "Power-driven vessel making way through the water (Rule 35a).",
     "rule": "Rule 35(a)", "category": "sound_signals_fog", "difficulty": 1},

    {"scenario": "In fog, you hear TWO PROLONGED blasts every 2 minutes.",
     "answer": "Power-driven vessel underway but STOPPED — not making way through the water (Rule 35b).",
     "rule": "Rule 35(b)", "category": "sound_signals_fog", "difficulty": 1},

    {"scenario": "In fog, you hear ONE PROLONGED + TWO SHORT blasts every 2 minutes.",
     "answer": "NUC, RAM, CBD, sailing vessel, fishing vessel, or vessel towing (Rule 35c). Any vessel not under power or restricted.",
     "rule": "Rule 35(c)", "category": "sound_signals_fog", "difficulty": 1},

    {"scenario": "In fog, you hear ONE PROLONGED + THREE SHORT blasts every 2 minutes.",
     "answer": "Vessel being TOWED (Rule 35d). If manned, sounds this signal immediately after the towing vessel's signal.",
     "rule": "Rule 35(d)", "category": "sound_signals_fog", "difficulty": 2},

    {"scenario": "In fog, you hear rapid ringing of a BELL for 5 seconds every minute.",
     "answer": "Vessel at anchor, less than 100m (Rule 35g). Bell rung rapidly for about 5 seconds at intervals of not more than one minute.",
     "rule": "Rule 35(g)", "category": "sound_signals_fog", "difficulty": 2},

    {"scenario": "In fog, you hear a BELL forward followed by a GONG aft.",
     "answer": "Vessel at anchor, 100m or more (Rule 35g). Bell rung forward, gong sounded aft, at intervals of not more than one minute.",
     "rule": "Rule 35(g)", "category": "sound_signals_fog", "difficulty": 2},

    {"scenario": "In fog, you hear rapid ringing of a bell + three distinct strokes before and after.",
     "answer": "Vessel AGROUND (Rule 35h). Three separate and distinct strokes of the bell before and after the rapid bell ringing.",
     "rule": "Rule 35(h)", "category": "sound_signals_fog", "difficulty": 3},

    {"scenario": "A vessel under 12m in fog — what sound signal is required?",
     "answer": "Not obliged to sound signals of Rule 35(a-h) but must make some other efficient sound signal at intervals of not more than 2 minutes (Rule 35i).",
     "rule": "Rule 35(i)", "category": "sound_signals_fog", "difficulty": 2},

    {"scenario": "What sound equipment is required for vessels 12m-100m? Over 100m?",
     "answer": "12m-100m: whistle and bell. Over 100m: whistle, bell, AND gong. Under 12m: any means of making an efficient sound signal (Rule 33).",
     "rule": "Rule 33", "category": "sound_signals_fog", "difficulty": 2},

    # ── RESTRICTED VISIBILITY (Rule 19) ───────────────────────────────

    {"scenario": "You detect a target on radar forward of the beam in restricted visibility. Can you alter to port?",
     "answer": "NO — avoid altering course to PORT for a vessel detected forward of the beam, except when overtaking (Rule 19d(i)). This is the key trap in restricted visibility.",
     "rule": "Rule 19(d)", "category": "restricted_visibility", "difficulty": 2},

    {"scenario": "In fog, who is the stand-on vessel and who is give-way?",
     "answer": "NEITHER. In restricted visibility (Rule 19), there is NO stand-on or give-way vessel. Rules 11-18 do NOT apply when vessels cannot see each other. Every vessel must take avoiding action.",
     "rule": "Rule 19", "category": "restricted_visibility", "difficulty": 1},

    {"scenario": "You detect a target on radar abeam or abaft the beam in restricted visibility. What action?",
     "answer": "Avoid altering course TOWARD the vessel (Rule 19d(ii)). You may alter away or reduce speed.",
     "rule": "Rule 19(d)", "category": "restricted_visibility", "difficulty": 2},

    {"scenario": "Fog rolls in suddenly. Visibility drops to 0.5nm. What are your mandatory actions?",
     "answer": "Reduce to safe speed (Rule 6). Sound fog signals every 2 min (Rule 35). Post extra lookout. Radar watch — Rule 19 applies. Consider anchoring in safe water.",
     "rule": "Rule 19/6/35", "category": "restricted_visibility", "difficulty": 1},

    {"scenario": "In restricted visibility, you hear a fog signal apparently forward of the beam. No radar contact. What do you do?",
     "answer": "Reduce speed to bare minimum (Rule 19e). If necessary, take all way off. Navigate with extreme caution until the danger of collision is over.",
     "rule": "Rule 19(e)", "category": "restricted_visibility", "difficulty": 2},

    {"scenario": "You are using GPS speed in restricted visibility to assess risk of collision with a radar target. Is this correct?",
     "answer": "NO. GPS speed shows speed over ground — it does not account for current. Use RADAR or AIS for relative assessment. Compass bearing change is the primary indicator of risk of collision (Rule 7).",
     "rule": "Rule 7", "category": "restricted_visibility", "difficulty": 3},

    {"scenario": "What factors determine safe speed in restricted visibility?",
     "answer": "Rule 6(b): radar characteristics and limitations, sea state, traffic density, stopping distance at current speed, and the ability to detect targets by radar. If you cannot stop in half the visible distance, speed is too fast.",
     "rule": "Rule 6(b)", "category": "restricted_visibility", "difficulty": 2},

    # ── TRAFFIC SEPARATION SCHEMES (Rule 10) ─────────────────────────

    {"scenario": "You are crossing a Traffic Separation Scheme. At what angle should you cross?",
     "answer": "As nearly as practicable at RIGHT ANGLES to the general direction of traffic flow (Rule 10c). This minimizes time in the lane.",
     "rule": "Rule 10(c)", "category": "tss", "difficulty": 1},

    {"scenario": "You are joining a TSS. How should you enter the traffic lane?",
     "answer": "Join or leave at the termination of a lane, or at as small an angle as practicable if joining/leaving from the side (Rule 10b(iii)).",
     "rule": "Rule 10(b)", "category": "tss", "difficulty": 2},

    {"scenario": "Can a fishing vessel fish inside a TSS traffic lane?",
     "answer": "Fishing vessels shall not impede the passage of any vessel following a traffic lane (Rule 10i). They may fish, but must not impede through-traffic.",
     "rule": "Rule 10(i)", "category": "tss", "difficulty": 2},

    {"scenario": "Can a vessel under 20m use the traffic lanes of a TSS?",
     "answer": "Vessels under 20m and sailing vessels shall not impede safe passage of power-driven vessels following a traffic lane (Rule 10j). They may use inshore traffic zones.",
     "rule": "Rule 10(j)", "category": "tss", "difficulty": 2},

    {"scenario": "Where should you avoid anchoring in relation to a TSS?",
     "answer": "Avoid anchoring in a traffic separation scheme or in areas near its terminations (Rule 10k).",
     "rule": "Rule 10(k)", "category": "tss", "difficulty": 1},

    {"scenario": "You are in the inshore traffic zone of a TSS. Who has priority?",
     "answer": "Inshore traffic zones are for coastal traffic, vessels under 20m, sailing vessels, and fishing vessels. Through traffic should use the TSS lanes, not the inshore zone (Rule 10d).",
     "rule": "Rule 10(d)", "category": "tss", "difficulty": 2},

    {"scenario": "You must cross a TSS. Can you navigate along the separation zone between the lanes?",
     "answer": "Normally NO — do not navigate in the separation zone (Rule 10e). Exceptions: crossing, joining/leaving at termination, fishing within the separation zone, emergencies, or avoiding immediate danger.",
     "rule": "Rule 10(e)", "category": "tss", "difficulty": 3},

    # ── NARROW CHANNELS (Rule 9) ─────────────────────────────────────

    {"scenario": "You are navigating in a narrow channel. Which side should you keep to?",
     "answer": "Keep as near to the outer limit of the channel on your STARBOARD side as is safe and practicable (Rule 9a).",
     "rule": "Rule 9(a)", "category": "narrow_channels", "difficulty": 1},

    {"scenario": "A vessel under 20m is in a narrow channel. Does she have right of way over larger vessels?",
     "answer": "NO. Vessels under 20m shall NOT impede the passage of a vessel which can safely navigate only within a narrow channel (Rule 9b).",
     "rule": "Rule 9(b)", "category": "narrow_channels", "difficulty": 1},

    {"scenario": "A sailing vessel is in a narrow channel with a large tanker approaching. Who gives way?",
     "answer": "The sailing vessel shall NOT impede the passage of a vessel which can safely navigate only within the channel (Rule 9b). The normal hierarchy (Rule 18) is overridden by Rule 9.",
     "rule": "Rule 9(b)", "category": "narrow_channels", "difficulty": 2},

    {"scenario": "A fishing vessel is operating in a narrow channel. Must she give way to through-traffic?",
     "answer": "YES. Fishing vessels shall NOT impede the passage of any other vessel navigating within a narrow channel (Rule 9c).",
     "rule": "Rule 9(c)", "category": "narrow_channels", "difficulty": 2},

    {"scenario": "You want to overtake another vessel in a narrow channel. The channel is too narrow to pass safely without the other vessel's cooperation. What do you do?",
     "answer": "Sound the appropriate signal: 2 prolonged + 1 short (overtake on your starboard) or 2 prolonged + 2 short (overtake on your port). The other vessel, if in agreement, sounds 1 prolonged + 1 short + 1 prolonged + 1 short (Rule 9e/34c).",
     "rule": "Rule 9(e)", "category": "narrow_channels", "difficulty": 2},

    {"scenario": "You are approaching a bend in a narrow channel where you cannot see oncoming traffic. What do you do?",
     "answer": "Navigate with particular alertness and caution. Sound ONE PROLONGED blast. Any vessel approaching from around the bend must answer with one prolonged blast (Rule 9f/34e).",
     "rule": "Rule 9(f)", "category": "narrow_channels", "difficulty": 2},

    {"scenario": "Can you anchor in a narrow channel?",
     "answer": "Avoid anchoring in a narrow channel if possible (Rule 9g). Only anchor if forced by emergency or to render assistance.",
     "rule": "Rule 9(g)", "category": "narrow_channels", "difficulty": 1},

    # ── GENERAL RULES (Rules 2-8) ────────────────────────────────────

    {"scenario": "What is the 'Golden Rule' of COLREGS?",
     "answer": "Rule 2 — Responsibility. Nothing in the rules exonerates a vessel from the consequences of any neglect. May depart from the rules to avoid IMMEDIATE danger.",
     "rule": "Rule 2", "category": "general_rules", "difficulty": 1},

    {"scenario": "How do you determine if risk of collision exists?",
     "answer": "Rule 7: If the compass bearing of an approaching vessel does NOT appreciably change, risk of collision exists. If in doubt, assume risk EXISTS. Use all available means: radar, AIS, visual bearings.",
     "rule": "Rule 7", "category": "general_rules", "difficulty": 1},

    {"scenario": "What makes an alteration of course 'substantial' enough to be effective?",
     "answer": "Rule 8: avoid small, successive course changes (2-5°) — they are imperceptible to other vessels and dangerous. Aim for changes of 30° or more if sea room allows. Action must be positive, in ample time, and readily apparent.",
     "rule": "Rule 8", "category": "general_rules", "difficulty": 2},

    {"scenario": "What constitutes 'safe speed'?",
     "answer": "Rule 6: speed that allows effective action to avoid collision and to stop within appropriate distance. Factors: visibility, traffic density, manoeuvrability, sea state, draught, radar limitations. If unable to stop in half the visible distance, too fast.",
     "rule": "Rule 6", "category": "general_rules", "difficulty": 1},

    {"scenario": "Rule 5 requires a proper lookout. What does 'by all available means' include?",
     "answer": "Sight, hearing, radar, ARPA, AIS, and any other means appropriate to the prevailing circumstances. Failure to use all available means is a critical operational error.",
     "rule": "Rule 5", "category": "general_rules", "difficulty": 1},

    {"scenario": "You are the give-way vessel in a crossing situation. What does 'early and substantial action' mean?",
     "answer": "Rule 16: take action early enough so that the other vessel can see you are taking action, and make an alteration large enough to be readily apparent on radar. A course change of 30°+ is preferred. Do not make small successive changes.",
     "rule": "Rule 16", "category": "general_rules", "difficulty": 2},

    {"scenario": "When may you depart from the rules of COLREGS?",
     "answer": "Rule 2(b): to avoid IMMEDIATE danger. Also, local regulations (harbour rules, VTS instructions) may override certain rules. But general departure from the rules requires immediate danger to life or vessel.",
     "rule": "Rule 2(b)", "category": "general_rules", "difficulty": 2},

    {"scenario": "You plan an alteration to avoid a vessel, but it would bring you close to a third vessel. What does Rule 8 say?",
     "answer": "Rule 8(d): action taken to avoid collision shall not result in another close-quarters situation. Check that your action does not create a new risk with another vessel.",
     "rule": "Rule 8(d)", "category": "general_rules", "difficulty": 3},

    # ── RESPONSIBILITIES (Rule 18 hierarchy) ──────────────────────────

    {"scenario": "A power-driven vessel meets a sailing vessel in open water. Who gives way?",
     "answer": "The power-driven vessel gives way (Rule 18a). Sailing vessels are higher in the hierarchy than power-driven vessels.",
     "rule": "Rule 18(a)", "category": "responsibilities", "difficulty": 1},

    {"scenario": "A sailing vessel meets a vessel displaying ball-diamond-ball. Who gives way?",
     "answer": "The sailing vessel gives way. Ball-diamond-ball = RAM (Restricted in Ability to Manoeuvre). RAM is higher in the hierarchy: NUC > RAM > CBD > Fishing > Sailing > Power-driven (Rule 18).",
     "rule": "Rule 18", "category": "responsibilities", "difficulty": 2},

    {"scenario": "A fishing vessel meets a NUC vessel. Who gives way?",
     "answer": "The fishing vessel gives way. NUC is at the top of the hierarchy. NUC > RAM > CBD > Fishing > Sailing > Power-driven (Rule 18).",
     "rule": "Rule 18", "category": "responsibilities", "difficulty": 1},

    {"scenario": "What is the full Rule 18 hierarchy from most privileged to least?",
     "answer": "NUC (Not Under Command) > RAM (Restricted in Ability to Manoeuvre) > CBD (Constrained by Draught) > Fishing > Sailing > Power-driven > WIG craft. Remember: NRC FSP.",
     "rule": "Rule 18", "category": "responsibilities", "difficulty": 1},

    {"scenario": "A vessel constrained by draught (CBD) meets a fishing vessel. Who gives way?",
     "answer": "The fishing vessel gives way. CBD is higher in the hierarchy than fishing (Rule 18c). However, CBD status only applies in certain waters.",
     "rule": "Rule 18(c)", "category": "responsibilities", "difficulty": 2},

    {"scenario": "Does the Rule 18 hierarchy apply in a narrow channel when a sailing vessel meets a large tanker?",
     "answer": "NO — Rule 9(b) overrides Rule 18 in narrow channels. The sailing vessel shall NOT impede a vessel that can safely navigate only within the channel, regardless of the hierarchy.",
     "rule": "Rule 9(b)/18", "category": "responsibilities", "difficulty": 3},

    {"scenario": "Does the Rule 18 hierarchy apply in restricted visibility?",
     "answer": "NO — Rule 19 replaces Rules 11-18 when vessels cannot see each other. There is no stand-on or give-way. All vessels must take avoiding action based on radar information.",
     "rule": "Rule 19", "category": "responsibilities", "difficulty": 2},

    {"scenario": "A power-driven vessel displays two red all-round lights vertically AND is in a TSS lane. Do you give way?",
     "answer": "YES — NUC (two red lights) is the highest in the hierarchy. Even in a TSS, you must keep clear of a NUC vessel. However, if you can only navigate safely within the lane, navigate with caution.",
     "rule": "Rule 18(a)", "category": "responsibilities", "difficulty": 3},

    {"scenario": "A seaplane is taxiing on the water. What rules apply?",
     "answer": "Rule 18(e)/31: Seaplanes shall keep well clear of all vessels and avoid impeding their navigation. Must comply with Rules as closely as possible. WIG craft operating on the surface = power-driven vessel.",
     "rule": "Rule 18(e)/31", "category": "responsibilities", "difficulty": 3},
]
