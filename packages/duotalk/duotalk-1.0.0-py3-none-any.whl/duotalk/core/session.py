"""
Conversation session management.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import json
from pathlib import Path

from livekit.agents import JobContext, AgentSession
from livekit.plugins.google.beta.realtime import RealtimeModel

from .config import ConversationConfig, AgentConfig
from ..agents.persona_agent import PersonaAgent
from ..modes import get_mode


logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session state enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ConversationMetrics:
    """Metrics tracking for conversation quality."""
    total_turns: int = 0
    agent_participation: Dict[str, int] = field(default_factory=dict)
    average_response_time: float = 0.0
    interruption_count: int = 0
    error_count: int = 0
    engagement_score: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def get_duration(self) -> float:
        """Get conversation duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    def get_participation_balance(self) -> float:
        """Get how balanced participation is (0.0 = very unbalanced, 1.0 = perfectly balanced)."""
        if not self.agent_participation:
            return 0.0
        
        total_responses = sum(self.agent_participation.values())
        if total_responses == 0:
            return 0.0
        
        expected_per_agent = total_responses / len(self.agent_participation)
        deviations = [abs(count - expected_per_agent) for count in self.agent_participation.values()]
        average_deviation = sum(deviations) / len(deviations)
        
        # Normalize to 0-1 scale (lower deviation = higher balance)
        max_possible_deviation = expected_per_agent
        balance_score = 1.0 - (average_deviation / max_possible_deviation)
        return max(0.0, min(1.0, balance_score))


class ConversationSession:
    """Manages a single conversation session."""
    
    def __init__(
        self,
        config: ConversationConfig,
        job_context: Optional[JobContext] = None,
        event_callbacks: Optional[Dict[str, Callable]] = None
    ):
        self.config = config
        self.job_context = job_context
        self.event_callbacks = event_callbacks or {}
        
        # Session state
        self.state = SessionState.INITIALIZING
        self.agents: List[PersonaAgent] = []
        self.current_speaker_index = 0
        self.conversation_mode = get_mode(config.mode)
        self.metrics = ConversationMetrics()
        
        # LiveKit session
        self.livekit_session: Optional[AgentSession] = None
        self.realtime_model: Optional[RealtimeModel] = None
        
        # Conversation tracking
        self.conversation_log: List[Dict[str, Any]] = []
        self.context_data: Dict[str, Any] = {
            "topic": config.topic,
            "mode": config.mode,
            "max_turns": config.max_turns
        }
        
        # Error handling
        self.last_error: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
        
        logger.info(f"ConversationSession initialized: {config.session_name}")
    
    async def initialize(self) -> bool:
        """Initialize the conversation session."""
        try:
            self.state = SessionState.INITIALIZING
            self.metrics.start_time = time.time()
            
            # Create agents
            await self._create_agents()
            
            # Initialize LiveKit session if context provided
            if self.job_context:
                await self._initialize_livekit_session()
            
            # Initialize conversation mode
            await self._initialize_mode()
            
            self.state = SessionState.RUNNING
            await self._emit_event("session_initialized", {"session": self})
            
            logger.info("Session initialized successfully")
            return True
            
        except Exception as e:
            self.state = SessionState.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to initialize session: {e}")
            await self._emit_event("session_error", {"error": e})
            return False
    
    async def _create_agents(self) -> None:
        """Create persona agents from configuration."""
        for i, agent_config in enumerate(self.config.agents):
            agent = PersonaAgent(
                config=agent_config,
                topic=self.config.topic,
                model_name=self.config.model_name
            )
            
            # Initialize agent metrics tracking
            self.metrics.agent_participation[agent_config.name] = 0
            
            self.agents.append(agent)
            logger.info(f"Created agent: {agent_config.name} ({agent_config.persona})")
    
    async def _initialize_livekit_session(self) -> None:
        """Initialize LiveKit session for audio."""
        if not self.job_context:
            return
            
        # Create realtime model
        self.realtime_model = RealtimeModel(
            model=self.config.model_name,
            instructions="",  # Will be set per agent
            voice=self.agents[0].config.voice.value if self.agents else "Puck",
        )
        
        # Create session
        self.livekit_session = AgentSession(
            userdata=self,
            llm=self.realtime_model,
            allow_interruptions=self.config.allow_interruptions,
            turn_detection="realtime_llm",
            min_interruption_duration=self.config.min_interruption_duration,
        )
        
        # Set up event handlers
        self.livekit_session.on("error", self._handle_session_error)
        
        logger.info("LiveKit session initialized")
    
    async def _initialize_mode(self) -> None:
        """Initialize conversation mode."""
        # Update context with mode-specific information
        for i, agent in enumerate(self.agents):
            mode_instructions = self.conversation_mode.get_agent_instructions(
                i, len(self.agents), self.context_data
            )
            agent.update_context({
                "mode_instructions": mode_instructions,
                "conversation_mode": self.config.mode,
                "total_agents": len(self.agents),
                "agent_index": i
            })
        
        logger.info(f"Conversation mode '{self.config.mode}' initialized")
    
    async def start_conversation(self) -> None:
        """Start the conversation loop."""
        if self.state != SessionState.RUNNING:
            raise RuntimeError("Session must be initialized and running to start conversation")
        
        await self._emit_event("conversation_started", {"session": self})
        
        try:
            # Start LiveKit session if available
            if self.livekit_session and self.job_context:
                await self.livekit_session.start(
                    agent=self.agents[0],  # Start with first agent
                    room=self.job_context.room
                )
            
            # Run conversation loop
            await self._conversation_loop()
            
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            self.state = SessionState.ERROR
            self.last_error = str(e)
            await self._emit_event("conversation_error", {"error": e})
        finally:
            await self.stop()
    
    async def _conversation_loop(self) -> None:
        """Main conversation loop."""
        turn_count = 0
        
        while (self.state == SessionState.RUNNING and 
               turn_count < self.config.max_turns and
               self.conversation_mode.should_continue(turn_count, self.context_data)):
            
            try:
                # Determine next speaker
                speaker_index = self.conversation_mode.get_turn_order(
                    self.agents, turn_count
                )
                current_agent = self.agents[speaker_index]
                
                # Generate response
                await self._agent_turn(current_agent, turn_count)
                
                turn_count += 1
                self.metrics.total_turns = turn_count
                
                # Update metrics
                self.metrics.agent_participation[current_agent.config.name] += 1
                
                # Inter-turn delay
                await asyncio.sleep(2.0)
                
                await self._emit_event("turn_completed", {
                    "turn": turn_count,
                    "speaker": current_agent.config.name,
                    "agent": current_agent
                })
                
            except Exception as e:
                self.metrics.error_count += 1
                logger.error(f"Error in turn {turn_count}: {e}")
                
                if self.metrics.error_count > 3:
                    logger.error("Too many errors, stopping conversation")
                    break
                    
                await asyncio.sleep(1.0)  # Brief pause before retry
        
        logger.info(f"Conversation completed after {turn_count} turns")
        await self._emit_event("conversation_completed", {"session": self})
    
    async def _agent_turn(self, agent: PersonaAgent, turn_count: int) -> None:
        """Execute a single agent turn."""
        start_time = time.time()
        
        try:
            # Build turn context
            turn_context = {
                **self.context_data,
                "turn_count": turn_count,
                "current_speaker": agent.config.name,
                "conversation_history": self.conversation_log[-5:],  # Last 5 messages
                "metrics": self.metrics,
            }
            
            # Generate prompt based on turn number
            if turn_count == 0:
                prompt = f"Start the conversation about: {self.config.topic}"
            else:
                prompt = f"Continue the conversation about: {self.config.topic}"
            
            # Generate response
            if self.livekit_session:
                # Use LiveKit for actual voice generation
                await self._generate_voice_response(agent, prompt, turn_context)
            else:
                # Simulate response for testing
                response = await agent.generate_persona_response(prompt, turn_context)
                await self._log_response(agent.config.name, response)
            
            # Update timing metrics
            response_time = time.time() - start_time
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * turn_count + response_time) / 
                (turn_count + 1)
            )
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {agent.config.name} on turn {turn_count}")
            await self._log_response(agent.config.name, "[Response timeout]")
        except Exception as e:
            logger.error(f"Error in agent turn for {agent.config.name}: {e}")
            raise
    
    async def _generate_voice_response(
        self, 
        agent: PersonaAgent, 
        prompt: str, 
        context: Dict[str, Any]
    ) -> None:
        """Generate voice response using LiveKit."""
        if not self.livekit_session:
            return
        
        # Update session voice and instructions
        if hasattr(self.livekit_session.llm, "voice"):
            self.livekit_session.llm.voice = agent.config.voice.value
        
        # Generate contextual prompt
        mode_instructions = self.conversation_mode.get_agent_instructions(
            context.get("agent_index", 0),
            len(self.agents),
            context
        )
        
        full_prompt = f"{mode_instructions}\n\n{prompt}"
        
        # Generate reply
        speech_handle = self.livekit_session.generate_reply(user_input=full_prompt)
        
        # Wait for completion with timeout
        try:
            await asyncio.wait_for(
                speech_handle.wait_for_playout(), 
                timeout=self.config.turn_timeout
            )
            await self._log_response(agent.config.name, "[Voice response generated]")
        except asyncio.TimeoutError:
            logger.warning(f"Voice generation timeout for {agent.config.name}")
            raise
    
    async def _log_response(self, speaker: str, response: str) -> None:
        """Log a conversation response."""
        log_entry = {
            "timestamp": time.time(),
            "speaker": speaker,
            "response": response,
            "turn": self.metrics.total_turns
        }
        
        self.conversation_log.append(log_entry)
        
        # Update agent history
        for agent in self.agents:
            agent.add_to_history(speaker, response)
        
        logger.info(f"{speaker}: {response[:100]}...")
        await self._emit_event("response_generated", log_entry)
    
    async def pause(self) -> None:
        """Pause the conversation."""
        if self.state == SessionState.RUNNING:
            self.state = SessionState.PAUSED
            await self._emit_event("session_paused", {"session": self})
            logger.info("Session paused")
    
    async def resume(self) -> None:
        """Resume the conversation.""" 
        if self.state == SessionState.PAUSED:
            self.state = SessionState.RUNNING
            await self._emit_event("session_resumed", {"session": self})
            logger.info("Session resumed")
    
    async def stop(self) -> None:
        """Stop the conversation session."""
        if self.state in [SessionState.STOPPING, SessionState.STOPPED]:
            return
            
        self.state = SessionState.STOPPING
        self.metrics.end_time = time.time()
        
        try:
            # Clean up LiveKit session
            if self.livekit_session:
                await self._cleanup_livekit_session()
            
            self.state = SessionState.STOPPED
            await self._emit_event("session_stopped", {"session": self})
            
            # Save conversation log if configured
            if self.config.log_conversation:
                await self._save_conversation_log()
            
            logger.info("Session stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping session: {e}")
            self.state = SessionState.ERROR
            self.last_error = str(e)
    
    async def _cleanup_livekit_session(self) -> None:
        """Clean up LiveKit session resources.""" 
        if not self.livekit_session:
            return
            
        try:
            await asyncio.wait_for(self.livekit_session.interrupt(), timeout=2.0)
        except (asyncio.TimeoutError, RuntimeError):
            logger.warning("Could not interrupt session cleanly")
        
        try:
            await asyncio.wait_for(self.livekit_session.drain(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Session drain timeout")
        
        try:
            await asyncio.wait_for(self.livekit_session.aclose(), timeout=3.0)
        except asyncio.TimeoutError:
            logger.warning("Session close timeout")
    
    async def _save_conversation_log(self) -> None:
        """Save conversation log to file."""
        if not self.config.output_dir:
            return
            
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        filename = f"conversation_{self.config.session_name}_{timestamp}.json"
        filepath = output_dir / filename
        
        conversation_data = {
            "config": {
                "topic": self.config.topic,
                "mode": self.config.mode,
                "agents": [
                    {
                        "name": agent.name,
                        "persona": agent.persona,
                        "role": agent.role
                    } for agent in self.config.agents
                ]
            },
            "metrics": {
                "total_turns": self.metrics.total_turns,
                "duration": self.metrics.get_duration(),
                "participation": self.metrics.agent_participation,
                "average_response_time": self.metrics.average_response_time,
                "participation_balance": self.metrics.get_participation_balance()
            },
            "conversation": self.conversation_log
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversation log saved to: {filepath}")
    
    async def _handle_session_error(self, error: Exception) -> None:
        """Handle LiveKit session errors."""
        logger.error(f"LiveKit session error: {error}")
        self.state = SessionState.ERROR
        self.last_error = str(error)
        await self._emit_event("session_error", {"error": error})
    
    async def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit an event to registered callbacks."""
        if event_name in self.event_callbacks:
            try:
                callback = self.event_callbacks[event_name]
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in event callback '{event_name}': {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            "state": self.state.value,
            "metrics": {
                "total_turns": self.metrics.total_turns,
                "duration": self.metrics.get_duration(),
                "participation": self.metrics.agent_participation,
                "errors": self.metrics.error_count,
                "participation_balance": self.metrics.get_participation_balance()
            },
            "agents": [
                {
                    "name": agent.config.name,
                    "persona": agent.config.persona,
                    "stats": agent.get_stats()
                } for agent in self.agents
            ],
            "last_error": self.last_error
        }
