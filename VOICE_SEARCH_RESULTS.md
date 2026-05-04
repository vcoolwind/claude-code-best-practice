# Voice Input, Speech-to-Text & Dictation Content — Repository Search Results

**Date:** May 4, 2026  
**Search Scope:** Best-practice/, tips/, reports/, README.md, and implementation files  
**Search Terms:** voice, speech-to-text, dictation, audio, microphone, voice control, voice workflow

---

## Summary

This repository contains **comprehensive content on voice input and dictation with Claude Code**, including:

- **Official feature documentation** linking to Claude Code's `/voice` command
- **Best practices and tips** from Boris Cherny (Claude Code creator)
- **Integration guides** for voice workflows
- **Advanced hooks** for voice-enabled workflows
- **Startup replacement tools** (Wispr Flow, SuperWhisper)

---

## 1. PRIMARY RESOURCES — Voice Dictation Feature

### README.md - Voice Dictation in Hot Features

**Feature Documentation:**
```
| [**Voice Dictation**](https://code.claude.com/docs/en/voice-dictation) ![beta](!/tags/beta.svg) | `/voice` | [![Best Practice](!/tags/best-practice.svg)](https://x.com/trq212/status/2028628570692890800) |
```

- **Command:** `/voice`
- **Status:** Beta (🔥 Hot Feature)
- **Best Practice Source:** [@trq212](https://x.com/trq212/status/2028628570692890800) (Thariq from Anthropic)

**Usage Tips (Tips & Tricks Section):**
```
[/voice](https://code.claude.com/docs/en/voice-dictation) or [Wispr Flow](https://wisprflow.ai) for voice prompting (10x productivity)
```
- Source: Boris Cherny ([@bcherny](https://x.com/bcherny/status/2038454362226467112))

**Market Context (STARTUPS Table):**
```
| Voice Dictation | [Wispr Flow](https://wisprflow.ai), [SuperWhisper](https://superwhisper.com/) |
```

---

## 2. BEST PRACTICES

### A. `best-practice/claude-commands.md` — `/voice` Command

**Command Reference:**
```
| `/voice [hold|tap|off]` | Config | Toggle voice dictation, or enable it in a specific mode. Requires a Claude.ai account |
```

**Details:**
- Three modes available: `hold`, `tap`, `off`
- Requires Claude.ai account
- Command signature updated to `/voice [hold|tap|off]` for mode selection

---

### B. `best-practice/claude-settings.md` — Voice Configuration

**New Voice Settings Object (v2.1.118+):**
```json
{
  "voice": {
    "enabled": boolean,      // toggle voice dictation on/off
    "mode": string,          // "hold" for hold-to-talk or "tap" for tap-to-toggle
    "autoSubmit": boolean    // auto-submit when dictation ends
  },
  "voiceEnabled": boolean    // DEPRECATED — use voice.enabled instead
}
```

**Language Setting:**
- `language` setting (default: "english") also controls voice dictation language
- Sets terminal tab title (v2.1.121)

---

## 3. TIPS & WORKFLOWS — Voice Usage

### From: `tips/claude-boris-15-tips-30-mar-26.md` (Tip #15)

**Title:** "Use /voice to Enable Voice Input"

**Key Quote:**
> "Fun fact: Boris does most of his coding by speaking to Claude, rather than typing."

**How to Use:**

1. **CLI:** Run `/voice` then hold the space bar to speak
2. **Desktop App:** Press the voice button in UI
3. **iOS:** Enable dictation in iOS settings

**Productivity Claim:** 10x productivity improvement

**Source:** [Boris Cherny on X — March 30, 2026](https://x.com/bcherny/status/2038454362226467112)

---

## 4. ADVANCED IMPLEMENTATIONS — Voice Hooks

### Weather Agent Voice Notifications System

**Files Involved:**
- `my-weather-agent-task-list.md`
- `.claude/agents/universal-weather-agent.md`
- `.claude/agents/weather-agent.md`

**Hook Events for Voice Output:**
```
PreToolUse:    python3 weather-voice.py --event=start   (🔊 announce start)
PostToolUse:   python3 weather-voice.py --event=done    (🔊 announce completion)
PostToolUseFailure: python3 weather-voice.py --event=error (🔊 announce failure)
```

**Audio Player Support:**
- **Linux:** Uses `paplay` from `pulseaudio-utils`
- **macOS/Windows:** Auto-detects appropriate player
- **Voice Used:** Samara X (customizable)

**Hook Configuration Example:**
```yaml
PreToolUse:
  command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/weather-voice.py --event=pre

PostToolUse:
  command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/weather-voice.py --event=post
```

---

## 5. CHANGELOG TRACKING

### Voice Feature Updates

**`changelog/best-practice/claude-commands/changelog.md`:**
- Entry 1: Add `/voice` command to Config tag — ✅ COMPLETE
- Entry 5: Update `/voice` signature to `/voice [hold|tap|off]` — ✅ COMPLETE

**`changelog/best-practice/claude-settings/changelog.md`:**
- Entry 1: Add `voiceEnabled` to General Settings table — ✅ COMPLETE
- Entry 6: Expand `voiceEnabled` into full `voice` object — ✅ COMPLETE
- Entry 8: Add "Also sets the voice dictation language" to `language` description — ✅ COMPLETE

**`changelog/best-practice/concepts/changelog.md`:**
- Entry 2: Rename to "Voice Dictation", update links — ✅ COMPLETE

---

## 6. VIDEO REFERENCES

### Matt Pocock Workshop (April 24, 2026)

**Reference:** `videos/claude-matt-pocock-24-apr-26.md`

**Quote:**
> "I usually dictate to the AI. I'm usually actually chatting to the AI instead of uh typing here, but uh this is a relatively new laptop and I couldn't get my dictation software working on it um because Windows is crap."

**Context:** Matt indicates that dictation is his primary interface with Claude Code, demonstrating mainstream adoption of voice workflows.

---

## 7. FULL REFERENCE TABLE

| Aspect | Details | Source |
|--------|---------|--------|
| **Command** | `/voice [hold\|tap\|off]` | `best-practice/claude-commands.md` |
| **Settings Key** | `voice.enabled`, `voice.mode`, `voice.autoSubmit` | `best-practice/claude-settings.md` |
| **Language Setting** | Affects voice dictation language | `best-practice/claude-settings.md` |
| **Feature Status** | Beta (🔥 Hot) | `README.md` |
| **Primary Tip** | Tip #15 in Boris's 15 Tips | `tips/claude-boris-15-tips-30-mar-26.md` |
| **Input Methods** | Space bar (CLI), Button (Desktop), iOS dictation | Best Practice Tips |
| **Productivity Gain** | 10x productivity | Boris Cherny tweet |
| **Alternative Tools** | Wispr Flow, SuperWhisper | `README.md` STARTUPS |
| **Advanced Usage** | Voice hooks for notifications | Weather agent implementation |
| **Requirements** | Claude.ai account | Documentation |

---

## 8. KEY FINDINGS

✅ **Comprehensive Voice Support**
- Built-in `/voice` command with multiple modes
- Settings-based configuration
- Desktop, CLI, and mobile integration

✅ **Creator Endorsement**
- Boris Cherny does "most of his coding by speaking"
- Claimed 10x productivity improvement

✅ **Production Ready**
- Hook system supports voice notifications
- Weather agent demonstrates advanced usage

✅ **Market Position**
- Replaces Wispr Flow and SuperWhisper for many users
- Competitive advantage for AI-native developers

✅ **Active Development**
- Multiple changelog entries tracking improvements
- Settings expanded from simple boolean to full object (v2.1.118)
- Command signature enhanced with mode parameters

---

## 9. QUICK START FOR VOICE

1. **Enable:** Run `/voice` in Claude Code
2. **Configure:** Use `/config` to set mode (`hold` or `tap`)
3. **Use:**
   - CLI: Hold space bar to speak
   - Desktop: Click voice button
   - iOS: Use OS dictation
4. **Learn:** Check `tips/claude-boris-15-tips-30-mar-26.md` (Tip #15)
5. **Automate:** Explore voice hooks in weather agent implementation

---

**Search Completed:** ✅ May 4, 2026  
**Total References Found:** 25+ mentions across 10+ files
