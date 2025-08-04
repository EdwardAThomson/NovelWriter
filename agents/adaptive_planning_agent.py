"""
Adaptive Planning Agent for NovelWriter.

Handles dynamic story arc adjustment and adaptive planning.
"""

from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

from agents.base.agent import BaseAgent, AgentResult

class ArcAdjustmentType(Enum):
    PACING = "pacing"
    CHARACTER_DEV = "character_development"
    PLOT_TWIST = "plot_twist"
    SUBPLOT = "subplot_addition"
    THEME = "theme_emphasis"
    TENSION = "tension_adjustment"

@dataclass
class ArcAnalysis:
    current_state: Dict[str, Any]
    issues: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    metrics: Dict[str, float]

@dataclass
class ArcProposal:
    adjustment_type: ArcAdjustmentType
    description: str
    impact: str
    implementation: str
    confidence: float
    priority: int

class AdaptivePlanningAgent(BaseAgent):
    """Agent for dynamic story arc adjustment and planning."""
    
    def __init__(self, model: str = "gpt-4o", logger: Optional[logging.Logger] = None):
        super().__init__(name="AdaptivePlanningAgent", model=model, logger=logger)
        self.analysis_history: List[Dict] = []
        
    def analyze_story_arc(self, story_data: Dict[str, Any]) -> ArcAnalysis:
        """
        Analyze the current story arc state across multiple dimensions.
        
        Args:
            story_data: Dictionary containing story elements like chapters, characters, plot points
            
        Returns:
            ArcAnalysis object containing analysis results
        """
        try:
            # Initialize analysis structure
            analysis = {
                "current_state": {
                    "pacing": {},
                    "character_development": {},
                    "plot_structure": {},
                    "themes": {},
                    "tension_arc": {}
                },
                "issues": [],
                "opportunities": [],
                "metrics": {
                    "pacing_score": 0.0,
                    "character_development_score": 0.0,
                    "plot_cohesion_score": 0.0,
                    "theme_consistency_score": 0.0,
                    "tension_variation_score": 0.0
                }
            }
            
            # 1. Analyze Pacing
            pacing_analysis = self._analyze_pacing(story_data)
            analysis["current_state"]["pacing"] = pacing_analysis["state"]
            analysis["issues"].extend(pacing_analysis["issues"])
            analysis["opportunities"].extend(pacing_analysis["opportunities"])
            analysis["metrics"]["pacing_score"] = pacing_analysis["score"]
            
            # 2. Analyze Character Development
            char_analysis = self._analyze_character_development(story_data)
            analysis["current_state"]["character_development"] = char_analysis["state"]
            analysis["issues"].extend(char_analysis["issues"])
            analysis["opportunities"].extend(char_analysis["opportunities"])
            analysis["metrics"]["character_development_score"] = char_analysis["score"]
            
            # 3. Analyze Plot Structure
            plot_analysis = self._analyze_plot_structure(story_data)
            analysis["current_state"]["plot_structure"] = plot_analysis["state"]
            analysis["issues"].extend(plot_analysis["issues"])
            analysis["opportunities"].extend(plot_analysis["opportunities"])
            analysis["metrics"]["plot_cohesion_score"] = plot_analysis["score"]
            
            # 4. Analyze Themes
            theme_analysis = self._analyze_themes(story_data)
            analysis["current_state"]["themes"] = theme_analysis["state"]
            analysis["issues"].extend(theme_analysis["issues"])
            analysis["opportunities"].extend(theme_analysis["opportunities"])
            analysis["metrics"]["theme_consistency_score"] = theme_analysis["score"]
            
            # 5. Analyze Tension Arc
            tension_analysis = self._analyze_tension_arc(story_data)
            analysis["current_state"]["tension_arc"] = tension_analysis["state"]
            analysis["issues"].extend(tension_analysis["issues"])
            analysis["opportunities"].extend(tension_analysis["opportunities"])
            analysis["metrics"]["tension_variation_score"] = tension_analysis["score"]
            
            # Store this analysis in history
            self.analysis_history.append({
                "timestamp": self._get_timestamp(),
                "analysis": analysis.copy()
            })
            
            return ArcAnalysis(**analysis)
            
        except Exception as e:
            self.logger.error(f"Error in analyze_story_arc: {e}")
            # Return empty analysis with error state
            return ArcAnalysis(
                current_state={"error": str(e)},
                issues=[{"type": "error", "message": f"Analysis failed: {e}"}],
                opportunities=[],
                metrics={}
            )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
        
    def _analyze_pacing(self, story_data: Dict) -> Dict:
        """Analyze story pacing."""
        # Implementation would analyze chapter lengths, scene distribution, etc.
        return {
            "state": {
                "chapters": len(story_data.get("chapters", [])),
                "scenes_per_chapter": self._calculate_scenes_per_chapter(story_data),
                "chapter_lengths": self._calculate_chapter_lengths(story_data)
            },
            "issues": [],  # Will be populated with pacing issues
            "opportunities": [],  # Will suggest pacing improvements
            "score": 0.8  # Example score (0-1)
        }
        
    def _analyze_character_development(self, story_data: Dict) -> Dict:
        """Analyze character development and arcs."""
        return {
            "state": {
                "character_count": len(story_data.get("characters", [])),
                "character_arcs": self._extract_character_arcs(story_data)
            },
            "issues": [],
            "opportunities": [],
            "score": 0.7
        }
        
    def _analyze_plot_structure(self, story_data: Dict) -> Dict:
        """Analyze plot structure and coherence."""
        return {
            "state": {
                "plot_points": story_data.get("plot_points", []),
                "subplots": self._identify_subplots(story_data)
            },
            "issues": [],
            "opportunities": [],
            "score": 0.75
        }
        
    def _analyze_themes(self, story_data: Dict) -> Dict:
        """Analyze thematic elements and consistency."""
        return {
            "state": {
                "themes": self._extract_themes(story_data),
                "theme_development": self._analyze_theme_development(story_data)
            },
            "issues": [],
            "opportunities": [],
            "score": 0.85
        }
        
    def _analyze_tension_arc(self, story_data: Dict) -> Dict:
        """Analyze tension and emotional arcs."""
        return {
            "state": {
                "tension_points": self._identify_tension_points(story_data),
                "emotional_arc": self._analyze_emotional_arc(story_data)
            },
            "issues": [],
            "opportunities": [],
            "score": 0.78
        }
        
    # Helper methods for analysis
    def _calculate_scenes_per_chapter(self, story_data: Dict) -> List[int]:
        """Calculate number of scenes per chapter."""
        return [len(chapter.get("scenes", [])) for chapter in story_data.get("chapters", [])]
        
    def _calculate_chapter_lengths(self, story_data: Dict) -> List[int]:
        """Calculate word count per chapter."""
        return [len(chapter.get("content", "").split()) for chapter in story_data.get("chapters", [])]
        
    def _extract_character_arcs(self, story_data: Dict) -> Dict:
        """Extract and analyze character arcs."""
        return {}
        
    def _identify_subplots(self, story_data: Dict) -> List[Dict]:
        """Identify and analyze subplots."""
        return []
        
    def _extract_themes(self, story_data: Dict) -> List[str]:
        """Extract major themes from the story."""
        return []
        
    def _analyze_theme_development(self, story_data: Dict) -> Dict:
        """Analyze how themes develop throughout the story."""
        return {}
        
    def _identify_tension_points(self, story_data: Dict) -> List[Dict]:
        """Identify key tension points in the story."""
        return []
        
    def _analyze_emotional_arc(self, story_data: Dict) -> Dict:
        """Analyze the emotional arc of the story."""
        return {}
        
    def propose_adjustments(self, analysis: ArcAnalysis) -> List[ArcProposal]:
        """Generate adjustment proposals based on analysis."""
        proposals = []
        
        # Generate pacing adjustments
        if analysis.metrics.get("pacing_score", 0) < 0.7:
            proposals.append(ArcProposal(
                adjustment_type=ArcAdjustmentType.PACING,
                description="Pacing is uneven in middle chapters",
                impact="Improves reader engagement and flow",
                implementation="Add a subplot or adjust chapter lengths",
                confidence=0.8,
                priority=2
            ))
            
        # Generate character development adjustments
        if analysis.metrics.get("character_development_score", 0) < 0.6:
            proposals.append(ArcProposal(
                adjustment_type=ArcAdjustmentType.CHARACTER_DEV,
                description="Side characters need more development",
                impact="Enhances reader connection to characters",
                implementation="Add character moments or backstory scenes",
                confidence=0.9,
                priority=1
            ))
            
        # Sort proposals by priority (highest first)
        return sorted(proposals, key=lambda x: x.priority, reverse=True)
    
    def apply_adjustment(self, proposal: ArcProposal, story_data: Dict) -> Dict:
        """Apply a proposed adjustment to the story."""
        # Implementation would adjust story data
        return story_data
    
    def get_available_tools(self) -> List[str]:
        """Return list of available tools for this agent."""
        return [
            "analyze_story_arc",
            "propose_adjustments",
            "apply_adjustment"
        ]
        
    def get_required_fields(self, tool_name: str) -> List[str]:
        """Return required fields for a given tool."""
        requirements = {
            "analyze_story_arc": ["story_data"],
            "propose_adjustments": ["analysis"],
            "apply_adjustment": ["proposal", "story_data"]
        }
        return requirements.get(tool_name, [])
    
    def process_task(self, task_data: Dict) -> AgentResult:
        """Process an adaptive planning task."""
        try:
            task_type = task_data.get("type")
            params = task_data.get("parameters", {})
            
            # Validate required fields
            required_fields = self.get_required_fields(task_type)
            missing_fields = [f for f in required_fields if f not in params]
            if missing_fields:
                return AgentResult(
                    success=False,
                    data={},
                    messages=[f"Missing required fields: {', '.join(missing_fields)}"],
                    metrics={}
                )
            
            if task_type == "analyze_story_arc":
                analysis = self.analyze_story_arc(params.get("story_data", {}))
                return AgentResult(
                    success=True, 
                    data={"analysis": analysis},
                    messages=["Story arc analysis completed successfully"],
                    metrics={}
                )
                
            elif task_type == "propose_adjustments":
                analysis = params.get("analysis")
                proposals = self.propose_adjustments(analysis)
                return AgentResult(
                    success=True, 
                    data={"proposals": proposals},
                    messages=["Adjustment proposals generated successfully"],
                    metrics={}
                )
                
            elif task_type == "apply_adjustment":
                proposal = params.get("proposal")
                story_data = params.get("story_data", {})
                updated_story = self.apply_adjustment(proposal, story_data)
                return AgentResult(
                    success=True, 
                    data={"updated_story": updated_story},
                    messages=["Adjustment applied successfully"],
                    metrics={}
                )
                
            else:
                return AgentResult(
                    success=False, 
                    data={},
                    messages=[f"Unknown task type: {task_type}"],
                    metrics={}
                )
                
        except Exception as e:
            self.logger.error(f"Error in process_task: {e}")
            return AgentResult(
                success=False,
                data={},
                messages=[str(e)],
                metrics={}
            )
