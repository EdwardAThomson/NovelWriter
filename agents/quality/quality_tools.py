"""
Quality analysis tools for NovelWriter agents.

These tools provide specific, focused functionality for evaluating
different aspects of story quality and coherence.
"""

from typing import Dict, List, Any, Optional
import re
import json
from dataclasses import dataclass

from agents.base.tool import BaseTool, ToolParameter, ToolResult, ToolAccessLevel
from core.generation.ai_helper import send_prompt


@dataclass
class QualityMetrics:
    """Quality metrics for story content."""
    coherence_score: float  # 0.0 - 1.0
    pacing_score: float     # 0.0 - 1.0
    prose_quality: float    # 0.0 - 1.0
    character_consistency: float  # 0.0 - 1.0
    dialogue_quality: float  # 0.0 - 1.0
    
    def overall_score(self) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            'coherence': 0.25,
            'pacing': 0.20,
            'prose': 0.20,
            'character': 0.20,
            'dialogue': 0.15
        }
        
        return (
            self.coherence_score * weights['coherence'] +
            self.pacing_score * weights['pacing'] +
            self.prose_quality * weights['prose'] +
            self.character_consistency * weights['character'] +
            self.dialogue_quality * weights['dialogue']
        )


class AnalyzeCoherenceTool(BaseTool):
    """Tool to analyze chapter coherence and logical flow."""
    
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(
            name="analyze_coherence",
            description="Analyze the logical coherence and flow of a chapter or scene",
            access_level=ToolAccessLevel.PUBLIC
        )
        self.model = model
    
    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="content",
                type="string",
                description="The chapter or scene content to analyze",
                examples=["Chapter text content here..."]
            ),
            ToolParameter(
                name="context",
                type="object",
                description="Previous chapters and story context",
                required=False,
                examples=[{"previous_chapters": ["Chapter 1 text...", "Chapter 2 text..."]}]
            ),
            ToolParameter(
                name="genre",
                type="string",
                description="Story genre for context-appropriate analysis",
                required=False,
                examples=["science_fiction", "fantasy", "mystery"]
            )
        ]
    
    def _define_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Analyze chapter coherence",
                "parameters": {
                    "content": "Chapter content here...",
                    "genre": "science_fiction"
                },
                "expected_result": {
                    "coherence_score": 0.85,
                    "issues": ["Minor plot inconsistency in paragraph 3"],
                    "suggestions": ["Clarify the timeline of events"]
                }
            }
        ]
    
    def _execute(self, **kwargs) -> ToolResult:
        content = kwargs["content"]
        context = kwargs.get("context", {})
        genre = kwargs.get("genre", "general")
        
        try:
            # Create analysis prompt
            prompt = self._create_coherence_prompt(content, context, genre)
            
            # Get LLM analysis
            response = send_prompt(prompt, model=self.model)
            
            # Parse response
            analysis = self._parse_coherence_response(response)
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={"model_used": self.model, "content_length": len(content)}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Coherence analysis failed: {str(e)}"
            )
    
    def _create_coherence_prompt(self, content: str, context: Dict, genre: str) -> str:
        """Create prompt for coherence analysis."""
        prompt = f"""
Analyze the coherence and logical flow of this {genre} story content.

CONTENT TO ANALYZE:
{content}

ANALYSIS CRITERIA:
1. Logical flow and sequence of events
2. Internal consistency within the content
3. Character behavior consistency
4. Plot development coherence
5. Setting and world-building consistency

Please provide your analysis in the following JSON format:
{{
    "coherence_score": 0.0-1.0,
    "issues": ["list of specific issues found"],
    "suggestions": ["list of improvement suggestions"],
    "strengths": ["list of coherent elements"],
    "detailed_analysis": "paragraph explaining the analysis"
}}

Focus on specific, actionable feedback that can help improve the content.
"""
        
        if context.get("previous_chapters"):
            prompt += f"\n\nPREVIOUS CONTEXT:\n{context['previous_chapters'][-1][:500]}..."
        
        return prompt
    
    def _parse_coherence_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured analysis."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {
                    "coherence_score": 0.7,  # Default score
                    "issues": ["Could not parse detailed analysis"],
                    "suggestions": ["Review content manually"],
                    "strengths": [],
                    "detailed_analysis": response
                }
        except json.JSONDecodeError:
            return {
                "coherence_score": 0.7,
                "issues": ["Analysis parsing failed"],
                "suggestions": ["Review content manually"],
                "strengths": [],
                "detailed_analysis": response
            }


class AnalyzePacingTool(BaseTool):
    """Tool to analyze story pacing and rhythm."""
    
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(
            name="analyze_pacing",
            description="Analyze the pacing and rhythm of story content",
            access_level=ToolAccessLevel.PUBLIC
        )
        self.model = model
    
    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="content",
                type="string",
                description="The content to analyze for pacing"
            ),
            ToolParameter(
                name="target_pacing",
                type="string",
                description="Desired pacing (fast, medium, slow, varied)",
                required=False,
                default="medium",
                examples=["fast", "medium", "slow", "varied"]
            ),
            ToolParameter(
                name="scene_type",
                type="string",
                description="Type of scene (action, dialogue, exposition, transition)",
                required=False,
                examples=["action", "dialogue", "exposition", "transition"]
            )
        ]
    
    def _execute(self, **kwargs) -> ToolResult:
        content = kwargs["content"]
        target_pacing = kwargs.get("target_pacing", "medium")
        scene_type = kwargs.get("scene_type", "general")
        
        try:
            # Analyze sentence structure for pacing indicators
            structural_analysis = self._analyze_structure(content)
            
            # Get LLM pacing analysis
            prompt = self._create_pacing_prompt(content, target_pacing, scene_type)
            response = send_prompt(prompt, model=self.model)
            llm_analysis = self._parse_pacing_response(response)
            
            # Combine analyses
            analysis = {
                **structural_analysis,
                **llm_analysis,
                "target_pacing": target_pacing,
                "scene_type": scene_type
            }
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={"model_used": self.model}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Pacing analysis failed: {str(e)}"
            )
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze structural elements that affect pacing."""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"pacing_score": 0.5, "structural_notes": ["No sentences found"]}
        
        # Calculate metrics
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        short_sentences = sum(1 for s in sentences if len(s.split()) < 10)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 20)
        
        # Determine pacing based on structure
        if avg_sentence_length < 12:
            pacing_indicator = "fast"
            pacing_score = 0.8
        elif avg_sentence_length > 18:
            pacing_indicator = "slow"
            pacing_score = 0.6
        else:
            pacing_indicator = "medium"
            pacing_score = 0.75
        
        return {
            "structural_pacing": pacing_indicator,
            "avg_sentence_length": avg_sentence_length,
            "short_sentences_ratio": short_sentences / len(sentences),
            "long_sentences_ratio": long_sentences / len(sentences),
            "total_sentences": len(sentences)
        }
    
    def _create_pacing_prompt(self, content: str, target_pacing: str, scene_type: str) -> str:
        """Create prompt for pacing analysis."""
        return f"""
Analyze the pacing and rhythm of this {scene_type} scene content.

TARGET PACING: {target_pacing}
CONTENT:
{content}

ANALYSIS CRITERIA:
1. Sentence rhythm and variation
2. Paragraph flow
3. Tension building/release
4. Information delivery rate
5. Appropriateness for scene type

Provide analysis in JSON format:
{{
    "pacing_score": 0.0-1.0,
    "current_pacing": "fast/medium/slow/varied",
    "matches_target": true/false,
    "pacing_issues": ["specific issues"],
    "pacing_suggestions": ["improvement suggestions"],
    "rhythm_analysis": "detailed analysis of rhythm and flow"
}}
"""
    
    def _parse_pacing_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM pacing analysis response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback
        return {
            "pacing_score": 0.7,
            "current_pacing": "medium",
            "matches_target": True,
            "pacing_issues": [],
            "pacing_suggestions": [],
            "rhythm_analysis": response
        }


class EvaluateProseQualityTool(BaseTool):
    """Tool to evaluate prose quality and style."""
    
    def __init__(self, model: str = "gpt-4o"):
        super().__init__(
            name="evaluate_prose_quality",
            description="Evaluate the quality of prose writing including style, clarity, and engagement",
            access_level=ToolAccessLevel.PUBLIC
        )
        self.model = model
    
    def _define_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="content",
                type="string",
                description="The prose content to evaluate"
            ),
            ToolParameter(
                name="style_target",
                type="string",
                description="Target writing style",
                required=False,
                examples=["literary", "commercial", "young_adult", "middle_grade"]
            ),
            ToolParameter(
                name="genre_standards",
                type="object",
                description="Genre-specific quality standards",
                required=False
            )
        ]
    
    def _execute(self, **kwargs) -> ToolResult:
        content = kwargs["content"]
        style_target = kwargs.get("style_target", "commercial")
        genre_standards = kwargs.get("genre_standards", {})
        
        try:
            # Basic prose analysis
            basic_analysis = self._basic_prose_analysis(content)
            
            # LLM quality evaluation
            prompt = self._create_prose_prompt(content, style_target, genre_standards)
            response = send_prompt(prompt, model=self.model)
            quality_analysis = self._parse_prose_response(response)
            
            # Combine analyses
            analysis = {
                **basic_analysis,
                **quality_analysis,
                "style_target": style_target
            }
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={"model_used": self.model}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Prose quality evaluation failed: {str(e)}"
            )
    
    def _basic_prose_analysis(self, content: str) -> Dict[str, Any]:
        """Perform basic statistical analysis of prose."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {"prose_score": 0.5, "analysis_notes": ["Insufficient content"]}
        
        # Calculate readability metrics
        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)
        
        # Count adverbs (simple heuristic)
        adverbs = sum(1 for word in words if word.lower().endswith('ly'))
        adverb_ratio = adverbs / len(words)
        
        # Count dialogue
        dialogue_lines = content.count('"')
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": avg_words_per_sentence,
            "avg_chars_per_word": avg_chars_per_word,
            "adverb_ratio": adverb_ratio,
            "dialogue_indicators": dialogue_lines
        }
    
    def _create_prose_prompt(self, content: str, style_target: str, genre_standards: Dict) -> str:
        """Create prompt for prose quality evaluation."""
        return f"""
Evaluate the prose quality of this {style_target} style content.

CONTENT:
{content}

EVALUATION CRITERIA:
1. Clarity and readability
2. Sentence variety and flow
3. Word choice and vocabulary
4. Show vs. tell balance
5. Engagement and voice
6. Technical writing quality

Provide evaluation in JSON format:
{{
    "prose_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "engagement_score": 0.0-1.0,
    "style_consistency": 0.0-1.0,
    "strengths": ["list of prose strengths"],
    "weaknesses": ["list of areas for improvement"],
    "specific_suggestions": ["actionable improvement suggestions"],
    "overall_assessment": "detailed prose analysis"
}}
"""
    
    def _parse_prose_response(self, response: str) -> Dict[str, Any]:
        """Parse prose quality evaluation response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {
            "prose_score": 0.7,
            "clarity_score": 0.7,
            "engagement_score": 0.7,
            "style_consistency": 0.7,
            "strengths": [],
            "weaknesses": [],
            "specific_suggestions": [],
            "overall_assessment": response
        }
