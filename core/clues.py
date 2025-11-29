"""
Clue system and evidence notebook for the Victorian Murder Mystery game.
Phase 1: Tracks discovered clues and determines win conditions.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ClueCategory(Enum):
    """Categories of clues for organization in the evidence notebook."""
    ALIBI = "alibi"
    MOTIVE = "motive"
    PHYSICAL = "physical"
    WITNESS = "witness"
    BEHAVIORAL = "behavioral"
    TIMELINE = "timeline"
    RELATIONSHIP = "relationship"


@dataclass
class Clue:
    """Represents a discoverable clue."""
    id: str
    name: str  # Short display name
    description: str  # Full description for evidence notebook
    category: ClueCategory
    source_suspect: str  # Who revealed this clue (or "any")
    is_key_evidence: bool = False  # Is this a key clue for conviction?
    points_to: Optional[str] = None  # Suspect this evidence points to (optional)


# All clues in the game
CLUES: dict[str, Clue] = {
    # === MAJOR THORNTON CLUES ===
    "WEAPON_MAJOR": Clue(
        id="WEAPON_MAJOR",
        name="Major's Letter Opener",
        description="The murder weapon - an ornate letter opener - belongs to Major Thornton. A memento from his Crimean War service.",
        category=ClueCategory.PHYSICAL,
        source_suspect="major",
        is_key_evidence=False,
        points_to="major"  # Red herring
    ),
    "ARGUMENT_MAJOR": Clue(
        id="ARGUMENT_MAJOR",
        name="Argument Over Debt",
        description="Major Thornton argued with Lord Pemberton earlier that day about an old debt. Pemberton threatened to ruin him publicly.",
        category=ClueCategory.MOTIVE,
        source_suspect="major",
        is_key_evidence=False,
        points_to="major"  # Red herring
    ),
    "ALIBI_MAJOR_WEAK": Clue(
        id="ALIBI_MAJOR_WEAK",
        name="Major's Weak Alibi",
        description="Major Thornton claims he was alone in the smoking room. No one can verify his whereabouts during the murder.",
        category=ClueCategory.ALIBI,
        source_suspect="major",
        is_key_evidence=False,
        points_to="major"  # Red herring
    ),
    "ALIBI_MAJOR_TIME": Clue(
        id="ALIBI_MAJOR_TIME",
        name="Major's Timeframe",
        description="Major Thornton claims to have been in the smoking room from 10 PM until 11:30 PM.",
        category=ClueCategory.TIMELINE,
        source_suspect="major",
        is_key_evidence=False
    ),

    # === LADY ASHWORTH CLUES ===
    "ALIBI_LADY_GAP": Clue(
        id="ALIBI_LADY_GAP",
        name="Lady's Alibi Gap",
        description="Lady Ashworth's alibi ends at 10:45 PM when she dismissed Clara. Her movements are unaccounted until she was found 'asleep' at 11:15 PM.",
        category=ClueCategory.ALIBI,
        source_suspect="lady",
        is_key_evidence=True,
        points_to="lady"
    ),
    "CORRIDOR_LADY": Clue(
        id="CORRIDOR_LADY",
        name="Lady Near Library",
        description="Lady Ashworth was seen in the corridor near the library around 10:50 PM - close to the time of the murder.",
        category=ClueCategory.WITNESS,
        source_suspect="maid",
        is_key_evidence=True,
        points_to="lady"
    ),
    "MOTIVE_LADY_DEBT": Clue(
        id="MOTIVE_LADY_DEBT",
        name="Lady's Financial Troubles",
        description="Lady Ashworth is in severe financial difficulty. Her late husband left massive debts and she was seeking help from Lord Pemberton.",
        category=ClueCategory.MOTIVE,
        source_suspect="lady",
        is_key_evidence=False,
        points_to="lady"
    ),
    "MOTIVE_LADY_BLACKMAIL": Clue(
        id="MOTIVE_LADY_BLACKMAIL",
        name="Blackmail Motive",
        description="Lord Pemberton made improper demands of Lady Ashworth in exchange for financial help. When she refused and sought help elsewhere, he threatened to expose her.",
        category=ClueCategory.MOTIVE,
        source_suspect="lady",
        is_key_evidence=True,
        points_to="lady"
    ),
    "SHINY_OBJECT": Clue(
        id="SHINY_OBJECT",
        name="Shiny Object",
        description="Clara saw Lady Ashworth clutching something shiny - likely metal - when she saw her in the corridor. Consistent with the murder weapon.",
        category=ClueCategory.PHYSICAL,
        source_suspect="maid",
        is_key_evidence=True,
        points_to="lady"
    ),
    "DISTRESSED_LADY": Clue(
        id="DISTRESSED_LADY",
        name="Lady's Distress",
        description="Lady Ashworth appeared extremely distressed when seen near the library - pale, hair disheveled, breathing hard as if she had been running.",
        category=ClueCategory.BEHAVIORAL,
        source_suspect="maid",
        is_key_evidence=True,
        points_to="lady"
    ),

    # === CLARA CLUES ===
    "ALIBI_CLARA": Clue(
        id="ALIBI_CLARA",
        name="Clara's Account",
        description="Clara was with Lady Ashworth until 10:45 PM, then met Thomas Whitmore. She returned to Lady Ashworth's chambers at 11:15 PM.",
        category=ClueCategory.ALIBI,
        source_suspect="maid",
        is_key_evidence=False
    ),
    "WITNESS_CLARA": Clue(
        id="WITNESS_CLARA",
        name="Clara's Witness Account",
        description="Clara saw Lady Ashworth in the corridor near the library at approximately 10:50 PM, coming from the direction of the library and looking distressed.",
        category=ClueCategory.WITNESS,
        source_suspect="maid",
        is_key_evidence=True,
        points_to="lady"
    ),
    "LOYALTY_CLARA": Clue(
        id="LOYALTY_CLARA",
        name="Clara's Torn Loyalty",
        description="Clara is torn between loyalty to her mistress and telling the truth about what she saw that night.",
        category=ClueCategory.BEHAVIORAL,
        source_suspect="maid",
        is_key_evidence=False
    ),
    "MEETING_SECRET": Clue(
        id="MEETING_SECRET",
        name="Secret Meeting",
        description="Clara and Thomas were meeting secretly that night in the servants' corridor, as Lady Ashworth disapproves of their courtship.",
        category=ClueCategory.RELATIONSHIP,
        source_suspect="maid",
        is_key_evidence=False
    ),

    # === THOMAS CLUES ===
    "ALIBI_THOMAS_CLARA": Clue(
        id="ALIBI_THOMAS_CLARA",
        name="Thomas with Clara",
        description="Thomas Whitmore was with Clara from 10:45 PM until just after 11:00 PM. Clara confirms this alibi.",
        category=ClueCategory.ALIBI,
        source_suspect="student",
        is_key_evidence=False
    ),
    "ALIBI_THOMAS_FOOTMAN": Clue(
        id="ALIBI_THOMAS_FOOTMAN",
        name="Footman Witness",
        description="A footman saw Thomas in the main hall at approximately 11:10 PM, confirming his account of returning to his room.",
        category=ClueCategory.ALIBI,
        source_suspect="student",
        is_key_evidence=False
    ),
    "CONFRONTATION_THOMAS": Clue(
        id="CONFRONTATION_THOMAS",
        name="Thomas Confronted Pemberton",
        description="Thomas confronted Lord Pemberton two days ago about improper advances toward Clara. Pemberton dismissed him with threats.",
        category=ClueCategory.MOTIVE,
        source_suspect="student",
        is_key_evidence=False,
        points_to="student"
    ),
    "MOTIVE_THOMAS_ANGER": Clue(
        id="MOTIVE_THOMAS_ANGER",
        name="Thomas's Anger",
        description="Thomas was furious at Lord Pemberton for his treatment of Clara. He had motive, but his alibi is solid.",
        category=ClueCategory.MOTIVE,
        source_suspect="student",
        is_key_evidence=False,
        points_to="student"  # Red herring
    ),
    "RELATIONSHIP_CLARA_THOMAS": Clue(
        id="RELATIONSHIP_CLARA_THOMAS",
        name="Clara & Thomas Courting",
        description="Clara and Thomas are secretly courting and plan to marry, despite the class difference.",
        category=ClueCategory.RELATIONSHIP,
        source_suspect="student",
        is_key_evidence=False
    ),

    # === GENERAL CLUES ===
    "TIME_OF_DEATH": Clue(
        id="TIME_OF_DEATH",
        name="Time of Death",
        description="Lord Pemberton was killed between 10:50 PM and 11:00 PM, based on when he was last seen and when the body was discovered.",
        category=ClueCategory.TIMELINE,
        source_suspect="any",
        is_key_evidence=False
    ),
}


# Key clues required for conviction
KEY_CLUE_IDS = [
    "ALIBI_LADY_GAP",
    "CORRIDOR_LADY",
    "MOTIVE_LADY_BLACKMAIL",
    "SHINY_OBJECT",
    "DISTRESSED_LADY",
    "WITNESS_CLARA",
]


@dataclass
class EvidenceNotebook:
    """Tracks all discovered clues during the game."""
    discovered_clues: set[str] = field(default_factory=set)

    def add_clue(self, clue_id: str) -> bool:
        """
        Add a clue to the notebook.
        Returns True if this is a new clue, False if already discovered.
        """
        if clue_id in self.discovered_clues:
            return False
        if clue_id in CLUES:
            self.discovered_clues.add(clue_id)
            return True
        return False

    def add_clues(self, clue_ids: list[str]) -> list[str]:
        """Add multiple clues and return list of newly discovered ones."""
        new_clues = []
        for clue_id in clue_ids:
            if self.add_clue(clue_id):
                new_clues.append(clue_id)
        return new_clues

    def has_clue(self, clue_id: str) -> bool:
        """Check if a clue has been discovered."""
        return clue_id in self.discovered_clues

    def get_clue(self, clue_id: str) -> Optional[Clue]:
        """Get clue details if discovered."""
        if clue_id in self.discovered_clues:
            return CLUES.get(clue_id)
        return None

    def get_all_discovered(self) -> list[Clue]:
        """Get all discovered clues as Clue objects."""
        return [CLUES[cid] for cid in self.discovered_clues if cid in CLUES]

    def get_clues_by_category(self, category: ClueCategory) -> list[Clue]:
        """Get all discovered clues of a specific category."""
        return [
            CLUES[cid] for cid in self.discovered_clues
            if cid in CLUES and CLUES[cid].category == category
        ]

    def get_clues_pointing_to(self, suspect_id: str) -> list[Clue]:
        """Get all clues that point to a specific suspect."""
        return [
            CLUES[cid] for cid in self.discovered_clues
            if cid in CLUES and CLUES[cid].points_to == suspect_id
        ]

    def get_key_clues_count(self) -> int:
        """Count how many key clues have been discovered."""
        return len([cid for cid in self.discovered_clues if cid in KEY_CLUE_IDS])

    def get_key_clues(self) -> list[Clue]:
        """Get all discovered key clues."""
        return [
            CLUES[cid] for cid in self.discovered_clues
            if cid in KEY_CLUE_IDS
        ]

    def count(self) -> int:
        """Get total number of discovered clues."""
        return len(self.discovered_clues)


class AccusationResult(Enum):
    """Possible outcomes of making an accusation."""
    VICTORY = "victory"           # Correct accusation with strong evidence
    PARTIAL_WIN = "partial_win"   # Correct accusation with weak evidence
    DEFEAT = "defeat"             # Wrong accusation or insufficient evidence


@dataclass
class AccusationOutcome:
    """Result of making an accusation."""
    result: AccusationResult
    message: str
    key_clues_found: int
    accused_suspect: str


def evaluate_accusation(accused_id: str, notebook: EvidenceNotebook) -> AccusationOutcome:
    """
    Evaluate whether an accusation is correct and well-supported.

    Returns AccusationOutcome with result and explanation.
    """
    key_clues_count = notebook.get_key_clues_count()
    clues_pointing_to_lady = len(notebook.get_clues_pointing_to("lady"))

    # Correct accusation: Lady Ashworth
    if accused_id == "lady":
        if key_clues_count >= 4:
            return AccusationOutcome(
                result=AccusationResult.VICTORY,
                message=_get_victory_message(key_clues_count, notebook.get_key_clues()),
                key_clues_found=key_clues_count,
                accused_suspect="lady"
            )
        elif key_clues_count >= 2:
            return AccusationOutcome(
                result=AccusationResult.PARTIAL_WIN,
                message=_get_partial_win_message(key_clues_count),
                key_clues_found=key_clues_count,
                accused_suspect="lady"
            )
        else:
            return AccusationOutcome(
                result=AccusationResult.DEFEAT,
                message=_get_insufficient_evidence_message(),
                key_clues_found=key_clues_count,
                accused_suspect="lady"
            )

    # Wrong accusation
    else:
        return AccusationOutcome(
            result=AccusationResult.DEFEAT,
            message=_get_wrong_accusation_message(accused_id, key_clues_count),
            key_clues_found=key_clues_count,
            accused_suspect=accused_id
        )


def _get_victory_message(key_clues: int, clues: list[Clue]) -> str:
    """Generate victory message."""
    clue_list = "\n".join([f"  - {c.name}: {c.description}" for c in clues])
    return f"""
{'='*60}
              CASE SOLVED!
{'='*60}

Your deduction is CORRECT, Inspector!

Lady Cordelia Ashworth breaks down under the weight of your evidence.

"Very well, Inspector. You've found me out."

She confesses: "Lord Pemberton was going to destroy me - not just
my reputation, but everything my family built over generations.
When I refused his... demands... he threatened to expose my
desperate attempts to save my estate. I found Major Thornton's
letter opener and... I saw my opportunity."

Lady Ashworth is taken into custody. Justice is served.

YOUR KEY EVIDENCE ({key_clues} pieces):
{clue_list}

CONGRATULATIONS, INSPECTOR!
{'='*60}
"""


def _get_partial_win_message(key_clues: int) -> str:
    """Generate partial win message."""
    return f"""
{'='*60}
              CASE CLOSED... BARELY
{'='*60}

Your accusation is CORRECT - Lady Ashworth did commit the murder.

However, your evidence was thin. With only {key_clues} key pieces of
evidence, the prosecution will have a difficult time securing a
conviction. Lady Ashworth may yet escape justice on a technicality.

A more thorough investigation might have uncovered stronger proof.
The key witnesses and physical evidence could have built an
airtight case.

RESULT: Correct deduction, but weak evidence.
        Consider investigating more thoroughly next time.
{'='*60}
"""


def _get_insufficient_evidence_message() -> str:
    """Generate insufficient evidence message."""
    return f"""
{'='*60}
              INSUFFICIENT EVIDENCE
{'='*60}

You accuse Lady Ashworth, but your evidence is sorely lacking.

While your instincts may be correct, without proper evidence to
support your accusation, the magistrate dismisses the case.
Lady Ashworth walks free, and the murder of Lord Pemberton
remains officially unsolved.

Perhaps if you had questioned the witnesses more carefully,
you might have uncovered the proof needed to secure justice.

THE TRUE KILLER: Lady Cordelia Ashworth
She murdered Lord Pemberton to prevent him from exposing her
desperate financial schemes and ruining her reputation forever.

RESULT: Correct suspect, but case dismissed due to lack of evidence.
{'='*60}
"""


def _get_wrong_accusation_message(accused_id: str, key_clues: int) -> str:
    """Generate wrong accusation message."""
    suspect_names = {
        "major": "Major Edmund Thornton",
        "maid": "Clara Finch",
        "student": "Thomas Whitmore"
    }
    accused_name = suspect_names.get(accused_id, "Unknown")

    return f"""
{'='*60}
              WRONG ACCUSATION
{'='*60}

You accuse {accused_name}, but your deduction is INCORRECT.

Upon further investigation, their alibi holds firm and they are
cleared of all suspicion. Meanwhile, the true killer slips away.

THE TRUE KILLER: Lady Cordelia Ashworth

She had motive - Lord Pemberton was blackmailing her.
She had opportunity - her alibi had a gap from 10:45 PM.
She was seen by Clara near the library, distressed and clutching
the murder weapon.

You found {key_clues} key pieces of evidence pointing to her,
but failed to see the truth.

RESULT: Wrong accusation. Justice denied.
{'='*60}
"""


def get_clue(clue_id: str) -> Optional[Clue]:
    """Get a clue by ID."""
    return CLUES.get(clue_id)


def get_all_clues() -> list[Clue]:
    """Get all clues in the game."""
    return list(CLUES.values())
