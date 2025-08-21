"""
Voice agent implementation for DuoTalk.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from livekit.agents.voice import Agent
from livekit.plugins.google.beta.realtime import RealtimeModel
from ..core.config import AgentConfig


logger = logging.getLogger(__name__)


class VoiceAgent(Agent):
    """Enhanced voice agent with persona support."""
    
    def __init__(
        self,
        config: AgentConfig,
        topic: str = "",
        model_name: str = "gemini-2.5-flash-preview-native-audio-dialog",
        **kwargs
    ):
        """Initialize the voice agent with configuration."""
        
        # Build comprehensive instructions
        instructions = self._build_instructions(config, topic)
        
        super().__init__(instructions=instructions, **kwargs)
        
        self.config = config
        self.topic = topic
        self.model_name = model_name
        self.conversation_history = []
        self.current_context = {}
        
        # Performance metrics
        self.total_responses = 0
        self.total_errors = 0
        self.average_response_time = 0.0
        
        logger.info(f"Initialized VoiceAgent: {config.name} ({config.persona})")
    
    def _build_instructions(self, config: AgentConfig, topic: str) -> str:
        """Build comprehensive instructions for the agent."""
        
        base_instructions = f"""You are {config.name}, a {config.persona} with a {config.perspective} perspective.

Your role: {config.role}
Topic: {topic}

Core personality traits:
- {config.instructions}

Conversation guidelines:
- Stay in character as {config.name}
- Keep responses concise (1-2 sentences to save API costs)
- Be engaging and contribute unique viewpoints
- Build on previous conversation points
- Maintain your {config.perspective} perspective
"""
        
        if config.custom_prompt:
            base_instructions += f"\n\nCustom instructions:\n{config.custom_prompt}"
            
        return base_instructions
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """Update agent's conversation context."""
        self.current_context.update(context)
        logger.debug(f"{self.config.name} context updated: {list(context.keys())}")
    
    def add_to_history(self, speaker: str, message: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Keep only recent history to manage memory
        max_history = self.current_context.get("context_window", 10)
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
    
    def get_context_for_response(self) -> str:
        """Get relevant context for generating response."""
        if not self.conversation_history:
            return ""
            
        recent_messages = self.conversation_history[-3:]  # Last 3 messages
        context_parts = []
        
        for msg in recent_messages:
            if msg["speaker"] != self.config.name:  # Don't include own messages
                context_parts.append(f"{msg['speaker']}: {msg['message']}")
        
        if context_parts:
            return f"Recent conversation:\n" + "\n".join(context_parts)
        return ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "name": self.config.name,
            "persona": self.config.persona,
            "total_responses": self.total_responses,
            "total_errors": self.total_errors,
            "average_response_time": self.average_response_time,
            "success_rate": (self.total_responses - self.total_errors) / max(self.total_responses, 1) * 100
        }
    
    async def generate_contextual_response(
        self,
        prompt: str,
        include_history: bool = True,
        **kwargs
    ) -> str:
        """Generate a response with conversation context."""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build contextual prompt
            contextual_prompt = prompt
            
            if include_history:
                context = self.get_context_for_response()
                if context:
                    contextual_prompt = f"{context}\n\nNow respond to: {prompt}"
            
            # Add any mode-specific instructions
            if "mode_instructions" in self.current_context:
                contextual_prompt += f"\n\nMode guidance: {self.current_context['mode_instructions']}"
            
            # Generate response (this would integrate with the actual LLM)
            response = await self._generate_response(contextual_prompt, **kwargs)
            
            # Update metrics
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            self.total_responses += 1
            self.average_response_time = (
                (self.average_response_time * (self.total_responses - 1) + response_time) 
                / self.total_responses
            )
            
            # Add to history
            self.add_to_history(self.config.name, response)
            
            logger.info(f"{self.config.name} generated response in {response_time:.2f}s")
            return response
            
        except Exception as e:
            self.total_errors += 1
            logger.error(f"Error generating response for {self.config.name}: {e}")
            raise
    
    async def _generate_response(self, prompt: str, **kwargs) -> str:
        """Internal method to generate response - to be implemented with actual LLM."""
        # This is a placeholder - in the actual implementation,
        # this would interface with the LiveKit/Gemini API
        return f"[{self.config.name} would respond to: {prompt[:50]}...]"
    
    def __repr__(self) -> str:
        return f"VoiceAgent(name='{self.config.name}', persona='{self.config.persona}')"
