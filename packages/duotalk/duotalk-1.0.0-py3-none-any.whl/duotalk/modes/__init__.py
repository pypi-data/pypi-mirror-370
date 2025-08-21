"""
Conversation modes for different types of interactions.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModeConfig:
    """Configuration for a conversation mode."""
    name: str
    description: str
    recommended_agents: int
    turn_order: str  # "sequential", "random", "structured"
    interruptions_allowed: bool = True
    response_time_limit: float = 15.0
    context_sharing: bool = True


class ConversationMode(ABC):
    """Base class for conversation modes."""
    
    def __init__(self, config: ModeConfig):
        self.config = config
    
    @abstractmethod
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        """Get specific instructions for an agent in this mode."""
        pass
    
    @abstractmethod
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        """Determine which agent should speak next."""
        pass
    
    @abstractmethod
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        """Determine if the conversation should continue."""
        pass


class FriendlyMode(ConversationMode):
    """Collaborative, friendly conversation mode."""
    
    def __init__(self):
        config = ModeConfig(
            name="friendly",
            description="Collaborative discussion where agents build on each other's ideas",
            recommended_agents=2,
            turn_order="sequential",
            interruptions_allowed=True,
            response_time_limit=12.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        return f"""You are participating in a friendly, collaborative discussion about {context.get('topic', 'the topic')}.
        
Key guidelines:
- Build on what others have said
- Be supportive and encouraging
- Share your unique perspective
- Ask thoughtful questions
- Keep responses concise (1-2 sentences)
- Show genuine interest in other viewpoints"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        return turn_count % len(agents)
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 10)
        return turn_count < max_turns


class DebateMode(ConversationMode):
    """Structured debate between opposing viewpoints."""
    
    def __init__(self):
        config = ModeConfig(
            name="debate", 
            description="Structured debate with opposing viewpoints and rebuttals",
            recommended_agents=2,
            turn_order="sequential",
            interruptions_allowed=False,
            response_time_limit=20.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        if agent_index % 2 == 0:
            stance = "Take a supportive/positive stance"
        else:
            stance = "Take a critical/opposing stance"
            
        return f"""You are participating in a structured debate about {context.get('topic', 'the topic')}.
        
Your role: {stance}
        
Guidelines:
- Present clear arguments with reasoning
- Address counterpoints from the other side
- Use evidence when possible
- Maintain respectful disagreement
- Be persuasive but fair
- Keep responses focused (2-3 sentences)"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        return turn_count % len(agents)
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 8)
        return turn_count < max_turns


class RoundtableMode(ConversationMode):
    """Multi-participant roundtable discussion."""
    
    def __init__(self):
        config = ModeConfig(
            name="roundtable",
            description="Multi-participant discussion with diverse perspectives",
            recommended_agents=4,
            turn_order="sequential",
            interruptions_allowed=True,
            response_time_limit=15.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        return f"""You are one of {total_agents} participants in a roundtable discussion about {context.get('topic', 'the topic')}.
        
Guidelines:
- Contribute your unique perspective
- Reference what others have said
- Ask questions to other participants
- Build bridges between different viewpoints
- Keep contributions concise (1-2 sentences)
- Ensure everyone gets to participate"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        return turn_count % len(agents)
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 16)
        return turn_count < max_turns


class InterviewMode(ConversationMode):
    """Interview-style conversation with interviewer and interviewees."""
    
    def __init__(self):
        config = ModeConfig(
            name="interview",
            description="Interview format with one interviewer and multiple interviewees",
            recommended_agents=3,
            turn_order="structured", 
            interruptions_allowed=False,
            response_time_limit=18.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        if agent_index == 0:
            return f"""You are the interviewer for a discussion about {context.get('topic', 'the topic')}.
            
Your role:
- Ask probing questions
- Follow up on interesting points
- Guide the conversation
- Ensure all interviewees get to speak
- Keep the discussion focused"""
        else:
            return f"""You are an interviewee in a discussion about {context.get('topic', 'the topic')}.
            
Your role:
- Answer questions thoughtfully
- Share your expertise/perspective
- Provide examples when appropriate
- Ask clarifying questions if needed
- Be engaging and informative"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        # Interviewer speaks every other turn, interviewees rotate
        if turn_count % 2 == 0:
            return 0  # Interviewer
        else:
            interviewee_index = (turn_count // 2) % (len(agents) - 1)
            return interviewee_index + 1
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 12)
        return turn_count < max_turns


class PanelMode(ConversationMode):
    """Panel discussion with expert perspectives."""
    
    def __init__(self):
        config = ModeConfig(
            name="panel",
            description="Expert panel with moderator and specialists",
            recommended_agents=4,
            turn_order="structured",
            interruptions_allowed=True,
            response_time_limit=20.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        if agent_index == 0:
            return f"""You are the moderator for an expert panel on {context.get('topic', 'the topic')}.
            
Your role:
- Introduce topics and questions
- Manage the discussion flow
- Ensure balanced participation
- Synthesize different viewpoints
- Keep the discussion productive"""
        else:
            return f"""You are a panelist/expert in a discussion about {context.get('topic', 'the topic')}.
            
Your role:
- Share your specialized knowledge
- Provide professional insights
- Engage with other panelists' points
- Offer practical examples
- Maintain your expert perspective"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        if turn_count % 4 == 0:
            return 0  # Moderator introduces new topics
        else:
            panelist_index = ((turn_count - 1) % 3) + 1
            return panelist_index
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 16)
        return turn_count < max_turns


class SocraticMode(ConversationMode):
    """Socratic questioning method for deep exploration."""
    
    def __init__(self):
        config = ModeConfig(
            name="socratic",
            description="Question-driven exploration using Socratic method",
            recommended_agents=2,
            turn_order="sequential",
            interruptions_allowed=False,
            response_time_limit=25.0
        )
        super().__init__(config)
    
    def get_agent_instructions(self, agent_index: int, total_agents: int, context: Dict[str, Any]) -> str:
        if agent_index == 0:
            return f"""You are the Socratic questioner exploring {context.get('topic', 'the topic')}.
            
Your role:
- Ask probing questions that reveal assumptions
- Challenge statements with "Why?" and "How do you know?"
- Don't provide answers, only questions
- Guide toward deeper understanding
- Question definitions and premises"""
        else:
            return f"""You are responding to Socratic questioning about {context.get('topic', 'the topic')}.
            
Your role:
- Think carefully about each question
- Examine your own assumptions
- Provide honest, thoughtful responses
- Admit when you're uncertain
- Build on previous insights"""
    
    def get_turn_order(self, agents: List[Any], turn_count: int) -> int:
        return turn_count % len(agents)
    
    def should_continue(self, turn_count: int, context: Dict[str, Any]) -> bool:
        max_turns = context.get('max_turns', 10)
        return turn_count < max_turns


# Mode registry for easy access
AVAILABLE_MODES = {
    "friendly": FriendlyMode,
    "debate": DebateMode,
    "roundtable": RoundtableMode,
    "interview": InterviewMode,
    "panel": PanelMode,
    "socratic": SocraticMode,
}

# All available modes for easy reference
ALL_MODES = list(AVAILABLE_MODES.keys())


def get_mode(mode_name: str) -> ConversationMode:
    """Get a conversation mode by name."""
    if mode_name not in AVAILABLE_MODES:
        raise ValueError(f"Mode '{mode_name}' not available. Available modes: {list(AVAILABLE_MODES.keys())}")
    
    return AVAILABLE_MODES[mode_name]()
