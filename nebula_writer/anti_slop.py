import re
from typing import List, Tuple

class AntiSlopFilter:
    """
    Detects and replaces AI slop cliches and repetitive phrasing in prose.
    """

    def __init__(self):
        # List of regex patterns and their dynamic replacements
        self.cliche_map: List[Tuple[re.Pattern, str]] = [
            (re.compile(r'\b(a testament to)\b', re.I), "reflecting"),
            (re.compile(r'\b(labyrinth of emotions)\b', re.I), "complex feelings"),
            (re.compile(r'\b(tapestry of)\b', re.I), "array of"),
            (re.compile(r'\b(symphony of)\b', re.I), "blend of"),
            (re.compile(r'\b(dance of shadows)\b', re.I), "flickering shadows"),
            (re.compile(r'\b(whispers of the past)\b', re.I), "old memories"),
            (re.compile(r'\b(cacophony of)\b', re.I), "noise of"),
            (re.compile(r'\b(palpable tension)\b', re.I), "heavy silence"),
            (re.compile(r'\b(shattered into a million pieces)\b', re.I), "broke apart"),
            (re.compile(r'\b(in a world where)\b', re.I), "where"),
        ]

    def clean_prose(self, text: str) -> str:
        """
        Scans prose for AI cliches and replaces them with stronger, natural phrasing,
        including structural filtering for redundant adverbs and spacing.
        """
        cleaned = text
        for pattern, replacement in self.cliche_map:
            cleaned = pattern.sub(replacement, cleaned)
            
        # Structural filtering: remove redundant filler adverbs
        cleaned = re.sub(r'\b(very|extremely|absolutely|completely|totally|utterly)\b\s+', '', cleaned, flags=re.I)
        
        # Structural filtering: fix repetitive whitespace
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        
        return cleaned.strip()
