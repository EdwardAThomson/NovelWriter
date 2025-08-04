"""
Review & Retry Agent for NovelWriter - Phase 1 Safe Implementation

This agent analyzes generated content and provides recommendations
without changing the existing workflow. It's read-only intelligence
that helps identify quality issues and suggests improvements.
"""

from typing import Dict, List, Any, Optional
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime

from agents.base.agent import BaseAgent, AgentResult, AgentMessage


@dataclass
class ContentReview:
    """Review results for generated content."""
    step_name: str
    quality_score: float  # 0.0 to 1.0
    issues_found: List[str]
    strengths_found: List[str]
    retry_recommended: bool
    improvement_suggestions: List[str]
    confidence: float  # How confident the agent is in its assessment


class ReviewAndRetryAgent(BaseAgent):
    """
    Safe review agent that analyzes content quality and provides recommendations.
    
    Phase 1 Implementation:
    - Analyzes generated content for quality issues
    - Provides detailed recommendations
    - Never modifies workflow or content
    - Conservative thresholds to avoid false positives
    """
    
    def __init__(self, model: str = "gpt-4o", logger: Optional[logging.Logger] = None):
        super().__init__(name="ReviewAndRetryAgent", model=model, logger=logger)
        
        # Conservative thresholds - only flag obvious issues
        self.quality_thresholds = {
            "retry_threshold": 0.3,  # Very low - only retry if clearly broken
            "warning_threshold": 0.6,  # Medium - warn but don't retry
            "good_threshold": 0.8,  # High quality content
        }
        
        # Content analysis patterns
        self.quality_indicators = {
            "character_arcs": {
                "good_signs": [
                    r"character development", r"motivation", r"growth", r"arc",
                    r"personality", r"backstory", r"goals", r"conflict"
                ],
                "warning_signs": [
                    r"generic", r"unclear", r"inconsistent", r"shallow",
                    r"underdeveloped", r"confusing"
                ],
                "required_elements": ["character names", "motivations", "development"]
            },
            "faction_arcs": {
                "good_signs": [
                    r"faction goals", r"political", r"alliance", r"conflict",
                    r"power structure", r"ideology", r"resources"
                ],
                "warning_signs": [
                    r"vague", r"unrealistic", r"contradictory", r"simplistic"
                ],
                "required_elements": ["faction names", "goals", "relationships"]
            },
            "plot_structure": {
                "good_signs": [
                    r"pacing", r"tension", r"climax", r"resolution",
                    r"character development", r"conflict escalation"
                ],
                "warning_signs": [
                    r"rushed", r"slow", r"confusing", r"anticlimactic",
                    r"unresolved", r"inconsistent"
                ],
                "required_elements": ["clear structure", "conflict", "resolution"]
            }
        }
        
        self.logger.info("Review & Retry Agent initialized (Phase 1 - Analysis Only)")
    
    def review_step_output(self, step_name: str, output_content: str, 
                          context: Optional[Dict] = None) -> ContentReview:
        """
        Analyze the output of a workflow step and provide recommendations.
        
        This is the main Phase 1 function - pure analysis, no modifications.
        """
        self.logger.info(f"🔍 Reviewing {step_name} output ({len(output_content)} chars)")
        
        try:
            # Analyze content quality
            quality_score = self._assess_content_quality(step_name, output_content)
            issues = self._identify_issues(step_name, output_content)
            strengths = self._identify_strengths(step_name, output_content)
            suggestions = self._generate_improvement_suggestions(step_name, issues, context)
            
            # Conservative retry recommendation
            retry_recommended = quality_score < self.quality_thresholds["retry_threshold"]
            
            # Calculate confidence in assessment
            confidence = self._calculate_confidence(step_name, output_content, quality_score)
            
            review = ContentReview(
                step_name=step_name,
                quality_score=quality_score,
                issues_found=issues,
                strengths_found=strengths,
                retry_recommended=retry_recommended,
                improvement_suggestions=suggestions,
                confidence=confidence
            )
            
            self._log_review_results(review)
            return review
            
        except Exception as e:
            self.logger.error(f"Error reviewing {step_name}: {e}")
            # Return safe default review
            return ContentReview(
                step_name=step_name,
                quality_score=0.5,  # Neutral score on error
                issues_found=[f"Review failed: {str(e)}"],
                strengths_found=[],
                retry_recommended=False,  # Conservative - don't retry on error
                improvement_suggestions=["Manual review recommended due to analysis error"],
                confidence=0.0
            )
    
    def _assess_content_quality(self, step_name: str, content: str) -> float:
        """Assess overall content quality using multiple metrics."""
        
        if not content or len(content.strip()) < 50:
            return 0.1  # Very low quality for empty/minimal content
        
        scores = []
        
        # 1. Length appropriateness
        length_score = self._assess_length_quality(step_name, content)
        scores.append(length_score)
        
        # 2. Content structure
        structure_score = self._assess_structure_quality(step_name, content)
        scores.append(structure_score)
        
        # 3. Domain-specific quality
        domain_score = self._assess_domain_quality(step_name, content)
        scores.append(domain_score)
        
        # 4. Language quality
        language_score = self._assess_language_quality(content)
        scores.append(language_score)
        
        # Average with slight bias toward domain-specific quality
        weights = [0.2, 0.3, 0.4, 0.1]
        weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return min(1.0, max(0.0, weighted_score))
    
    def _assess_length_quality(self, step_name: str, content: str) -> float:
        """Assess if content length is appropriate for the step."""
        
        length = len(content)
        
        # Expected length ranges for different steps
        expected_ranges = {
            "character_arcs": (500, 3000),
            "faction_arcs": (400, 2500),
            "plot_structure": (800, 4000),
            "locations": (300, 2000),
            "improve_structure": (1000, 5000)
        }
        
        min_length, max_length = expected_ranges.get(step_name, (200, 10000))
        
        if length < min_length * 0.5:
            return 0.2  # Too short
        elif length < min_length:
            return 0.6  # Somewhat short
        elif length <= max_length:
            return 1.0  # Good length
        elif length <= max_length * 1.5:
            return 0.8  # Somewhat long
        else:
            return 0.5  # Too long
    
    def _assess_structure_quality(self, step_name: str, content: str) -> float:
        """Assess content structure and organization."""
        
        score = 0.5  # Start with neutral
        
        # Check for headers/sections
        if re.search(r'^#+\s+', content, re.MULTILINE):
            score += 0.2
        
        # Check for lists/organization
        if re.search(r'^\s*[-*]\s+', content, re.MULTILINE):
            score += 0.1
        
        # Check for paragraphs (not just one big block)
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 0.2
        
        # Check for reasonable sentence length
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 25:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_domain_quality(self, step_name: str, content: str) -> float:
        """Assess quality specific to the content domain."""
        
        if step_name not in self.quality_indicators:
            return 0.7  # Neutral score for unknown domains
        
        indicators = self.quality_indicators[step_name]
        score = 0.5  # Start neutral
        
        # Check for good signs
        good_matches = 0
        for pattern in indicators["good_signs"]:
            if re.search(pattern, content, re.IGNORECASE):
                good_matches += 1
        
        # Boost score based on good signs found
        good_ratio = good_matches / len(indicators["good_signs"])
        score += good_ratio * 0.4
        
        # Check for warning signs
        warning_matches = 0
        for pattern in indicators["warning_signs"]:
            if re.search(pattern, content, re.IGNORECASE):
                warning_matches += 1
        
        # Reduce score based on warning signs
        warning_ratio = warning_matches / len(indicators["warning_signs"])
        score -= warning_ratio * 0.3
        
        return min(1.0, max(0.0, score))
    
    def _assess_language_quality(self, content: str) -> float:
        """Assess basic language quality."""
        
        score = 0.7  # Start with good baseline
        
        # Check for excessive repetition
        words = content.lower().split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                score -= 0.3  # Too repetitive
            elif unique_ratio > 0.7:
                score += 0.1  # Good variety
        
        # Check for reasonable capitalization
        sentences = re.split(r'[.!?]+', content)
        properly_capitalized = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        if len(sentences) > 0:
            cap_ratio = properly_capitalized / len(sentences)
            if cap_ratio > 0.8:
                score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _identify_issues(self, step_name: str, content: str) -> List[str]:
        """Identify specific issues in the content."""
        
        issues = []
        
        # Basic content checks
        if len(content.strip()) < 100:
            issues.append("Content is very short and may be incomplete")
        
        if not re.search(r'[.!?]', content):
            issues.append("Content lacks proper sentence structure")
        
        # Domain-specific checks
        if step_name in self.quality_indicators:
            indicators = self.quality_indicators[step_name]
            
            # Check for required elements
            for element in indicators["required_elements"]:
                # Simple heuristic - look for keywords related to required elements
                element_keywords = element.lower().split()
                found = any(keyword in content.lower() for keyword in element_keywords)
                if not found:
                    issues.append(f"Missing or unclear {element}")
            
            # Check for warning signs
            for pattern in indicators["warning_signs"]:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Potential issue detected: content may be {pattern}")
        
        return issues
    
    def _identify_strengths(self, step_name: str, content: str) -> List[str]:
        """Identify strengths in the content."""
        
        strengths = []
        
        # Basic quality indicators
        if len(content) > 1000:
            strengths.append("Comprehensive and detailed content")
        
        if re.search(r'^#+\s+', content, re.MULTILINE):
            strengths.append("Well-organized with clear sections")
        
        # Domain-specific strengths
        if step_name in self.quality_indicators:
            indicators = self.quality_indicators[step_name]
            
            good_matches = 0
            for pattern in indicators["good_signs"]:
                if re.search(pattern, content, re.IGNORECASE):
                    good_matches += 1
            
            if good_matches >= len(indicators["good_signs"]) * 0.7:
                strengths.append(f"Strong {step_name.replace('_', ' ')} content with good coverage")
        
        return strengths
    
    def _generate_improvement_suggestions(self, step_name: str, issues: List[str], 
                                        context: Optional[Dict] = None) -> List[str]:
        """Generate specific suggestions for improvement."""
        
        suggestions = []
        
        # Address identified issues
        for issue in issues:
            if "short" in issue.lower():
                suggestions.append(f"Expand the {step_name.replace('_', ' ')} with more detail and examples")
            elif "missing" in issue.lower():
                suggestions.append(f"Add the missing elements identified in the analysis")
            elif "structure" in issue.lower():
                suggestions.append("Improve content organization with headers and clear sections")
        
        # Domain-specific suggestions
        if step_name == "character_arcs":
            suggestions.append("Ensure each character has clear motivations, goals, and development")
        elif step_name == "faction_arcs":
            suggestions.append("Define clear faction goals, relationships, and power structures")
        elif step_name == "plot_structure":
            suggestions.append("Verify proper pacing and conflict escalation throughout the structure")
        
        return suggestions
    
    def _calculate_confidence(self, step_name: str, content: str, quality_score: float) -> float:
        """Calculate confidence in the quality assessment."""
        
        confidence = 0.7  # Base confidence
        
        # Higher confidence for longer content (more to analyze)
        if len(content) > 1000:
            confidence += 0.1
        elif len(content) < 200:
            confidence -= 0.2
        
        # Higher confidence for known domains
        if step_name in self.quality_indicators:
            confidence += 0.1
        
        # More confident in extreme scores
        if quality_score < 0.3 or quality_score > 0.8:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _log_review_results(self, review: ContentReview):
        """Log the review results in a structured way."""
        
        self.logger.info(f"📊 Review Results for {review.step_name}:")
        self.logger.info(f"   Quality Score: {review.quality_score:.2f}")
        self.logger.info(f"   Confidence: {review.confidence:.2f}")
        self.logger.info(f"   Retry Recommended: {review.retry_recommended}")
        
        if review.strengths_found:
            self.logger.info(f"   ✅ Strengths: {', '.join(review.strengths_found)}")
        
        if review.issues_found:
            self.logger.warning(f"   ⚠️ Issues: {', '.join(review.issues_found)}")
        
        if review.improvement_suggestions:
            self.logger.info(f"   💡 Suggestions: {', '.join(review.improvement_suggestions)}")
    
    def review_complete_workflow(self, workflow_results: Dict[str, Any]) -> Dict[str, ContentReview]:
        """Review all steps in a completed workflow."""
        
        self.logger.info("🔍 Reviewing complete workflow results")
        
        reviews = {}
        
        for step_name, result in workflow_results.items():
            if isinstance(result, dict) and "content" in result:
                content = str(result["content"])
                reviews[step_name] = self.review_step_output(step_name, content)
        
        # Generate overall workflow assessment
        self._generate_workflow_summary(reviews)
        
        return reviews
    
    def _generate_workflow_summary(self, reviews: Dict[str, ContentReview]):
        """Generate a summary of the entire workflow quality."""
        
        if not reviews:
            return
        
        avg_quality = sum(review.quality_score for review in reviews.values()) / len(reviews)
        retry_needed = [name for name, review in reviews.items() if review.retry_recommended]
        
        self.logger.info("=" * 50)
        self.logger.info("📋 WORKFLOW REVIEW SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Overall Quality Score: {avg_quality:.2f}")
        self.logger.info(f"Steps Reviewed: {len(reviews)}")
        
        if retry_needed:
            self.logger.warning(f"Steps Needing Retry: {', '.join(retry_needed)}")
        else:
            self.logger.info("✅ All steps meet minimum quality standards")
        
        self.logger.info("=" * 50)
    
    def get_available_tools(self) -> List[str]:
        """Return available review capabilities."""
        return [
            "review_step_output",
            "review_complete_workflow", 
            "assess_content_quality",
            "identify_issues",
            "generate_suggestions"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for review operations."""
        return ["step_name", "content"]
    
    def process_task(self, task_data: Dict[str, Any]) -> AgentResult:
        """
        Process a review task.
        
        Args:
            task_data: Dictionary containing:
                - step_name: Name of the workflow step
                - content: Content to review
                - context: Optional context information
        """
        
        try:
            step_name = task_data.get("step_name", "unknown")
            content = task_data.get("content", "")
            context = task_data.get("context", {})
            
            review = self.review_step_output(step_name, content, context)
            
            return AgentResult(
                success=True,
                data={"review": review},
                messages=[f"Review completed for {step_name}"],
                metrics={
                    "quality_score": review.quality_score,
                    "confidence": review.confidence,
                    "issues_count": len(review.issues_found),
                    "suggestions_count": len(review.improvement_suggestions)
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "process_task")
