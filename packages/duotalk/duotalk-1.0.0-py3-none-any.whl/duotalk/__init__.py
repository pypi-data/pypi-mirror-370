"""
DuoTalk - Advanced Multi-Agent Voice Conversation System

A comprehensive Python package for creating multi-agent voice conversations
with customizable personas, modes, and easy integration capabilities.

Example usage:
    ```python
    from duotalk import ConversationRunner, ConversationConfig
    from duotalk.personas import OPTIMIST, SKEPTIC
    from duotalk.modes import DebateMode
    
    # Simple conversation
    config = ConversationConfig(
        topic="Climate Change Solutions",
        agents=[OPTIMIST, SKEPTIC],
        mode=DebateMode(),
        max_turns=10
    )
    
    runner = ConversationRunner(config)
    await runner.start()
    ```
"""

from .core.runner import ConversationRunner
from .core.config import ConversationConfig, AgentConfig
from .core.session import ConversationSession
from .modes import (
    FriendlyMode,
    DebateMode,
    RoundtableMode,
    InterviewMode,
    PanelMode,
    SocraticMode,
)
from .personas import (
    OPTIMIST,
    PESSIMIST,
    PRAGMATIST,
    THEORIST,
    SKEPTIC,
    ENTHUSIAST,
    MEDIATOR,
    ANALYST,
    CREATIVE,
    LOGICAL,
)
from .agents.voice_agent import VoiceAgent
from .agents.persona_agent import PersonaAgent

# Convenience functions for quick setup
from .core.convenience import (
    create_debate,
    create_roundtable,
    create_friendly_chat,
    create_interview,
    create_panel,
    create_socratic,
    create_random_conversation,
    create_business_discussion,
    create_academic_debate,
    create_creative_brainstorm,
    create_policy_discussion,
)

__version__ = "1.0.0"
__author__ = "Abhyuday Patel"
__email__ = "your.email@example.com"

__all__ = [
    # Core classes
    "ConversationRunner",
    "ConversationConfig",
    "AgentConfig", 
    "ConversationSession",
    "VoiceAgent",
    "PersonaAgent",
    
    # Conversation modes
    "FriendlyMode",
    "DebateMode", 
    "RoundtableMode",
    "InterviewMode",
    "PanelMode",
    "SocraticMode",
    
    # Pre-defined personas
    "OPTIMIST",
    "PESSIMIST",
    "PRAGMATIST",
    "THEORIST",
    "SKEPTIC",
    "ENTHUSIAST",
    "MEDIATOR",
    "ANALYST",
    "CREATIVE",
    "LOGICAL",
    
    # Convenience functions
    "create_debate",
    "create_roundtable", 
    "create_friendly_chat",
    "create_interview",
    "create_custom_conversation",
]
