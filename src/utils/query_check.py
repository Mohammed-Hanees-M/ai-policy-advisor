from typing import List, Dict, Set
import re

class QueryClassifier:
    def __init__(self):
        # Core business/legal keywords
        self.business_keywords: Set[str] = {
            "tax", "license", "compliance", "regulation",
            "contract", "llc", "corporation", "irs",
            "employee", "wage", "osha", "filing",
            "legal", "law", "statute", "ordinance",
            "agreement", "clause", "penalty", "fine"
        }
        
        # Patterns for high-priority legal references
        self.priority_patterns: List[str] = [
            r"\b\d{4} [A-Z]+\b",  # "2023 IRS"
            r"Section \d+ [A-Z]{2,10}",  # "Section 123 ABC"
            r"[A-Z]{2,10}-\d{4}",  # "HR-1234"
            r"Article [IVXLCDM]+",  # Roman numeral articles
            r"\b\d+ [A-Z][a-z]+ Code"  # "42 US Code"
        ]
        
        # Common legal entity patterns
        self.entity_patterns: Dict[str, str] = {
            "law_reference": r"[A-Z][a-z]+ \d+ [A-Z]{2,10}",
            "acronym": r"\b[A-Z]{2,10}\b",
            "legal_citation": r"\d+ [A-Z]+\s?\d+"
        }

    def is_business_related(self, query: str) -> bool:
        """
        Determines if a query is business/legal related
        
        Args:
            query: User input string
            
        Returns:
            bool: True if business/legal related, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
            
        query_lower = query.lower()
        
        # Check for priority patterns first (case sensitive)
        for pattern in self.priority_patterns:
            if re.search(pattern, query):
                return True
                
        # Check for keywords in lowercase
        return any(keyword in query_lower for keyword in self.business_keywords)
        
    def get_query_type(self, query: str) -> Dict:
        """
        Classifies query with detailed metadata
        
        Args:
            query: User input string
            
        Returns:
            Dict: {
                "is_business": bool,
                "priority": int (0-5),
                "entities": List[str]
            }
        """
        return {
            "is_business": self.is_business_related(query),
            "priority": self._get_priority_score(query),
            "entities": self._extract_entities(query)
        }
        
    def _get_priority_score(self, query: str) -> int:
        """
        Scores query importance (0-5)
        0 = Not business related
        5 = Critical legal/business query
        """
        if not self.is_business_related(query):
            return 0
            
        score = 2  # Base score for business-related
            
        # Additional points for specific patterns
        if any(re.search(p, query) for p in self.priority_patterns):
            score += 3
            
        return min(5, score)
        
    def _extract_entities(self, query: str) -> List[str]:
        """
        Extracts key legal/business entities from query
        
        Args:
            query: User input string
            
        Returns:
            List[str]: Found entities (max 10)
        """
        if not query:
            return []
            
        entities = set()
        
        # Extract all entity types
        for entity_type, pattern in self.entity_patterns.items():
            entities.update(re.findall(pattern, query))
            
        return sorted(list(entities))[:10]  # Return top 10 entities

# Create global instance
query_classifier = QueryClassifier()

# Expose main function directly
def is_business_related(query: str) -> bool:
    """Public interface for business/legal check"""
    return query_classifier.is_business_related(query)