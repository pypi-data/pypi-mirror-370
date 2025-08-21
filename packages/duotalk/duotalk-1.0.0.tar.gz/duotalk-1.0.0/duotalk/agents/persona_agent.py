"""
Persona-specific agent implementations.
"""

from typing import Dict, Any, Optional
from .voice_agent import VoiceAgent
from ..core.config import AgentConfig


class PersonaAgent(VoiceAgent):
    """Agent with enhanced persona-specific behaviors."""
    
    def __init__(self, config: AgentConfig, topic: str = "", **kwargs):
        super().__init__(config, topic, **kwargs)
        
        # Persona-specific response patterns
        self.response_patterns = self._get_persona_patterns()
        self.interaction_style = self._get_interaction_style()
    
    def _get_persona_patterns(self) -> Dict[str, Any]:
        """Get response patterns specific to this persona."""
        patterns = {
            "optimist": {
                "openings": ["I think", "What if we", "Imagine if", "The good news is"],
                "transitions": ["Even better,", "Plus,", "And here's what's exciting:"],
                "sentiment": "positive",
                "focus": "solutions"
            },
            "pessimist": {
                "openings": ["But consider", "The problem is", "We should be careful", "What concerns me"],
                "transitions": ["However,", "Unfortunately,", "The issue is:"],
                "sentiment": "cautious", 
                "focus": "problems"
            },
            "pragmatist": {
                "openings": ["In practice", "What actually works", "From experience", "The reality is"],
                "transitions": ["Here's how:", "In the real world,", "Practically speaking:"],
                "sentiment": "neutral",
                "focus": "implementation"
            },
            "theorist": {
                "openings": ["Conceptually", "From a theoretical standpoint", "If we consider", "The framework suggests"],
                "transitions": ["This relates to", "In the broader context,", "Theoretically:"],
                "sentiment": "analytical",
                "focus": "concepts"
            },
            "skeptic": {
                "openings": ["How do we know", "What evidence", "I question whether", "Prove to me"],
                "transitions": ["But wait,", "That assumes,", "Where's the proof:"],
                "sentiment": "questioning",
                "focus": "evidence"
            },
            "enthusiast": {
                "openings": ["This is amazing!", "I love that", "How exciting that", "Absolutely!"],
                "transitions": ["Even more exciting,", "And get this,", "Plus:"],
                "sentiment": "energetic",
                "focus": "possibilities"
            },
            "mediator": {
                "openings": ["Both sides have merit", "Let's find common ground", "I see the value in", "Perhaps we can"],
                "transitions": ["On one hand,", "Considering both views,", "A compromise might be:"],
                "sentiment": "balanced",
                "focus": "harmony"
            },
            "analyst": {
                "openings": ["The data shows", "According to research", "Statistics indicate", "Analysis reveals"],
                "transitions": ["Furthermore,", "The numbers suggest,", "Evidence points to:"],
                "sentiment": "objective",
                "focus": "data"
            }
        }
        
        return patterns.get(self.config.persona, patterns["pragmatist"])
    
    def _get_interaction_style(self) -> Dict[str, Any]:
        """Get interaction style for this persona."""
        styles = {
            "optimist": {"interrupts_often": False, "builds_on_ideas": True, "challenges_directly": False},
            "pessimist": {"interrupts_often": True, "builds_on_ideas": False, "challenges_directly": True},
            "pragmatist": {"interrupts_often": False, "builds_on_ideas": True, "challenges_directly": True},
            "theorist": {"interrupts_often": False, "builds_on_ideas": True, "challenges_directly": False},
            "skeptic": {"interrupts_often": True, "builds_on_ideas": False, "challenges_directly": True},
            "enthusiast": {"interrupts_often": True, "builds_on_ideas": True, "challenges_directly": False},
            "mediator": {"interrupts_often": False, "builds_on_ideas": True, "challenges_directly": False},
            "analyst": {"interrupts_often": False, "builds_on_ideas": False, "challenges_directly": True},
        }
        
        default_style = {"interrupts_often": False, "builds_on_ideas": True, "challenges_directly": False}
        return styles.get(self.config.persona, default_style)
    
    def should_interrupt(self, current_speaker: str, conversation_context: Dict[str, Any]) -> bool:
        """Determine if this agent should interrupt based on persona."""
        if current_speaker == self.config.name:
            return False
            
        # Persona-specific interruption logic
        if self.interaction_style["interrupts_often"]:
            # Check if there's something to challenge or get excited about
            last_message = conversation_context.get("last_message", "")
            
            if self.config.persona in ["skeptic", "pessimist"]:
                # Interrupt if they disagree
                trigger_words = ["always", "never", "definitely", "impossible", "perfect"]
                return any(word in last_message.lower() for word in trigger_words)
            
            elif self.config.persona == "enthusiast":
                # Interrupt if excited about something
                trigger_words = ["amazing", "incredible", "breakthrough", "innovation"]
                return any(word in last_message.lower() for word in trigger_words)
        
        return False
    
    def get_response_style_prompt(self, context: Dict[str, Any]) -> str:
        """Get persona-specific style guidance for response generation."""
        patterns = self.response_patterns
        
        style_prompt = f"""
Response style for {self.config.name} ({self.config.persona}):

- Sentiment: {patterns['sentiment']}
- Focus on: {patterns['focus']}
- Use openings like: {', '.join(patterns['openings'][:2])}
- Use transitions like: {', '.join(patterns['transitions'][:2])}

Interaction style:
- Builds on others' ideas: {self.interaction_style['builds_on_ideas']}
- Challenges directly: {self.interaction_style['challenges_directly']}
"""
        
        return style_prompt
    
    async def generate_persona_response(
        self,
        prompt: str,
        conversation_context: Dict[str, Any],
        **kwargs
    ) -> str:
        """Generate a response that's true to the persona."""
        
        # Add persona-specific style guidance
        style_guidance = self.get_response_style_prompt(conversation_context)
        enhanced_prompt = f"{style_guidance}\n\nRespond to: {prompt}"
        
        # Update context with persona information
        enhanced_context = {**self.current_context, **conversation_context}
        enhanced_context["persona_style"] = self.response_patterns
        enhanced_context["interaction_style"] = self.interaction_style
        
        self.update_context(enhanced_context)
        
        return await self.generate_contextual_response(
            enhanced_prompt,
            include_history=True,
            **kwargs
        )


class DynamicPersonaAgent(PersonaAgent):
    """Agent that can adapt its persona based on conversation dynamics."""
    
    def __init__(self, config: AgentConfig, topic: str = "", **kwargs):
        super().__init__(config, topic, **kwargs)
        self.persona_intensity = 1.0  # How strongly to express persona (0.0 to 2.0)
        self.adaptation_rate = 0.1   # How quickly to adapt
    
    def adapt_persona_intensity(self, conversation_metrics: Dict[str, Any]) -> None:
        """Adapt persona intensity based on conversation dynamics."""
        
        # Get conversation metrics
        engagement_level = conversation_metrics.get("engagement_level", 0.5)
        conflict_level = conversation_metrics.get("conflict_level", 0.5)
        participation_balance = conversation_metrics.get("participation_balance", 0.5)
        
        # Adjust persona intensity
        if engagement_level < 0.3:
            # Low engagement - be more expressive
            self.persona_intensity = min(2.0, self.persona_intensity + self.adaptation_rate)
        elif engagement_level > 0.8:
            # High engagement - tone it down a bit
            self.persona_intensity = max(0.5, self.persona_intensity - self.adaptation_rate)
        
        # Adjust based on conflict
        if self.config.persona == "mediator" and conflict_level > 0.7:
            # Mediator becomes more active during high conflict
            self.persona_intensity = min(1.5, self.persona_intensity + self.adaptation_rate * 2)
        
        elif self.config.persona in ["skeptic", "pessimist"] and conflict_level > 0.8:
            # Reduce challenging behavior if conflict is too high
            self.persona_intensity = max(0.3, self.persona_intensity - self.adaptation_rate)
    
    def get_adapted_config(self) -> AgentConfig:
        """Get persona config adapted to current intensity."""
        adapted_config = self.config
        
        # Modify instructions based on intensity
        if self.persona_intensity < 0.5:
            adapted_config.instructions += " Be more gentle and measured in your responses."
        elif self.persona_intensity > 1.5:
            adapted_config.instructions += " Express your perspective more strongly and clearly."
        
        return adapted_config
