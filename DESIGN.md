# The Pemberton Manor Mystery - Phase 1 Design Document

## Overview

A choice-based murder mystery game where the player (Detective Inspector) questions four suspects to solve the murder of Lord Reginald Pemberton. Strategic question selection determines success.

---

## The Murder

**Victim:** Lord Reginald Pemberton (62)
- Wealthy, cruel manor lord known for ruthless dealings
- Found dead in the library at 11:00 PM
- Cause of death: Stabbed through the heart with an ornate letter opener
- The weapon belonged to Major Thornton (Crimean War memento)

**Time of Death:** Approximately 10:50 PM - 11:00 PM

---

## The Killer

**Lady Cordelia Ashworth** is the murderer.

### Motive
Lord Pemberton promised financial assistance for her failing estate but demanded sexual favors in return. When she refused and secretly tried to sell family secrets to a rival, Pemberton discovered this and threatened to expose her completely. She would lose everything - reputation, estate, social standing.

### Opportunity
- Her alibi ends at 10:45 PM (dismissed Clara)
- Murder occurred at ~10:50 PM
- She was seen by Clara in the library corridor at 10:50 PM
- She returned to her chambers pretending to sleep by 11:15 PM

### Method
- Found Major Thornton's letter opener on a side table in the library
- Used it to kill Pemberton during a confrontation
- Framed it to look like Major Thornton's doing (his weapon, his argument with Pemberton)

---

## Characters

### 1. Major Edmund Thornton (58)
- **Role:** Red Herring (Innocent)
- **Occupation:** Retired Army Officer
- **Personality:** Gruff, honorable, haunted by war
- **Secret:** Argued with Pemberton about old debt that day
- **Alibi:** Smoking room, alone, 10 PM - 11:30 PM (weak - no witnesses)
- **The weapon was his - but he didn't use it**

### 2. Lady Cordelia Ashworth (42)
- **Role:** THE MURDERER
- **Occupation:** Widow, Socialite
- **Personality:** Proud, desperate, manipulative
- **Secret:** Killed Pemberton to prevent ruin
- **Alibi:** With Clara until 10:45 PM, then "retired" (GAP: 10:45-11:15)
- **Motive:** Blackmail prevention, financial desperation

### 3. Clara Finch (19)
- **Role:** Key Witness (Innocent)
- **Occupation:** Lady's Maid
- **Personality:** Observant, loyal, torn between duty and truth
- **Secret:** Saw Lady Ashworth at 10:50 PM in corridor, distressed, holding something shiny
- **Alibi:** With Lady until 10:45, met Thomas 10:45-11:05, returned at 11:15
- **Her testimony is crucial to solving the case**

### 4. Thomas Whitmore (23)
- **Role:** Secondary Suspect (Innocent)
- **Occupation:** Law Student
- **Personality:** Idealistic, passionate, naive
- **Secret:** Confronted Pemberton about improper advances toward Clara
- **Alibi:** With Clara 10:45-11:05, seen by footman at 11:10 PM (solid)
- **Motive exists but alibi clears him**

---

## Clue System

### All Clues (20 total)

| ID | Clue | Source | Type |
|----|------|--------|------|
| WEAPON_MAJOR | Letter opener belonged to Major | Major | Physical |
| ARGUMENT_MAJOR | Major argued with Pemberton about debt | Major/Lady | Circumstantial |
| ALIBI_MAJOR_WEAK | Major was alone - no witnesses | Major | Alibi |
| ALIBI_MAJOR_TIME | Major claims 10 PM - 11:30 PM in smoking room | Major | Alibi |
| ALIBI_LADY_GAP | Lady's alibi ends at 10:45 PM | Lady/Clara | Alibi |
| CORRIDOR_LADY | Lady was in library corridor around murder time | Clara | Location |
| MOTIVE_LADY_BLACKMAIL | Pemberton was blackmailing Lady | Lady | Motive |
| MOTIVE_LADY_DEBT | Lady is financially desperate | Lady | Motive |
| SHINY_OBJECT | Clara saw Lady holding something shiny (weapon) | Clara | Physical |
| DISTRESSED_LADY | Lady was distressed when seen by Clara | Clara | Behavioral |
| WITNESS_CLARA | Clara saw Lady near the library at 10:50 PM | Clara | Witness |
| ALIBI_CLARA | Clara was with Lady until 10:45 PM | Clara | Alibi |
| MEETING_SECRET | Thomas and Clara were meeting secretly | Clara/Thomas | Relationship |
| ALIBI_THOMAS_CLARA | Thomas was with Clara 10:45-11:05 PM | Thomas/Clara | Alibi |
| ALIBI_THOMAS_FOOTMAN | Footman saw Thomas at 11:10 PM | Thomas | Alibi |
| CONFRONTATION_THOMAS | Thomas confronted Pemberton about Clara | Thomas | Motive |
| MOTIVE_THOMAS_ANGER | Thomas was furious at Pemberton | Thomas | Motive |
| RELATIONSHIP_CLARA_THOMAS | Clara and Thomas are courting | Clara/Thomas | Relationship |
| LOYALTY_CLARA | Clara is torn about revealing what she saw | Clara | Behavioral |
| TIME_OF_DEATH | Death occurred approximately 10:50-11:00 PM | Any | Timeline |

### Key Clues for Conviction (6 required)

To correctly accuse Lady Ashworth with sufficient evidence:

1. **ALIBI_LADY_GAP** - Establishes opportunity
2. **CORRIDOR_LADY** - Places her at crime scene
3. **WITNESS_CLARA** - Provides witness testimony
4. **SHINY_OBJECT** - Links her to the weapon
5. **MOTIVE_LADY_BLACKMAIL** or **MOTIVE_LADY_DEBT** - Establishes motive
6. **DISTRESSED_LADY** - Shows guilt/awareness

### Win Conditions

- **VICTORY:** Accuse Lady Ashworth with 4+ key clues
- **PARTIAL WIN:** Accuse Lady Ashworth with 2-3 key clues (lucky guess)
- **DEFEAT:** Accuse wrong person OR accuse Lady with <2 key clues

---

## Question Pool (30 Questions)

### Generic Questions (Available to All)
1. "Where were you between 10 PM and 11 PM last night?"
2. "Did you hear or see anything unusual?"
3. "What was your relationship with Lord Pemberton?"
4. "Do you know of anyone who wished him harm?"
5. "When did you last see the victim alive?"
6. "Can anyone verify your whereabouts?"

### Major Thornton Questions
7. "Tell me about your Crimean service, Major."
8. "Is this letter opener yours?" (shows weapon)
9. "I understand you argued with Lord Pemberton today?"
10. "What was this debt Lord Pemberton mentioned?"
11. "Where exactly were you in the smoking room?"
12. "Did you leave the smoking room at any point?"

### Lady Ashworth Questions
13. "What business did you have with Lord Pemberton?"
14. "Lady Ashworth, are you in financial difficulty?"
15. "What were Lord Pemberton's 'demands'?"
16. "Where did you go after dismissing Clara?"
17. "Were you in the library corridor last night?"
18. "Why were you seen looking distressed?"

### Clara Questions
19. "Clara, what time did you leave Lady Ashworth?"
20. "Where did you go after leaving her Ladyship?"
21. "Did you see anyone in the corridors that night?"
22. "What exactly did you see Lady Ashworth doing?"
23. "Was her Ladyship carrying anything?"
24. "How did Lady Ashworth appear when you saw her?"

### Thomas Questions
25. "Mr. Whitmore, what were you doing last night?"
26. "Tell me about your relationship with Clara."
27. "Did you have words with Lord Pemberton recently?"
28. "What did Lord Pemberton do to upset you?"
29. "Can anyone confirm you were with Clara?"
30. "Did you see anyone else in the halls?"

### Unlockable Questions (appear after certain clues)
- Q17 unlocks after CORRIDOR_LADY discovered
- Q23 unlocks after WITNESS_CLARA discovered
- Q18 unlocks after DISTRESSED_LADY discovered
- Q15 unlocks after MOTIVE_LADY_DEBT discovered

---

## Optimal Question Path (12-15 questions)

### Phase 1: Establish Timeline (3-4 questions)
1. Ask Clara Q19 → ALIBI_CLARA, ALIBI_LADY_GAP
2. Ask Thomas Q25 → ALIBI_THOMAS_CLARA
3. Ask Major Q1 (generic) → ALIBI_MAJOR_WEAK

### Phase 2: Identify Witness (3-4 questions)
4. Ask Clara Q21 → CORRIDOR_LADY, WITNESS_CLARA (if pressed)
5. Ask Clara Q22 → WITNESS_CLARA confirmed
6. Ask Clara Q23 (unlocked) → SHINY_OBJECT

### Phase 3: Establish Motive (3-4 questions)
7. Ask Lady Q13 → hints at MOTIVE_LADY_DEBT
8. Ask Lady Q14 → MOTIVE_LADY_DEBT
9. Ask Lady Q15 (unlocked) → MOTIVE_LADY_BLACKMAIL

### Phase 4: Confirm Behavioral Evidence (2-3 questions)
10. Ask Clara Q24 → DISTRESSED_LADY
11. Ask Lady Q17 (unlocked) → defensive response confirms presence

### Final: Make Accusation
- Accuse Lady Ashworth with 6+ key clues = VICTORY

---

## Suboptimal Paths

### Red Herring: Major Thornton
If player focuses on Major:
- Weapon was his → WEAPON_MAJOR
- Argued with victim → ARGUMENT_MAJOR
- Weak alibi → ALIBI_MAJOR_WEAK

But missing: No witness placing him at scene, no motive beyond debt

### Red Herring: Thomas Whitmore
If player focuses on Thomas:
- Had confrontation → CONFRONTATION_THOMAS
- Was angry → MOTIVE_THOMAS_ANGER

But: Solid alibi with Clara AND footman witness → cleared

---

## UI Layout (Pygame)

```
+--------------------------------------------------+
|        THE PEMBERTON MANOR MYSTERY               |
|                                                  |
|  +--------+  +--------+  +--------+  +--------+  |
|  | MAJOR  |  | LADY   |  | CLARA  |  | THOMAS |  |
|  | [1]    |  | [2]    |  | [3]    |  | [4]    |  |
|  +--------+  +--------+  +--------+  +--------+  |
|                                                  |
|  QUESTIONS (12/15 remaining)                     |
|  +--------------------------------------------+  |
|  | 1. Where were you at 10 PM?                |  |
|  | 2. Did you see anything unusual?           |  |
|  | 3. What was your relationship with...      |  |
|  | [↑↓ to scroll, Enter to select]            |  |
|  +--------------------------------------------+  |
|                                                  |
|  EVIDENCE NOTEBOOK (4 clues)                     |
|  +--------------------------------------------+  |
|  | • Major's letter opener was the weapon     |  |
|  | • Lady Ashworth's alibi ends at 10:45 PM   |  |
|  | • Clara saw Lady in corridor at 10:50 PM   |  |
|  | • Lady was holding something shiny         |  |
|  +--------------------------------------------+  |
|                                                  |
|  [A] Make Accusation  [H] Help  [Q] Quit         |
+--------------------------------------------------+
```

---

## Phase 2 Roadmap (LLM Integration)

Once Phase 1 is stable:

1. **Hybrid Questions:** Keep scripted critical clues, allow free-form follow-ups
2. **LLM Responses:** Characters respond naturally while still revealing key info
3. **Dynamic Dialogue:** LLM generates contextual responses based on discovered clues
4. **Conversation Memory:** Characters remember what you've asked them
5. **Emergent Gameplay:** Players can ask questions not in the original pool

---

## Success Metrics

- [ ] Game completes in 5-10 minutes
- [ ] Clear visual feedback on question selection
- [ ] Evidence notebook shows discovered clues
- [ ] Question counter tracks usage (X/15)
- [ ] Deterministic: same questions = same outcome
- [ ] Solvable in 12-15 optimal questions
- [ ] Three distinct endings (Victory, Partial, Defeat)
