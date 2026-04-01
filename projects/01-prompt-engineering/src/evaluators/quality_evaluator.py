"""Quality evaluator for prompt responses."""

from typing import Dict, Any, List


class QualityEvaluator:
    """
    Evaluate the quality of LLM responses based on multiple metrics.
    评估LLM响应的质量，基于多个指标。
    """
    
    def __init__(self):
        self.metrics = {
            "completeness": self._evaluate_completeness,
            "clarity": self._evaluate_clarity,
            "relevance": self._evaluate_relevance,
            "coherence": self._evaluate_coherence
        }
    
    def evaluate(
        self,
        prompt: str,
        response: str,
        expected_keywords: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a response based on the prompt.
        
        Args:
            prompt: The original prompt
            response: The LLM's response
            expected_keywords: Optional list of expected keywords
        
        Returns:
            Dictionary containing scores and analysis
        """
        scores = {}
        
        # Calculate individual metrics
        for metric_name, metric_func in self.metrics.items():
            scores[metric_name] = metric_func(prompt, response, expected_keywords)
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "overall_score": round(overall_score, 2),
            "metrics": scores,
            "analysis": self._generate_analysis(scores, response)
        }
    
    def _evaluate_completeness(
        self,
        prompt: str,
        response: str,
        expected_keywords: List[str] = None
    ) -> float:
        """
        Evaluate if the response addresses all aspects of the prompt.
        评估响应是否完整回答了prompt的所有方面。
        
        Score: 0.0 - 1.0
        """
        if not response or len(response.strip()) == 0:
            return 0.0
        
        # Basic heuristic: response length and structure
        length_score = min(len(response.split()) / 50, 1.0)  # Normalize around 50 words
        
        # Check for expected keywords if provided
        keyword_score = 1.0
        if expected_keywords:
            found_keywords = sum(1 for kw in expected_keywords if kw.lower() in response.lower())
            keyword_score = found_keywords / len(expected_keywords)
        
        # Average of length and keyword scores
        return round((length_score + keyword_score) / 2, 2)
    
    def _evaluate_clarity(
        self,
        prompt: str,
        response: str,
        expected_keywords: List[str] = None
    ) -> float:
        """
        Evaluate clarity of the response.
        评估响应的清晰度。
        
        Score: 0.0 - 1.0
        """
        if not response:
            return 0.0
        
        # Check for structural indicators (lists, paragraphs, etc.)
        has_structure = any([
            "\n•" in response or "\n-" in response,  # Bullet points
            "\n\n" in response,  # Multiple paragraphs
            ":" in response  # Clear sections
        ])
        
        # Check for clarity indicators
        clarity_indicators = [
            not response.isupper(),  # Not all caps
            len(response.split(".")) > 1,  # Multiple sentences
            not any(char * 3 in response for char in "!?")  # No excessive punctuation
        ]
        
        structure_score = 1.0 if has_structure else 0.7
        clarity_score = sum(clarity_indicators) / len(clarity_indicators)
        
        return round((structure_score + clarity_score) / 2, 2)
    
    def _evaluate_relevance(
        self,
        prompt: str,
        response: str,
        expected_keywords: List[str] = None
    ) -> float:
        """
        Evaluate relevance to the prompt.
        评估与prompt的相关性。
        
        Score: 0.0 - 1.0
        """
        if not response or not prompt:
            return 0.0
        
        # Extract key terms from prompt (simplified)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common stop words (simplified)
        stop_words = {"的", "是", "在", "了", "和", "a", "the", "is", "are", "was", "were"}
        prompt_words -= stop_words
        response_words -= stop_words
        
        # Calculate word overlap
        if len(prompt_words) == 0:
            return 1.0 if len(response_words) > 0 else 0.0
        
        overlap = len(prompt_words & response_words) / len(prompt_words)
        
        return round(overlap, 2)
    
    def _evaluate_coherence(
        self,
        prompt: str,
        response: str,
        expected_keywords: List[str] = None
    ) -> float:
        """
        Evaluate coherence and logical flow.
        评估连贯性和逻辑性。
        
        Score: 0.0 - 1.0
        """
        if not response:
            return 0.0
        
        # Check for transition words and logical connectors
        connectors = [
            "首先", "其次", "最后", "因此", "所以", "但是", "然而",
            "first", "second", "finally", "therefore", "however", "moreover"
        ]
        
        has_connectors = any(conn in response.lower() for conn in connectors)
        
        # Check sentence length consistency (avoid run-on sentences)
        sentences = [s.strip() for s in response.split(".") if s.strip()]
        if len(sentences) == 0:
            return 0.5
        
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_consistency = 1.0 if 5 < avg_length < 30 else 0.7
        
        connector_score = 0.9 if has_connectors else 0.6
        
        return round((connector_score + length_consistency) / 2, 2)
    
    def _generate_analysis(self, scores: Dict[str, float], response: str) -> str:
        """Generate qualitative analysis based on scores."""
        overall = sum(scores.values()) / len(scores)
        
        if overall >= 0.8:
            quality = "优秀"
        elif overall >= 0.6:
            quality = "良好"
        elif overall >= 0.4:
            quality = "一般"
        else:
            quality = "需要改进"
        
        analysis_parts = [f"整体质量：{quality}"]
        
        # Identify strengths and weaknesses
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [name for name, score in sorted_scores[:2] if score >= 0.7]
        weaknesses = [name for name, score in sorted_scores[-2:] if score < 0.6]
        
        if strengths:
            analysis_parts.append(f"优势：{', '.join(strengths)}")
        if weaknesses:
            analysis_parts.append(f"改进方向：{', '.join(weaknesses)}")
        
        return " | ".join(analysis_parts)
