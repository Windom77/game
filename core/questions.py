"""
Question pool and scripted responses for the Victorian Murder Mystery game.
Phase 1: Choice-based gameplay with deterministic clue discovery.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class QuestionCategory(Enum):
    """Categories of questions."""
    GENERIC = "generic"      # Available to all suspects
    SPECIFIC = "specific"    # Targeted at one suspect
    UNLOCKABLE = "unlockable"  # Appears after certain clues discovered


@dataclass
class Question:
    """Represents a question the detective can ask."""
    id: str
    text: str
    category: QuestionCategory
    target_suspects: list[str]  # Which suspects can be asked this (empty = all)
    unlock_requires: list[str] = field(default_factory=list)  # Clue IDs required to unlock
    is_active: bool = True  # Whether currently available

    def can_ask(self, suspect_id: str, discovered_clues: set[str]) -> bool:
        """Check if this question can be asked to a specific suspect."""
        # Check if question targets this suspect (empty = all)
        if self.target_suspects and suspect_id not in self.target_suspects:
            return False
        # Check unlock requirements
        if self.unlock_requires:
            if not all(clue in discovered_clues for clue in self.unlock_requires):
                return False
        return self.is_active


@dataclass
class Response:
    """A scripted response from a suspect."""
    text: str
    clues_revealed: list[str]  # Clue IDs this response reveals
    unlocks_questions: list[str] = field(default_factory=list)  # Question IDs this unlocks


# All questions in the game
QUESTIONS: dict[str, Question] = {
    # === GENERIC QUESTIONS (Available to all) ===
    "Q_WHEREABOUTS": Question(
        id="Q_WHEREABOUTS",
        text="Where were you between 10 PM and 11 PM last night?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),
    "Q_SEE_UNUSUAL": Question(
        id="Q_SEE_UNUSUAL",
        text="Did you hear or see anything unusual last night?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),
    "Q_RELATIONSHIP_VICTIM": Question(
        id="Q_RELATIONSHIP_VICTIM",
        text="What was your relationship with Lord Pemberton?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),
    "Q_ENEMIES": Question(
        id="Q_ENEMIES",
        text="Do you know of anyone who wished Lord Pemberton harm?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),
    "Q_LAST_SEEN": Question(
        id="Q_LAST_SEEN",
        text="When did you last see the victim alive?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),
    "Q_ALIBI_WITNESS": Question(
        id="Q_ALIBI_WITNESS",
        text="Can anyone verify your whereabouts during the murder?",
        category=QuestionCategory.GENERIC,
        target_suspects=[]
    ),

    # === MAJOR THORNTON QUESTIONS ===
    "Q_MAJOR_CRIMEA": Question(
        id="Q_MAJOR_CRIMEA",
        text="Tell me about your Crimean service, Major.",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"]
    ),
    "Q_MAJOR_WEAPON": Question(
        id="Q_MAJOR_WEAPON",
        text="Is this letter opener yours, Major?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"]
    ),
    "Q_MAJOR_ARGUMENT": Question(
        id="Q_MAJOR_ARGUMENT",
        text="I understand you argued with Lord Pemberton earlier today?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"]
    ),
    "Q_MAJOR_DEBT": Question(
        id="Q_MAJOR_DEBT",
        text="What was this debt Lord Pemberton mentioned?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"],
        unlock_requires=["ARGUMENT_MAJOR"]
    ),
    "Q_MAJOR_SMOKING_ROOM": Question(
        id="Q_MAJOR_SMOKING_ROOM",
        text="Where exactly were you seated in the smoking room?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"]
    ),
    "Q_MAJOR_LEFT_ROOM": Question(
        id="Q_MAJOR_LEFT_ROOM",
        text="Did you leave the smoking room at any point that evening?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["major"]
    ),

    # === LADY ASHWORTH QUESTIONS ===
    "Q_LADY_BUSINESS": Question(
        id="Q_LADY_BUSINESS",
        text="What business did you have with Lord Pemberton, Lady Ashworth?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"]
    ),
    "Q_LADY_FINANCIAL": Question(
        id="Q_LADY_FINANCIAL",
        text="Lady Ashworth, are you in financial difficulty?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"]
    ),
    "Q_LADY_DEMANDS": Question(
        id="Q_LADY_DEMANDS",
        text="What exactly were Lord Pemberton's 'demands' of you?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"],
        unlock_requires=["MOTIVE_LADY_DEBT"]
    ),
    "Q_LADY_AFTER_CLARA": Question(
        id="Q_LADY_AFTER_CLARA",
        text="Where did you go after dismissing Clara at 10:45?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"],
        unlock_requires=["ALIBI_LADY_GAP"]
    ),
    "Q_LADY_CORRIDOR": Question(
        id="Q_LADY_CORRIDOR",
        text="Were you in the library corridor last night, Lady Ashworth?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"],
        unlock_requires=["CORRIDOR_LADY"]
    ),
    "Q_LADY_DISTRESSED": Question(
        id="Q_LADY_DISTRESSED",
        text="Why were you seen looking distressed near the library?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["lady"],
        unlock_requires=["DISTRESSED_LADY"]
    ),

    # === CLARA QUESTIONS ===
    "Q_CLARA_TIME_LEFT": Question(
        id="Q_CLARA_TIME_LEFT",
        text="Clara, what time did you leave Lady Ashworth last night?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"]
    ),
    "Q_CLARA_AFTER_LADY": Question(
        id="Q_CLARA_AFTER_LADY",
        text="Where did you go after leaving her Ladyship?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"]
    ),
    "Q_CLARA_CORRIDORS": Question(
        id="Q_CLARA_CORRIDORS",
        text="Did you see anyone in the corridors that night?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"]
    ),
    "Q_CLARA_SAW_LADY": Question(
        id="Q_CLARA_SAW_LADY",
        text="What exactly did you see Lady Ashworth doing in the corridor?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"],
        unlock_requires=["WITNESS_CLARA"]
    ),
    "Q_CLARA_CARRYING": Question(
        id="Q_CLARA_CARRYING",
        text="Was her Ladyship carrying anything when you saw her?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"],
        unlock_requires=["WITNESS_CLARA"]
    ),
    "Q_CLARA_DEMEANOR": Question(
        id="Q_CLARA_DEMEANOR",
        text="How did Lady Ashworth appear when you saw her?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["maid"],
        unlock_requires=["CORRIDOR_LADY"]
    ),

    # === THOMAS QUESTIONS ===
    "Q_THOMAS_EVENING": Question(
        id="Q_THOMAS_EVENING",
        text="Mr. Whitmore, what were you doing last night?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"]
    ),
    "Q_THOMAS_CLARA": Question(
        id="Q_THOMAS_CLARA",
        text="Tell me about your relationship with Clara.",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"]
    ),
    "Q_THOMAS_CONFRONTATION": Question(
        id="Q_THOMAS_CONFRONTATION",
        text="Did you have words with Lord Pemberton recently?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"]
    ),
    "Q_THOMAS_UPSET": Question(
        id="Q_THOMAS_UPSET",
        text="What did Lord Pemberton do to upset you so?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"],
        unlock_requires=["CONFRONTATION_THOMAS"]
    ),
    "Q_THOMAS_CONFIRM_CLARA": Question(
        id="Q_THOMAS_CONFIRM_CLARA",
        text="Can Clara confirm she was with you that night?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"]
    ),
    "Q_THOMAS_OTHERS": Question(
        id="Q_THOMAS_OTHERS",
        text="Did you see anyone else in the halls that night?",
        category=QuestionCategory.SPECIFIC,
        target_suspects=["student"]
    ),
}


# Responses for each question-suspect pair
# Key format: "{question_id}_{suspect_id}"
RESPONSES: dict[str, Response] = {
    # === MAJOR THORNTON RESPONSES ===
    "Q_WHEREABOUTS_major": Response(
        text="I was in the smoking room, Inspector. Reading correspondence from an old regiment comrade. From around ten o'clock until... well, until the commotion started. I was alone, I'm afraid. Not much of an alibi, is it?",
        clues_revealed=["ALIBI_MAJOR_WEAK", "ALIBI_MAJOR_TIME"],
        unlocks_questions=[]
    ),
    "Q_SEE_UNUSUAL_major": Response(
        text="Nothing, Inspector. The smoking room is at the far end of the house. I heard nothing until the servants raised the alarm. Blast it all, if I'd been closer perhaps I could have stopped this villainy.",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_RELATIONSHIP_VICTIM_major": Response(
        text="Pemberton and I go back decades. We were acquaintances in our youth, though I confess our relationship had grown... strained of late. A matter of business, nothing more.",
        clues_revealed=[],
        unlocks_questions=["Q_MAJOR_ARGUMENT"]
    ),
    "Q_ENEMIES_major": Response(
        text="Lord Pemberton was not a man who inspired affection, Inspector. His business dealings left many aggrieved. I couldn't name names, but he had his share of enemies. Perhaps look to his financial records.",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_LAST_SEEN_major": Response(
        text="I saw him briefly at dinner, around eight o'clock. We exchanged a few words - civil enough. After that, I retired to the smoking room and did not see him again. Not alive, at any rate.",
        clues_revealed=["TIME_OF_DEATH"],
        unlocks_questions=[]
    ),
    "Q_ALIBI_WITNESS_major": Response(
        text="*shifts uncomfortably* No, Inspector, I cannot. I was alone in the smoking room the entire time. A soldier learns to enjoy his own company, you understand. I realize how that looks.",
        clues_revealed=["ALIBI_MAJOR_WEAK"],
        unlocks_questions=[]
    ),
    "Q_MAJOR_CRIMEA_major": Response(
        text="The Crimean campaign? I served at Sevastopol, Inspector. Dark days. I saw things no man should see. But I came out with my honour intact and a few mementos. That letter opener among them.",
        clues_revealed=["WEAPON_MAJOR"],
        unlocks_questions=["Q_MAJOR_WEAPON"]
    ),
    "Q_MAJOR_WEAPON_major": Response(
        text="*face drains of color* Yes... yes, that is mine. A Turkish officer's blade, taken at the siege. But I swear to you, Inspector, I did not use it for... for that. It was on the mantelpiece last I saw it!",
        clues_revealed=["WEAPON_MAJOR"],
        unlocks_questions=[]
    ),
    "Q_MAJOR_ARGUMENT_major": Response(
        text="*stiffens* You know about that, do you? Yes, we had words. The man was holding an old debt over my head, threatening to make it public. It would have ruined me. But I did NOT kill him!",
        clues_revealed=["ARGUMENT_MAJOR"],
        unlocks_questions=["Q_MAJOR_DEBT"]
    ),
    "Q_MAJOR_DEBT_major": Response(
        text="Twenty years ago, Pemberton lent me money to save my family estate. I've paid him back tenfold, but he kept the original note. Said he'd tell everyone I was once a debtor. For a man of my standing... it would be devastating.",
        clues_revealed=["ARGUMENT_MAJOR"],
        unlocks_questions=[]
    ),
    "Q_MAJOR_SMOKING_ROOM_major": Response(
        text="The leather chair by the fire, Inspector. It's my customary spot. I had my dispatches, a glass of brandy. One can verify the empty decanter if you wish. I did not move from that chair.",
        clues_revealed=["ALIBI_MAJOR_WEAK"],
        unlocks_questions=[]
    ),
    "Q_MAJOR_LEFT_ROOM_major": Response(
        text="I... no. No, I did not leave. *tugs at collar* Well, perhaps briefly to use the facilities. But I was gone mere minutes! The library is on the other side of the house entirely.",
        clues_revealed=["ALIBI_MAJOR_WEAK"],
        unlocks_questions=[]
    ),

    # === LADY ASHWORTH RESPONSES ===
    "Q_WHEREABOUTS_lady": Response(
        text="I was reviewing correspondence with my maid Clara until approximately quarter to eleven. Then I retired to my chambers. I was exhausted from the journey here, Inspector. I went straight to bed.",
        clues_revealed=["ALIBI_LADY_GAP"],
        unlocks_questions=["Q_LADY_AFTER_CLARA"]
    ),
    "Q_SEE_UNUSUAL_lady": Response(
        text="Nothing, Inspector. My chambers are in the east wing, quite removed from the library. I heard nothing until Clara woke me with the dreadful news. *dabs eyes with handkerchief*",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_RELATIONSHIP_VICTIM_lady": Response(
        text="Lord Pemberton was an old friend of my late husband's. He offered to help me with certain... financial matters after Lord Ashworth's passing. We had a business arrangement, nothing more.",
        clues_revealed=["MOTIVE_LADY_DEBT"],
        unlocks_questions=["Q_LADY_FINANCIAL"]
    ),
    "Q_ENEMIES_lady": Response(
        text="Lord Pemberton was not beloved, Inspector. His business practices were... ruthless. I couldn't say who specifically might wish him harm, but a man like that makes many enemies over a lifetime.",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_LAST_SEEN_lady": Response(
        text="At dinner, Inspector. We spoke briefly. He was in good spirits, discussing some investment or another. I excused myself early, pleading fatigue. That was around nine o'clock.",
        clues_revealed=["TIME_OF_DEATH"],
        unlocks_questions=[]
    ),
    "Q_ALIBI_WITNESS_lady": Response(
        text="Clara was with me until 10:45. After that... *hesitates* I was in my chambers, alone. Preparing for bed. Surely you cannot expect a lady to have a witness while she undresses, Inspector.",
        clues_revealed=["ALIBI_LADY_GAP", "ALIBI_CLARA"],
        unlocks_questions=[]
    ),
    "Q_LADY_BUSINESS_lady": Response(
        text="*ice creeps into voice* Financial matters, Inspector. My late husband left certain debts. Lord Pemberton offered assistance. The specific terms are hardly relevant to your murder investigation.",
        clues_revealed=["MOTIVE_LADY_DEBT"],
        unlocks_questions=["Q_LADY_FINANCIAL"]
    ),
    "Q_LADY_FINANCIAL_lady": Response(
        text="*stiffens* You tread on delicate ground, Inspector. But yes, if you must know - the Ashworth estate faces difficulties. Lord Pemberton was in a position to help. Or so I believed.",
        clues_revealed=["MOTIVE_LADY_DEBT"],
        unlocks_questions=["Q_LADY_DEMANDS"]
    ),
    "Q_LADY_DEMANDS_lady": Response(
        text="*turns pale, voice drops* He wanted... he made demands no gentleman should make of a lady. I refused him. And he threatened to... to expose certain correspondence. He would have ruined me completely.",
        clues_revealed=["MOTIVE_LADY_BLACKMAIL"],
        unlocks_questions=[]
    ),
    "Q_LADY_AFTER_CLARA_lady": Response(
        text="*slight hesitation* I told you, Inspector. I retired to my chambers. Changed for bed. Read briefly. Went to sleep. What else would a lady do at such an hour?",
        clues_revealed=["ALIBI_LADY_GAP"],
        unlocks_questions=[]
    ),
    "Q_LADY_CORRIDOR_lady": Response(
        text="*sharp intake of breath* Who told you that? I... I may have stepped out briefly. For some air. The room was stuffy. But I did not go near the library! I swear it!",
        clues_revealed=["CORRIDOR_LADY"],
        unlocks_questions=[]
    ),
    "Q_LADY_DISTRESSED_lady": Response(
        text="*voice trembling* Distressed? I was... I had received upsetting news about my estate. Financial matters. I stepped out to compose myself. That is all! You twist innocent actions into evidence of guilt!",
        clues_revealed=["DISTRESSED_LADY"],
        unlocks_questions=[]
    ),

    # === CLARA RESPONSES ===
    "Q_WHEREABOUTS_maid": Response(
        text="Begging your pardon, sir, I was with her Ladyship until quarter to eleven, helping with her correspondence. Then I... I went to meet someone briefly, sir. Returned to her Ladyship's chambers after eleven.",
        clues_revealed=["ALIBI_CLARA", "ALIBI_LADY_GAP"],
        unlocks_questions=["Q_CLARA_AFTER_LADY"]
    ),
    "Q_SEE_UNUSUAL_maid": Response(
        text="*fidgets nervously* I... well, sir, I did see something. In the corridor, near the library. But I shouldn't say, sir. It's not my place to speak ill of my betters.",
        clues_revealed=["CORRIDOR_LADY"],
        unlocks_questions=["Q_CLARA_CORRIDORS"]
    ),
    "Q_RELATIONSHIP_VICTIM_maid": Response(
        text="I'm just a lady's maid, sir. Lord Pemberton barely acknowledged the likes of me. Though... *lowers voice* he wasn't always kind to the female servants, if you take my meaning, sir.",
        clues_revealed=[],
        unlocks_questions=["Q_THOMAS_CONFRONTATION"]
    ),
    "Q_ENEMIES_maid": Response(
        text="It's not my place to say, sir. But the master wasn't well-liked below stairs. The way he treated people... *shakes head* But I shouldn't speak ill of the dead, sir.",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_LAST_SEEN_maid": Response(
        text="I saw him at dinner, sir, serving with the other staff. He seemed his usual self. Didn't see him after that, sir. I was occupied with her Ladyship.",
        clues_revealed=["TIME_OF_DEATH"],
        unlocks_questions=[]
    ),
    "Q_ALIBI_WITNESS_maid": Response(
        text="Her Ladyship can vouch for me until quarter to eleven, sir. And then... *blushes deeply* Mr. Whitmore can confirm where I was after that. We were together, sir. Talking.",
        clues_revealed=["ALIBI_CLARA", "ALIBI_THOMAS_CLARA", "MEETING_SECRET"],
        unlocks_questions=[]
    ),
    "Q_CLARA_TIME_LEFT_maid": Response(
        text="It was exactly quarter to eleven, sir. I remember because the clock in her Ladyship's sitting room chimed. She dismissed me to retire, she said.",
        clues_revealed=["ALIBI_CLARA", "ALIBI_LADY_GAP"],
        unlocks_questions=[]
    ),
    "Q_CLARA_AFTER_LADY_maid": Response(
        text="*blushes* I went to meet Mr. Whitmore, sir. Thomas. We've been... we're courting, sir. Lady Ashworth doesn't approve, so we meet in secret. In the servants' corridor.",
        clues_revealed=["MEETING_SECRET", "ALIBI_THOMAS_CLARA", "RELATIONSHIP_CLARA_THOMAS"],
        unlocks_questions=["Q_THOMAS_CLARA"]
    ),
    "Q_CLARA_CORRIDORS_maid": Response(
        text="*voice drops to whisper* I saw her Ladyship, sir. Lady Ashworth. In the corridor near the library. It was about ten to eleven. She looked... she looked troubled, sir. And she was hurrying.",
        clues_revealed=["WITNESS_CLARA", "CORRIDOR_LADY"],
        unlocks_questions=["Q_CLARA_SAW_LADY", "Q_CLARA_CARRYING", "Q_CLARA_DEMEANOR"]
    ),
    "Q_CLARA_SAW_LADY_maid": Response(
        text="*wringing hands* She was coming from the direction of the library, sir. Moving quickly, like. Her face was pale as a ghost. She didn't see me - I stepped into an alcove. I didn't want her to know I was meeting Thomas.",
        clues_revealed=["WITNESS_CLARA", "CORRIDOR_LADY", "DISTRESSED_LADY"],
        unlocks_questions=[]
    ),
    "Q_CLARA_CARRYING_maid": Response(
        text="*long pause, then quietly* Yes, sir. She had something in her hand. Something shiny, like. Metal. She was clutching it close. I... I didn't think anything of it at the time, sir. But now...",
        clues_revealed=["SHINY_OBJECT"],
        unlocks_questions=[]
    ),
    "Q_CLARA_DEMEANOR_maid": Response(
        text="*tears forming* Distressed, sir. Terribly distressed. Her hair was coming loose from its pins, which isn't like her Ladyship at all. She's always so proper. And she was breathing hard, like she'd been running.",
        clues_revealed=["DISTRESSED_LADY"],
        unlocks_questions=[]
    ),

    # === THOMAS RESPONSES ===
    "Q_WHEREABOUTS_student": Response(
        text="I was in my room until about quarter to eleven, writing letters home. Then I went to meet Clara - Miss Finch - in the servants' corridor. We spoke until just after eleven, when I returned to my room via the main hall.",
        clues_revealed=["ALIBI_THOMAS_CLARA", "MEETING_SECRET"],
        unlocks_questions=[]
    ),
    "Q_SEE_UNUSUAL_student": Response(
        text="I saw one of the footmen as I passed through the main hall around ten past eleven - he can confirm the time. But nothing unusual, no. I was rather preoccupied with my own thoughts, I confess.",
        clues_revealed=["ALIBI_THOMAS_FOOTMAN"],
        unlocks_questions=[]
    ),
    "Q_RELATIONSHIP_VICTIM_student": Response(
        text="Lord Pemberton was a friend of my father's, which is why I was invited. We were not close. In fact... *jaw tightens* I found his character rather wanting. But that's beside the point.",
        clues_revealed=[],
        unlocks_questions=["Q_THOMAS_CONFRONTATION"]
    ),
    "Q_ENEMIES_student": Response(
        text="A man like Lord Pemberton makes enemies easily. His treatment of those he considered beneath him was... unconscionable. I'm studying law, Inspector - I believe in justice. Someone clearly decided to dispense their own.",
        clues_revealed=[],
        unlocks_questions=[]
    ),
    "Q_LAST_SEEN_student": Response(
        text="At dinner, around eight o'clock. We exchanged unpleasantries, if I'm honest. After that, I kept to myself. I had no desire to spend more time in his company than necessary.",
        clues_revealed=["TIME_OF_DEATH"],
        unlocks_questions=[]
    ),
    "Q_ALIBI_WITNESS_student": Response(
        text="Clara can confirm we were together from quarter to eleven until after eleven. And the footman, James, saw me in the main hall at approximately ten past eleven. My alibi is solid, Inspector.",
        clues_revealed=["ALIBI_THOMAS_CLARA", "ALIBI_THOMAS_FOOTMAN"],
        unlocks_questions=[]
    ),
    "Q_THOMAS_EVENING_student": Response(
        text="I had dinner with the other guests, then retired to compose some letters. Around quarter to eleven, I went to meet Clara. We talked - about our future, about how to tell Lady Ashworth. Then I returned to my room.",
        clues_revealed=["ALIBI_THOMAS_CLARA", "RELATIONSHIP_CLARA_THOMAS"],
        unlocks_questions=[]
    ),
    "Q_THOMAS_CLARA_student": Response(
        text="*smiles despite circumstances* Clara and I are courting, Inspector. I know it's unconventional - a law student and a lady's maid. But I love her, and I intend to marry her. Lady Ashworth disapproves, hence the secrecy.",
        clues_revealed=["RELATIONSHIP_CLARA_THOMAS", "MEETING_SECRET"],
        unlocks_questions=[]
    ),
    "Q_THOMAS_CONFRONTATION_student": Response(
        text="*face darkens* Yes, Inspector. Two days ago. I confronted him about his behavior toward Clara. The man made improper advances toward her. She was too frightened to speak up, so I did.",
        clues_revealed=["CONFRONTATION_THOMAS", "MOTIVE_THOMAS_ANGER"],
        unlocks_questions=["Q_THOMAS_UPSET"]
    ),
    "Q_THOMAS_UPSET_student": Response(
        text="He tried to force himself on Clara! When I confronted him, he laughed. Said no one would believe a student over a lord. Said he'd have me thrown out. I was furious, yes. But I didn't kill him. I was with Clara when it happened.",
        clues_revealed=["MOTIVE_THOMAS_ANGER", "CONFRONTATION_THOMAS"],
        unlocks_questions=[]
    ),
    "Q_THOMAS_CONFIRM_CLARA_student": Response(
        text="Of course she can. We were together in the servants' corridor from 10:45 until just after 11. She was worried about being caught, kept checking the time. She'll confirm it, Inspector.",
        clues_revealed=["ALIBI_THOMAS_CLARA"],
        unlocks_questions=[]
    ),
    "Q_THOMAS_OTHERS_student": Response(
        text="Only the footman, James, when I passed through the main hall around 10 past 11. He was adjusting a lamp. We nodded to each other. Other than that, the halls were empty.",
        clues_revealed=["ALIBI_THOMAS_FOOTMAN"],
        unlocks_questions=[]
    ),
}


def get_question(question_id: str) -> Optional[Question]:
    """Get a question by ID."""
    return QUESTIONS.get(question_id)


def get_response(question_id: str, suspect_id: str) -> Optional[Response]:
    """Get the response for a question-suspect pair."""
    key = f"{question_id}_{suspect_id}"
    return RESPONSES.get(key)


def get_available_questions(suspect_id: str, discovered_clues: set[str], asked_questions: set[str]) -> list[Question]:
    """Get all questions available to ask a specific suspect."""
    available = []
    for q_id, question in QUESTIONS.items():
        # Skip if already asked to this suspect
        if f"{q_id}_{suspect_id}" in asked_questions:
            continue
        # Check if can ask this question
        if question.can_ask(suspect_id, discovered_clues):
            available.append(question)
    return available


def get_all_questions() -> list[Question]:
    """Get all questions in the game."""
    return list(QUESTIONS.values())
