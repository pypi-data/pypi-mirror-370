"""
Convenience functions for quickly creating conversations.
"""

from typing import List, Optional, Union, Dict, Any
import random

from .config import ConversationConfig, AgentConfig
from ..personas import (
    OPTIMIST, PESSIMIST, PRAGMATIST, THEORIST, SKEPTIC, ENTHUSIAST,
    MEDIATOR, ANALYST, CREATIVE, LOGICAL, EDUCATOR, ENTREPRENEUR,
    SCIENTIST, ARTIST, ALL_PERSONAS
)


def get_persona_by_name(persona_name: str) -> AgentConfig:
    """Get persona by name."""
    persona_map = {
        'optimist': OPTIMIST,
        'pessimist': PESSIMIST,
        'pragmatist': PRAGMATIST,
        'theorist': THEORIST,
        'skeptic': SKEPTIC,
        'enthusiast': ENTHUSIAST,
        'mediator': MEDIATOR,
        'analyst': ANALYST,
        'creative': CREATIVE,
        'logical thinker': LOGICAL,
        'educator': EDUCATOR,
        'entrepreneur': ENTREPRENEUR,
        'scientist': SCIENTIST,
        'artist': ARTIST,
    }
    
    if persona_name not in persona_map:
        raise ValueError(f"Persona '{persona_name}' not found. Available: {list(persona_map.keys())}")
    
    return persona_map[persona_name]


def create_debate(
    topic: str,
    personas: Optional[List[str]] = None,
    max_turns: int = 8,
    **kwargs
) -> ConversationConfig:
    """
    Create a debate conversation configuration.
    
    Args:
        topic: The topic to debate
        personas: List of persona names (defaults to ['optimist', 'skeptic'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if personas is None:
        personas = ['optimist', 'skeptic']
    
    # Get agents from persona names
    agents = [get_persona_by_name(persona) for persona in personas]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="debate",
        max_turns=max_turns,
        **kwargs
    )


def create_roundtable(
    topic: str,
    personas: Optional[List[str]] = None,
    max_turns: int = 12,
    **kwargs
) -> ConversationConfig:
    """
    Create a roundtable discussion configuration.
    
    Args:
        topic: The topic to discuss
        personas: List of persona names (defaults to ['pragmatist', 'theorist', 'skeptic'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if personas is None:
        personas = ['pragmatist', 'theorist', 'skeptic']
    
    agents = [get_persona_by_name(persona) for persona in personas]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="roundtable",
        max_turns=max_turns,
        **kwargs
    )


def create_interview(
    topic: str,
    interviewer: Optional[str] = None,
    interviewees: Optional[List[str]] = None,
    max_turns: int = 10,
    **kwargs
) -> ConversationConfig:
    """
    Create an interview conversation configuration.
    
    Args:
        topic: The interview topic
        interviewer: Interviewer persona name (defaults to 'mediator')
        interviewees: List of interviewee persona names (defaults to ['scientist', 'entrepreneur'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if interviewer is None:
        interviewer = 'mediator'
    if interviewees is None:
        interviewees = ['scientist', 'entrepreneur']
    
    agents = [get_persona_by_name(interviewer)] + [get_persona_by_name(name) for name in interviewees]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="interview",
        max_turns=max_turns,
        **kwargs
    )


def create_panel(
    topic: str,
    moderator: Optional[str] = None,
    panelists: Optional[List[str]] = None,
    max_turns: int = 15,
    **kwargs
) -> ConversationConfig:
    """
    Create a panel discussion configuration.
    
    Args:
        topic: The panel topic
        moderator: Moderator persona name (defaults to 'mediator')
        panelists: List of panelist persona names (defaults to ['scientist', 'entrepreneur', 'educator'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if moderator is None:
        moderator = 'mediator'
    if panelists is None:
        panelists = ['scientist', 'entrepreneur', 'educator']
    
    agents = [get_persona_by_name(moderator)] + [get_persona_by_name(name) for name in panelists]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="panel",
        max_turns=max_turns,
        **kwargs
    )


def create_socratic(
    topic: str,
    personas: Optional[List[str]] = None,
    max_turns: int = 10,
    **kwargs
) -> ConversationConfig:
    """
    Create a Socratic dialogue configuration.
    
    Args:
        topic: The topic to explore
        personas: List of persona names (defaults to ['theorist', 'skeptic'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if personas is None:
        personas = ['theorist', 'skeptic']
    
    agents = [get_persona_by_name(persona) for persona in personas]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="socratic",
        max_turns=max_turns,
        **kwargs
    )


def create_friendly_chat(
    topic: str,
    personas: Optional[List[str]] = None,
    max_turns: int = 8,
    **kwargs
) -> ConversationConfig:
    """
    Create a friendly chat conversation configuration.
    
    Args:
        topic: The topic to chat about
        personas: List of persona names (defaults to ['optimist', 'enthusiast'])
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if personas is None:
        personas = ['optimist', 'enthusiast']
    
    agents = [get_persona_by_name(persona) for persona in personas]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode="friendly",
        max_turns=max_turns,
        **kwargs
    )


def get_random_personas(count: int = 2) -> List[str]:
    """
    Get random persona names.
    
    Args:
        count: Number of personas to select
        
    Returns:
        List of random persona names
    """
    persona_names = [
        'optimist', 'pessimist', 'pragmatist', 'theorist', 'skeptic',
        'enthusiast', 'mediator', 'analyst', 'creative', 'logical thinker',
        'educator', 'entrepreneur', 'scientist', 'artist'
    ]
    
    return random.sample(persona_names, min(count, len(persona_names)))


def create_random_conversation(
    topic: str,
    mode: Optional[str] = None,
    persona_count: int = 2,
    max_turns: int = 10,
    **kwargs
) -> ConversationConfig:
    """
    Create a random conversation configuration.
    
    Args:
        topic: The conversation topic
        mode: Conversation mode (defaults to random selection)
        persona_count: Number of personas to include
        max_turns: Maximum number of turns
        **kwargs: Additional configuration options
        
    Returns:
        ConversationConfig ready for use
    """
    if mode is None:
        modes = ['friendly', 'debate', 'roundtable', 'socratic']
        mode = random.choice(modes)
    
    personas = get_random_personas(persona_count)
    agents = [get_persona_by_name(persona) for persona in personas]
    
    return ConversationConfig(
        topic=topic,
        agents=agents,
        mode=mode,
        max_turns=max_turns,
        **kwargs
    )


# Preset conversation creators for common scenarios
def create_business_discussion(topic: str) -> ConversationConfig:
    """Create a business-focused discussion."""
    return create_roundtable(topic, ['entrepreneur', 'analyst', 'pragmatist'])


def create_academic_debate(topic: str) -> ConversationConfig:
    """Create an academic-style debate."""
    return create_debate(topic, ['scientist', 'theorist'])


def create_creative_brainstorm(topic: str) -> ConversationConfig:
    """Create a creative brainstorming session."""
    return create_friendly_chat(topic, ['creative', 'enthusiast', 'artist'])


def create_policy_discussion(topic: str) -> ConversationConfig:
    """Create a policy discussion."""
    return create_panel(topic, 'mediator', ['pragmatist', 'analyst', 'educator'])
