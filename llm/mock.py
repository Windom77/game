"""
Mock LLM provider for testing without an actual LLM.
"""

from .base import LLMProvider, ConversationHistory


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without an actual LLM."""

    def __init__(self):
        self.response_templates = {
            "major": [
                "I say, that's a rather pointed question, Inspector. *tugs at collar* I was in the smoking room, dash it all.",
                "By Jove, I resent the implication! I am a man of honour, sir. My service record speaks for itself.",
                "The letter opener? Yes, it was mine. A memento from Crimea. But I did not use it for... that.",
            ],
            "lady": [
                "Inspector, I find your line of questioning most improper. A lady of my standing...",
                "Lord Pemberton and I had a business arrangement. Nothing more. These insinuations are beneath you.",
                "I retired to my chambers at a reasonable hour. Surely you don't expect me to account for every moment?",
            ],
            "maid": [
                "Begging your pardon, sir, but I don't rightly know what you mean. I was with her Ladyship, I was.",
                "I... I shouldn't say, sir. It's not my place to speak ill of my betters.",
                "Thomas - Mr. Whitmore, I mean - he's a good man, sir. He wouldn't hurt no one.",
            ],
            "student": [
                "In principle, Inspector, one must consider the facts dispassionately. Though I admit this situation is most distressing.",
                "I am a student of law, sir. I understand the gravity of these proceedings. I have nothing to hide.",
                "Lord Pemberton was not... shall we say... the most honourable of men. But that is hardly evidence of anything.",
            ],
        }
        self.response_index = {"major": 0, "lady": 0, "maid": 0, "student": 0}

    def generate_response(self, conversation: ConversationHistory) -> str:
        """Return a pre-written response based on character."""
        # Detect character from system prompt
        character_id = None
        for cid in self.response_templates.keys():
            if cid in conversation.system_prompt.lower():
                character_id = cid
                break

        if character_id is None:
            return "I... I'm not sure what to say, Inspector."

        responses = self.response_templates[character_id]
        idx = self.response_index[character_id] % len(responses)
        self.response_index[character_id] += 1
        return responses[idx]

    def is_available(self) -> bool:
        return True
