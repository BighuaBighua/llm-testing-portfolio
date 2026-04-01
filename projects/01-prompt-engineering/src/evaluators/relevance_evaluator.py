"""Relevance evaluator for prompt responses."""

from typing import Dict, Any, List
import re


class RelevanceEvaluator:
    """
    Evaluate how well a response stays on topic and addresses the prompt.
    评估响应是否切题并回应了prompt。
    """
    
    def __init__(self):
        self.thresholds = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3
        }
    
    def evaluate(
        self,
        prompt: str,
        response: str,
        key_topics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate relevance of response to prompt.
        
        Args:
            prompt: The original prompt
            response: The LLM's response
            key_topics: Optional list of key topics that should be covered
        
        Returns:
            Dictionary with relevance score and analysis
        """
        # Calculate basic relevance
        keyword_relevance = self._calculate_keyword_relevance(prompt, response)
        
        # Calculate topic coverage if key topics provided
        topic_coverage = 1.0
        covered_topics = []
        if key_topics:
            topic_coverage, covered_topics = self._calculate_topic_coverage(
                response, key_topics
            )
        
        # Calculate overall relevance
        overall_relevance = (keyword_relevance * 0.6 + topic_coverage * 0.4)
        
        # Determine relevance level
        if overall_relevance >= self.thresholds["high"]:
            level = "高度相关"
        elif overall_relevance >= self.thresholds["medium"]:
            level = "中度相关"
        elif overall_relevance >= self.thresholds["low"]:
            level = "低度相关"
        else:
            level = "不相关"
        
        return {
            "relevance_score": round(overall_relevance, 2),
            "level": level,
            "keyword_relevance": round(keyword_relevance, 2),
            "topic_coverage": round(topic_coverage, 2),
            "covered_topics": covered_topics,
            "analysis": self._generate_relevance_analysis(
                overall_relevance, keyword_relevance, topic_coverage
            )
        }
    
    def _calculate_keyword_relevance(self, prompt: str, response: str) -> float:
        """
        Calculate keyword-based relevance.
        基于关键词计算相关性。
        """
        # Extract meaningful words from prompt
        prompt_words = self._extract_meaningful_words(prompt)
        response_words = self._extract_meaningful_words(response)
        
        if len(prompt_words) == 0:
            return 1.0 if len(response_words) > 0 else 0.0
        
        # Calculate overlap
        common_words = prompt_words & response_words
        overlap_ratio = len(common_words) / len(prompt_words)
        
        return overlap_ratio
    
    def _extract_meaningful_words(self, text: str) -> set:
        """Extract meaningful words from text, excluding stop words."""
        # Define stop words (simplified)
        stop_words = {
            # Chinese stop words
            "的", "了", "和", "是", "在", "有", "我", "他", "她", "它",
            "这", "那", "就", "也", "都", "而", "及", "与", "着",
            "或", "一个", "没有", "我们", "你们", "他们", "可以",
            # English stop words
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "yourselves", "he", "him",
            "his", "himself", "she", "her", "hers", "herself", "it", "its",
            "itself", "they", "them", "their", "theirs", "themselves",
            "what", "which", "who", "whom", "this", "that", "these", "those"
        }
        
        # Tokenize (simplified - split by whitespace and punctuation)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        meaningful_words = {
            word for word in words 
            if word not in stop_words and len(word) > 1
        }
        
        return meaningful_words
    
    def _calculate_topic_coverage(
        self,
        response: str,
        key_topics: List[str]
    ) -> tuple:
        """
        Calculate how many key topics are covered in the response.
        计算响应中覆盖了多少关键主题。
        """
        if not key_topics:
            return 1.0, []
        
        response_lower = response.lower()
        covered = []
        
        for topic in key_topics:
            # Check if topic or related terms appear in response
            if topic.lower() in response_lower:
                covered.append(topic)
        
        coverage = len(covered) / len(key_topics)
        return coverage, covered
    
    def _generate_relevance_analysis(
        self,
        overall: float,
        keyword_rel: float,
        topic_cov: float
    ) -> str:
        """Generate qualitative analysis of relevance."""
        parts = []
        
        if overall >= 0.8:
            parts.append("响应高度相关，很好地回应了prompt的主题")
        elif overall >= 0.5:
            parts.append("响应基本相关，但可能有部分内容偏离主题")
        else:
            parts.append("响应相关性较低，可能偏离了prompt的核心主题")
        
        if keyword_rel < 0.3:
            parts.append("关键词匹配度较低")
        elif keyword_rel > 0.7:
            parts.append("关键词匹配度良好")
        
        if topic_cov < 0.5:
            parts.append("部分关键主题未被覆盖")
        
        return "。".join(parts)
