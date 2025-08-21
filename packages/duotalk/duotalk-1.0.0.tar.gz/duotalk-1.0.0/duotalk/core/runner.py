"""
Main conversation runner and orchestrator.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
import os

from livekit.agents import JobContext, WorkerOptions, cli
from dotenv import load_dotenv

from .config import ConversationConfig, EnvironmentConfig
from .session import ConversationSession, SessionState
from ..agents.persona_agent import PersonaAgent


logger = logging.getLogger(__name__)


class ConversationRunner:
    """Main orchestrator for running conversations."""
    
    def __init__(
        self,
        config: Optional[ConversationConfig] = None,
        env_config: Optional[EnvironmentConfig] = None,
        event_callbacks: Optional[Dict[str, Callable]] = None
    ):
        """Initialize the conversation runner."""
        self.config = config
        self.env_config = env_config or EnvironmentConfig()
        self.event_callbacks = event_callbacks or {}
        
        # Load environment variables
        load_dotenv()
        
        # Runtime state
        self.session: Optional[ConversationSession] = None
        self.job_context: Optional[JobContext] = None
        self.is_running = False
        
        # Setup logging
        self._setup_logging()
        
        logger.info("ConversationRunner initialized")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.env_config.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format=self.env_config.log_format,
            handlers=[
                logging.StreamHandler(),
                *([logging.FileHandler(self.env_config.log_file)] if self.env_config.log_file else [])
            ]
        )
    
    async def start(
        self,
        config: Optional[ConversationConfig] = None,
        use_livekit: bool = True
    ) -> bool:
        """Start a conversation with the given configuration."""
        
        # Use provided config or default
        conversation_config = config or self.config
        if not conversation_config:
            raise ValueError("No conversation configuration provided")
        
        try:
            if use_livekit:
                return await self._start_with_livekit(conversation_config)
            else:
                return await self._start_standalone(conversation_config)
                
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            return False
    
    async def _start_with_livekit(self, config: ConversationConfig) -> bool:
        """Start conversation with LiveKit integration."""
        
        # Validate environment
        if not self._validate_livekit_environment():
            return False
        
        # Create worker options
        worker_options = WorkerOptions(
            entrypoint_fnc=self._livekit_entrypoint,
        )
        
        # Store config for entrypoint
        self.config = config
        
        # Run with LiveKit CLI
        try:
            cli.run_app(worker_options)
            return True
        except Exception as e:
            logger.error(f"LiveKit execution failed: {e}")
            return False
    
    async def _start_standalone(self, config: ConversationConfig) -> bool:
        """Start conversation without LiveKit (for testing/development)."""
        
        try:
            # Create session
            self.session = ConversationSession(
                config=config,
                job_context=None,
                event_callbacks=self.event_callbacks
            )
            
            # Initialize and start
            if await self.session.initialize():
                self.is_running = True
                await self.session.start_conversation()
                return True
            else:
                logger.error("Failed to initialize session")
                return False
                
        except Exception as e:
            logger.error(f"Standalone execution failed: {e}")
            return False
        finally:
            self.is_running = False
    
    async def _livekit_entrypoint(self, ctx: JobContext) -> None:
        """LiveKit entrypoint function."""
        await ctx.connect()
        
        if not self.config:
            raise RuntimeError("No configuration available for LiveKit entrypoint")
        
        try:
            # Create session with LiveKit context
            self.session = ConversationSession(
                config=self.config,
                job_context=ctx,
                event_callbacks=self.event_callbacks
            )
            
            # Initialize and start
            if await self.session.initialize():
                self.is_running = True
                await self.session.start_conversation()
            else:
                raise RuntimeError("Failed to initialize session")
                
        except Exception as e:
            logger.error(f"Error in LiveKit entrypoint: {e}")
            raise
        finally:
            self.is_running = False
            if self.session:
                await self.session.stop()
    
    def _validate_livekit_environment(self) -> bool:
        """Validate LiveKit environment configuration."""
        
        # Check for required API keys
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            logger.error("GEMINI_API_KEY or GOOGLE_API_KEY environment variable required")
            return False
        
        # Check LiveKit keys (optional for development)
        livekit_key = os.getenv("LIVEKIT_API_KEY")
        livekit_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not (livekit_key and livekit_secret):
            logger.warning("LiveKit API credentials not found - using development mode")
        
        return True
    
    async def stop(self) -> None:
        """Stop the current conversation."""
        if self.session:
            await self.session.stop()
        self.is_running = False
        logger.info("Conversation runner stopped")
    
    async def pause(self) -> None:
        """Pause the current conversation."""
        if self.session:
            await self.session.pause()
    
    async def resume(self) -> None:
        """Resume the current conversation."""
        if self.session:
            await self.session.resume()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current runner status."""
        return {
            "is_running": self.is_running,
            "session_status": self.session.get_status() if self.session else None,
            "config": {
                "topic": self.config.topic if self.config else None,
                "mode": self.config.mode if self.config else None,
                "agent_count": len(self.config.agents) if self.config else 0
            } if self.config else None
        }
    
    def add_event_callback(self, event_name: str, callback: Callable) -> None:
        """Add an event callback."""
        self.event_callbacks[event_name] = callback
    
    def remove_event_callback(self, event_name: str) -> None:
        """Remove an event callback."""
        self.event_callbacks.pop(event_name, None)


class ConversationManager:
    """Manages multiple conversation sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.runners: Dict[str, ConversationRunner] = {}
    
    async def create_session(
        self,
        session_id: str,
        config: ConversationConfig,
        use_livekit: bool = True
    ) -> ConversationRunner:
        """Create a new conversation session."""
        
        if session_id in self.sessions:
            raise ValueError(f"Session '{session_id}' already exists")
        
        # Create runner
        runner = ConversationRunner(config=config)
        self.runners[session_id] = runner
        
        return runner
    
    async def start_session(self, session_id: str) -> bool:
        """Start a specific session."""
        if session_id not in self.runners:
            raise ValueError(f"Session '{session_id}' not found")
        
        runner = self.runners[session_id]
        return await runner.start()
    
    async def stop_session(self, session_id: str) -> None:
        """Stop a specific session.""" 
        if session_id in self.runners:
            await self.runners[session_id].stop()
            self.sessions.pop(session_id, None)
    
    async def stop_all_sessions(self) -> None:
        """Stop all active sessions."""
        for session_id in list(self.runners.keys()):
            await self.stop_session(session_id)
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific session."""
        if session_id in self.runners:
            return self.runners[session_id].get_status()
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with their status."""
        return [
            {
                "session_id": session_id,
                "status": runner.get_status()
            }
            for session_id, runner in self.runners.items()
        ]


# Global manager instance
conversation_manager = ConversationManager()
