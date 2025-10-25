"""
Client Insight Analyzer
Analyzes client speech to extract insights about objections, interests, emotions, etc.
"""

import re
from typing import Dict, List, Optional
from collections import deque


class ClientInsightAnalyzer:
    """Analyzes client text to extract sales insights"""
    
    def __init__(self, history_size: int = 5):
        self.history_size = history_size
        self.utterance_history = deque(maxlen=history_size)
        self.client_utterances = 0
        self.total_utterances = 0
        
        # Keywords for detection
        self.objection_keywords = {
            "price": ["expensive", "costly", "price", "afford", "budget", "money", "cheap", "mahal", "harga", "budget", "biaya"],
            "time": ["busy", "no time", "schedule", "when", "how long", "duration", "weeks", "sibuk", "waktu", "jadwal"],
            "family": ["spouse", "husband", "wife", "family", "partner", "discuss", "keluarga", "suami", "istri"],
            "value": ["worth", "benefit", "why", "what for", "results", "guarantee", "manfaat", "apa manfaatnya"],
            "child": ["not interested", "doesn't want", "refuses", "boring", "difficult", "tidak tertarik", "membosankan", "sulit"]
        }
        
        self.interest_keywords = {
            "game-based learning": ["game", "minecraft", "fun", "play", "exciting", "enjoy", "permainan", "main", "seru", "menyenangkan"],
            "future skills": ["future", "career", "profession", "technology", "it", "programming", "masa depan", "karir", "teknologi"],
            "logic": ["think", "logic", "problem solving", "analytical", "smart", "clever", "logika", "berpikir", "masalah"],
            "creativity": ["creative", "create", "build", "design", "imagination", "kreatif", "membuat", "desain"],
            "confidence": ["confident", "self-esteem", "believe", "capable", "achieve", "percaya diri", "mampu"]
        }
        
        self.emotion_keywords = {
            "engaged": ["yes", "great", "interesting", "tell me more", "sounds good", "like", "love", "ya", "bagus", "menarik", "ceritakan lagi"],
            "curious": ["how", "what", "when", "where", "really", "tell me", "explain", "curious", "bagaimana", "apa", "jelaskan"],
            "hesitant": ["maybe", "not sure", "think about", "consider", "hmm", "well", "mungkin", "tidak yakin", "pikirkan"],
            "defensive": ["but", "however", "no", "don't", "can't", "won't", "already", "tapi", "tetapi", "tidak", "sudah"],
            "negative": ["bad", "terrible", "waste", "useless", "not working", "disappointed", "buruk", "sia-sia", "tidak berfungsi"]
        }
        
        self.stage_patterns = {
            "profiling": ["child", "age", "experience", "interested", "hobby", "school", "grade"],
            "presentation": ["how it works", "program", "lesson", "teacher", "learn", "include"],
            "objection": ["but", "expensive", "busy", "not sure", "problem", "concern"],
            "closing": ["start", "register", "sign up", "payment", "schedule", "first lesson"]
        }
    
    def analyze_client_text(self, text: str, is_client: bool = True) -> Dict:
        """
        Analyze client utterance and return insights
        
        Args:
            text: The utterance text
            is_client: Whether this is a client speaking (for engagement tracking)
            
        Returns:
            Dictionary with insights
        """
        text_lower = text.lower()
        
        # Update utterance counts
        self.total_utterances += 1
        if is_client:
            self.client_utterances += 1
            self.utterance_history.append(text_lower)
        
        # Analyze current + history
        all_text = " ".join(self.utterance_history)
        
        # Detect stage
        stage = self._detect_stage(all_text)
        
        # Detect emotion
        emotion = self._detect_emotion(text_lower)
        
        # Detect objections
        active_objections = self._detect_objections(all_text)
        
        # Detect interests
        interests = self._detect_interests(all_text)
        
        # Extract need
        need = self._extract_need(all_text)
        
        # Calculate engagement
        engagement = self._calculate_engagement()
        
        # Determine trend (simplified)
        trend = self._determine_trend(emotion)
        
        return {
            "stage": stage,
            "emotion": emotion,
            "active_objections": active_objections,
            "interests": interests,
            "need": need,
            "engagement": round(engagement, 2),
            "trend": trend
        }
    
    def _detect_stage(self, text: str) -> str:
        """Detect current dialogue stage"""
        stage_scores = {}
        
        for stage, keywords in self.stage_patterns.items():
            score = sum(1 for kw in keywords if kw in text)
            stage_scores[stage] = score
        
        if not any(stage_scores.values()):
            return "profiling"
        
        return max(stage_scores, key=stage_scores.get)
    
    def _detect_emotion(self, text: str) -> str:
        """Detect emotional tone"""
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            emotion_scores[emotion] = score
        
        if not any(emotion_scores.values()):
            return "curious"
        
        return max(emotion_scores, key=emotion_scores.get)
    
    def _detect_objections(self, text: str) -> List[str]:
        """Detect active objections"""
        objections = []
        
        for objection, keywords in self.objection_keywords.items():
            if any(kw in text for kw in keywords):
                objections.append(objection)
        
        return objections[:3]  # Max 3 objections
    
    def _detect_interests(self, text: str) -> List[str]:
        """Detect topics of interest"""
        interests = []
        
        for interest, keywords in self.interest_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                interests.append(interest)
        
        return interests[:3]  # Max 3 interests
    
    def _extract_need(self, text: str) -> Optional[str]:
        """Extract stated need from text"""
        # Look for patterns like "I want...", "I need...", "so that..."
        patterns = [
            r"(?:want|need|would like)(?:\s+\w+){0,2}\s+to\s+([^.,!?]+)",
            r"so that\s+(?:he|she|they|child)?\s*(?:can|will)?\s*([^.,!?]+)",
            r"(?:help|improve|develop|learn)\s+([^.,!?]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                need = match.group(1).strip()
                # Limit length
                if len(need) > 50:
                    need = need[:47] + "..."
                return need
        
        # Fallback: look for key phrases
        if "logic" in text or "think" in text:
            return "improve logical thinking"
        elif "programming" in text or "coding" in text:
            return "learn programming"
        elif "creative" in text:
            return "develop creativity"
        
        return None
    
    def _calculate_engagement(self) -> float:
        """Calculate engagement level based on client participation"""
        if self.total_utterances == 0:
            return 0.5
        
        # Base engagement on client participation
        participation = self.client_utterances / max(self.total_utterances, 1)
        
        # Ideal ratio is around 0.4-0.6 (client talks 40-60% of time)
        if 0.3 <= participation <= 0.7:
            engagement = 0.7 + (0.3 * (participation / 0.5))
        else:
            engagement = 0.5 + (participation * 0.3)
        
        return min(max(engagement, 0.0), 1.0)
    
    def _determine_trend(self, emotion: str) -> str:
        """Determine engagement trend"""
        # Simplified: based on emotion
        positive_emotions = ["engaged", "curious"]
        negative_emotions = ["defensive", "negative"]
        
        if emotion in positive_emotions:
            return "up"
        elif emotion in negative_emotions:
            return "down"
        else:
            return "stable"
    
    def reset(self):
        """Reset analyzer state"""
        self.utterance_history.clear()
        self.client_utterances = 0
        self.total_utterances = 0


# Global instance
_analyzer = ClientInsightAnalyzer()


def analyze_client_text(text: str, is_client: bool = True) -> Dict:
    """
    Convenience function to analyze client text
    
    Args:
        text: The utterance text
        is_client: Whether this is a client speaking
        
    Returns:
        Dictionary with insights
    """
    return _analyzer.analyze_client_text(text, is_client)


def reset_analyzer():
    """Reset the analyzer state"""
    _analyzer.reset()

