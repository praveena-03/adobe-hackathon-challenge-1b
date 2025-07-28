"""
Persona-Based Content Analysis Module
Local ML models for offline persona analysis
"""

import re
import nltk
from typing import Dict, List, Any, Optional
from loguru import logger
import textstat

class PersonaAnalyzer:
    def __init__(self):
        self.personas = {
            "researcher": {
                "keywords": ["research", "study", "analysis", "methodology", "findings", "conclusion", "data", "results", "hypothesis", "experiment"],
                "focus": "academic and research content"
            },
            "student": {
                "keywords": ["learning", "education", "course", "assignment", "study", "academic", "university", "college", "textbook", "lecture"],
                "focus": "educational content and learning materials"
            },
            "business_analyst": {
                "keywords": ["business", "market", "strategy", "analysis", "report", "financial", "performance", "metrics", "revenue", "profit"],
                "focus": "business and financial analysis"
            },
            "technical_writer": {
                "keywords": ["technical", "documentation", "manual", "guide", "procedure", "specification", "api", "code", "system", "implementation"],
                "focus": "technical documentation and manuals"
            },
            "legal_professional": {
                "keywords": ["legal", "law", "contract", "agreement", "clause", "jurisdiction", "compliance", "regulation", "attorney", "court"],
                "focus": "legal documents and contracts"
            },
            "medical_professional": {
                "keywords": ["medical", "health", "patient", "treatment", "diagnosis", "clinical", "medicine", "healthcare", "symptoms", "therapy"],
                "focus": "medical and healthcare content"
            },
            "travel_planner": {
                "keywords": ["travel", "tourism", "vacation", "destination", "hotel", "restaurant", "attraction", "culture", "cuisine", "adventure"],
                "focus": "travel and tourism content"
            }
        }
    
    def detect_persona(self, text_content: List[Dict[str, Any]]) -> str:
        """Automatically detect the most appropriate persona based on content"""
        try:
            if not text_content:
                return "general"
            
            # Combine all text
            full_text = " ".join([item.get("text", "") for item in text_content])
            full_text_lower = full_text.lower()
            
            # Calculate scores for each persona
            persona_scores = {}
            for persona_type, persona_info in self.personas.items():
                keywords = persona_info["keywords"]
                score = sum(full_text_lower.count(keyword.lower()) for keyword in keywords)
                persona_scores[persona_type] = score
            
            # Find the persona with highest score
            if persona_scores:
                best_persona = max(persona_scores, key=persona_scores.get)
                if persona_scores[best_persona] > 0:
                    return best_persona
            
            return "general"
            
        except Exception as e:
            logger.error(f"Error detecting persona: {e}")
            return "general"
    
    def analyze_content(self, text_content: List[Dict[str, Any]], persona_type: str = "auto") -> Dict[str, Any]:
        """Analyze content based on persona."""
        try:
            if not text_content:
                return {"persona_analysis": "No content to analyze"}
            
            # Auto-detect persona if not specified
            if persona_type == "auto":
                persona_type = self.detect_persona(text_content)
            
            # Combine all text
            full_text = " ".join([item.get("text", "") for item in text_content])
            
            # Basic text analysis
            analysis = {
                "persona_type": persona_type,
                "text_length": len(full_text),
                "word_count": len(full_text.split()),
                "readability_score": textstat.flesch_reading_ease(full_text),
                "complexity_level": self._get_complexity_level(full_text),
                "key_themes": self._extract_key_themes(full_text),
                "content_summary": self._generate_summary(full_text)
            }
            
            # Persona-specific analysis
            if persona_type in self.personas:
                persona_analysis = self._analyze_for_persona(full_text, persona_type)
                analysis.update(persona_analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in persona analysis: {e}")
            return {"error": str(e)}
    
    def _get_complexity_level(self, text: str) -> str:
        """Determine text complexity level."""
        try:
            score = textstat.flesch_reading_ease(text)
            if score >= 90:
                return "Very Easy"
            elif score >= 80:
                return "Easy"
            elif score >= 70:
                return "Fairly Easy"
            elif score >= 60:
                return "Standard"
            elif score >= 50:
                return "Fairly Difficult"
            elif score >= 30:
                return "Difficult"
            else:
                return "Very Difficult"
        except:
            return "Unknown"
    
    def _extract_key_themes(self, text: str) -> List[str]:
        """Extract key themes from text."""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = {}
            
            for word in words:
                if len(word) > 4:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top 5 most frequent words
            themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            return [theme[0] for theme in themes]
            
        except Exception as e:
            logger.error(f"Error extracting themes: {e}")
            return []
    
    def _generate_summary(self, text: str) -> str:
        """Generate a simple summary."""
        try:
            sentences = text.split('.')
            if len(sentences) > 3:
                return '. '.join(sentences[:3]) + '.'
            return text[:200] + '...' if len(text) > 200 else text
        except:
            return "Summary not available"
    
    def _analyze_for_persona(self, text: str, persona_type: str) -> Dict[str, Any]:
        """Analyze content specifically for a given persona."""
        try:
            persona = self.personas.get(persona_type, {})
            keywords = persona.get("keywords", [])
            
            # Count keyword occurrences
            keyword_matches = {}
            for keyword in keywords:
                count = len(re.findall(rf'\b{keyword}\b', text.lower()))
                if count > 0:
                    keyword_matches[keyword] = count
            
            # Calculate relevance score
            total_keywords = sum(keyword_matches.values())
            relevance_score = min(100, (total_keywords / len(text.split())) * 10000)
            
            return {
                "keyword_matches": keyword_matches,
                "relevance_score": round(relevance_score, 2),
                "focus_area": persona.get("focus", "General content"),
                "recommendations": self._get_recommendations(persona_type, relevance_score)
            }
            
        except Exception as e:
            logger.error(f"Error in persona-specific analysis: {e}")
            return {}
    
    def _get_recommendations(self, persona_type: str, relevance_score: float) -> List[str]:
        """Get recommendations based on persona and relevance."""
        recommendations = []
        
        if relevance_score < 30:
            recommendations.append("Content may not be highly relevant for this persona")
        elif relevance_score > 70:
            recommendations.append("Content is highly relevant for this persona")
        
        if persona_type == "researcher":
            recommendations.append("Look for methodology and findings sections")
        elif persona_type == "student":
            recommendations.append("Focus on educational content and examples")
        elif persona_type == "business_analyst":
            recommendations.append("Identify business metrics and strategic insights")
        elif persona_type == "travel_planner":
            recommendations.append("Focus on destinations, activities, and practical travel information")
        
        return recommendations 