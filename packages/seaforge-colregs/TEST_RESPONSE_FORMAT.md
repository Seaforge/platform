# 🧭 Maritime AI Response Format Test Guide

## What Was Changed

All four LLM provider system prompts (Claude, OpenAI, Google, Gemini, Groq) now enforce a **mandatory response format** that ensures structured, concise, actionable answers.

### New Required Format

Every response must follow this exact structure:

```
**[RULE NUMBER OR TOPIC TITLE]**

Action: [One clear sentence: what to do]

Why: [One-line explanation tied to collision avoidance or seamanship]

[Additional context, examples, or edge cases if needed]
```

### Formatting Enforcement

The system prompt now includes:
- **Mandatory bold rule/title** with `**` delimiters
- **Blank line spacing** between sections (Action/Why/Additional)
- **Concise sections**: Action and Why limited to 1-2 sentences max
- **Detailed context** only in the Additional section
- **Visual warnings** using ⚠️ symbol

---

## How to Test

### Step 1: Open the Dashboard
```
Open browser to: http://localhost:5001
Click "🤖 Maritime AI" tab
```

### Step 2: Configure API
1. Click ⚙️ **Settings** (bottom-right)
2. Select your provider: **Claude**, **OpenAI**, **Google**, or **Groq**
3. Enter your API key
4. Click **Save Settings**

### Step 3: Test With These Questions

#### Test 1: COLREGS Rule Question
```
Ask: "Two power-driven vessels meeting head-on at night.
What lights does each vessel see?"
```

**Expected response format:**
```
**Rule 23(a) — Power-Driven Vessel Lights**

Action: Each vessel alters course to starboard to pass port-to-port.

Why: Head-on encounter (Rule 14) requires mutual alteration to avoid collision.

Additional: At night, you'll see two masthead lights in vertical line, sidelights (red port, green starboard), and sternlight. This confirms power-driven vessel per Rule 23(a). If lights are in different vertical pattern, re-assess vessel type.
```

#### Test 2: Seamanship Question
```
Ask: "What's the best way to maintain a safe speed
when visibility drops suddenly to 1 nautical mile?"
```

**Expected response format:**
```
**Rule 6 — Safe Speed**

Action: Reduce speed immediately to half current speed minimum, increase radar scan frequency, sound fog signal.

Why: Safe speed must allow you to stop within half visible distance (Rule 6). At 1nm, this means max 6-8 knots depending on vessel size/turning circle.

Additional: Increase look-out watch rotations. Engine standby. Have anchor ready. Monitor radar for targets. If CPA becomes concerning, alter course 30°+ decisively (not small incremental changes).
```

#### Test 3: Anti-Pattern Warning
```
Ask: "I'm the stand-on vessel in fog.
Should I maintain course and speed?"
```

**Expected response format (with warning):**
```
**Rule 19 — Restricted Visibility (Fog/Darkness)**

Action: NO — alter course decisively BEFORE collision develops.

Why: In restricted visibility, there IS NO stand-on vessel. Rule 19 overrides Rules 13-15. All vessels must avoid collision actively.

Additional: ⚠️ **This is the #1 assumption that kills people.** You may have stand-on role in clear visibility (Rule 14), but fog strips that authority. If you see a target on radar, assume risk of collision exists. Alter course 30°+ EARLY. Call the Master if in any doubt.
```

---

## What You Should See

✅ **Correct Format:**
- Title in bold with rule number
- `Action:` label followed by 1 sentence
- `Why:` label followed by 1 line explanation
- Extra context below with blank line separation
- Warnings flagged with ⚠️
- Clear, concise language (no rambling)
- Each section has distinct purpose

❌ **Incorrect Format (old behavior):**
- No bold titles
- Rambling multi-paragraph responses
- No clear section breaks
- Action mixed with reasoning in one block
- Overly detailed without structure

---

## Testing Checklist

Use this to verify each response:

- [ ] Response starts with **bold rule/title**
- [ ] Blank line after title
- [ ] "Action:" section (1 sentence max)
- [ ] Blank line
- [ ] "Why:" section (1 line explanation)
- [ ] Blank line
- [ ] Additional context (if needed)
- [ ] No rambling paragraphs
- [ ] Citations include rule numbers
- [ ] Warnings flagged with ⚠️

---

## Test All Four Providers

| Provider | Command | Model to Test |
|----------|---------|---|
| **Claude** | Select "Claude" in settings | claude-3-5-sonnet-20241022 |
| **OpenAI** | Select "OpenAI" in settings | gpt-4o |
| **Google** | Select "Google" in settings | gemini-2-5-pro |
| **Groq** | Select "Groq" in settings | mixtral-8x7b-32768 |

Each should follow the same format regardless of provider.

---

## Files Modified

- `/home/arne/projects/seaforge/packages/seaforge-colregs/templates/demo_dashboard.html`
  - Updated `callClaudeAPI()` system prompt (line ~1697)
  - Updated `callOpenAIAPI()` system prompt (line ~1766)
  - Updated `callGoogleAPI()` system prompt (line ~1825)
  - Updated `callGroqAPI()` system prompt (line ~1911)

All system prompts now include:
1. Mandatory response format template
2. Formatting rules with bullet points
3. Critical anti-patterns list with ⚠️ symbols
4. Quality checklist
5. Reference to MARITIME_AI_SOUL.md

---

## Next Steps If Test Fails

If responses don't follow the format:

1. **Check API Key**: Verify key is valid (look for API errors in console)
2. **Check Model Selection**: Some older models ignore system prompts better
3. **Try Different Provider**: Test with Claude first (most reliable)
4. **Check Console**: Browser dev tools (F12) → Console tab for error messages

---

**Last Updated:** 2026-03-28
**Status:** ✅ Ready for testing
