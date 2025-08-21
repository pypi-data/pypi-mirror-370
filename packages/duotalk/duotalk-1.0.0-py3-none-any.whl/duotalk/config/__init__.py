"""
Configuration classes for DuoTalk conversations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, validator


class VoiceType(str, Enum):
    """Available voice types for agents."""
    PUCK = "Puck"
    CHARON = "Charon"
    KORE = "Kore"
    FENRIR = "Fenrir"
    AOEDE = "Aoede"


class ConversationModeType(str, Enum):
    """Available conversation modes."""
    FRIENDLY = "friendly"
    DEBATE = "debate"
    ROUNDTABLE = "roundtable" 
    INTERVIEW = "interview"
    PANEL = "panel"
    SOCRATIC = "socratic"
    CUSTOM = "custom"


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    name: str
    persona: str
    role: str
    perspective: str
    voice: VoiceType = VoiceType.PUCK
    instructions: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    custom_prompt: Optional[str] = None
    
    def __post_init__(self):
        if self.instructions is None:
            self.instructions = f"You are {self.name}, a {self.persona} with a {self.perspective} perspective."


@dataclass 
class ConversationConfig:
    """Main configuration for a conversation."""
    topic: str
    agents: List[AgentConfig]
    mode: str = ConversationModeType.FRIENDLY
    max_turns: int = 10
    turn_timeout: float = 15.0
    allow_interruptions: bool = True
    min_interruption_duration: float = 0.3
    conversation_timeout: Optional[float] = None
    
    # Audio settings
    audio_enabled: bool = True
    sample_rate: int = 48000
    channels: int = 1
    
    # Model settings
    model_name: str = "gemini-2.5-flash-preview-native-audio-dialog"
    api_key: Optional[str] = None
    
    # Session settings
    session_name: Optional[str] = None
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Logging
    log_level: str = "INFO"
    log_conversation: bool = True
    save_audio: bool = False
    output_dir: Optional[str] = None
    
    # Advanced settings
    context_window: int = 5  # Number of previous messages to include as context
    response_filtering: bool = True
    profanity_filter: bool = False
    sentiment_analysis: bool = False
    
    def __post_init__(self):
        if len(self.agents) < 2:
            raise ValueError("At least 2 agents are required for a conversation")
        if len(self.agents) > 10:
            raise ValueError("Maximum 10 agents allowed per conversation")
        
        # Set default session name if not provided
        if self.session_name is None:
            agent_names = [agent.name for agent in self.agents]
            self.session_name = f"{'-'.join(agent_names[:3])}-{self.mode}"
    
    @validator('max_turns')
    def validate_max_turns(cls, v):
        if v < 1 or v > 100:
            raise ValueError("max_turns must be between 1 and 100")
        return v
    
    @validator('turn_timeout')
    def validate_turn_timeout(cls, v):
        if v < 1.0 or v > 60.0:
            raise ValueError("turn_timeout must be between 1.0 and 60.0 seconds")
        return v


class EnvironmentConfig(BaseModel):
    """Environment and API configuration."""
    
    # API Keys
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # LiveKit settings
    livekit_url: Optional[str] = None
    livekit_region: str = "us-west-2"
    
    # Development settings
    debug_mode: bool = False
    dev_mode: bool = False
    test_mode: bool = False
    
    # Logging
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
