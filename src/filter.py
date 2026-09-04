"""
Stage 2 Filter Module for Discovery Engine.
Implements the 4 sequential filtering gates for Play Store reviews
while passing Reddit and Survey records through untouched.
"""

import re
import yaml
from typing import Dict, Any, List, Tuple, Optional

class DiscoveryFilter:
    def __init__(self, config_path: str = "config/filters.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        ps_cfg = self.config.get("play_store_filters", {})
        self.min_words = ps_cfg.get("gate_2_word_count", {}).get("min_words", 15)
        self.wishlist_terms = [t.lower() for t in ps_cfg.get("gate_3_wishlist_terms", {}).get("terms", [])]
        
        # Compile gate 4 regex patterns
        patterns_cfg = ps_cfg.get("gate_4_deliberation_and_blockers", {}).get("patterns", [])
        self.patterns: List[Tuple[str, re.Pattern]] = [
            (p["name"], re.compile(p["regex"], re.I)) for p in patterns_cfg
        ]
        self.pass_through_sources = set(self.config.get("pass_through_sources", ["reddit", "survey"]))

    def gate_1_non_empty(self, record: Dict[str, Any]) -> bool:
        """Gate 1: Review text must be non-empty string."""
        text = record.get("text")
        return bool(isinstance(text, str) and text.strip())

    def gate_2_word_count(self, record: Dict[str, Any]) -> bool:
        """Gate 2: Word count must be >= min_words threshold."""
        text = record.get("text", "")
        return len(text.strip().split()) >= self.min_words

    def gate_3_wishlist_terms(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Gate 3: Must match at least one wishlist-relevant term.
        Checks both record's pre-matched terms (if present) and direct text match.
        """
        meta_matched = [t.lower() for t in record.get("meta", {}).get("matched_terms", [])]
        text_lower = record.get("text", "").lower()
        
        found_terms = []
        for term in self.wishlist_terms:
            if term in meta_matched or re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                found_terms.append(term)
                
        return (len(found_terms) > 0, found_terms)

    def gate_4_deliberation_and_blockers(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Gate 4: Must match deliberation language or structural-blocker pattern.
        Returns (is_matched, matched_pattern_name).
        """
        text = record.get("text", "")
        for name, pattern in self.patterns:
            if pattern.search(text):
                return True, name
        return False, None
