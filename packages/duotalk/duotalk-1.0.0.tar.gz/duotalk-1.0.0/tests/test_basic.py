"""
Basic tests for DuoTalk package.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch

# Import the package modules
try:
    from duotalk.core.config import ConversationConfig, AgentConfig, VoiceType
    from duotalk.core.runner import ConversationRunner
    from duotalk.personas import OPTIMIST, SKEPTIC
    from duotalk.modes import get_mode
    from duotalk.core.convenience import create_debate, quick_conversation
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the package is installed: pip install -e .")


class TestConfiguration:
    """Test configuration classes."""
    
    def test_agent_config_creation(self):
        """Test creating agent configuration."""
        agent = AgentConfig(
            name="Test Agent",
            persona="test",
            role="tester",
            perspective="testing perspective",
            voice=VoiceType.PUCK
        )
        
        assert agent.name == "Test Agent"
        assert agent.persona == "test"
        assert agent.voice == VoiceType.PUCK
        assert "Test Agent" in agent.instructions
    
    def test_conversation_config_creation(self):
        """Test creating conversation configuration."""
        config = ConversationConfig(
            topic="Test Topic",
            agents=[OPTIMIST, SKEPTIC],
            mode="debate",
            max_turns=5
        )
        
        assert config.topic == "Test Topic"
        assert len(config.agents) == 2
        assert config.mode == "debate"
        assert config.max_turns == 5
        assert config.session_name is not None
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Should raise error with only one agent
        with pytest.raises(ValueError):
            ConversationConfig(
                topic="Test",
                agents=[OPTIMIST],  # Only one agent
                mode="debate"
            )


class TestPersonas:
    """Test persona system."""
    
    def test_predefined_personas(self):
        """Test predefined personas are properly configured."""
        assert OPTIMIST.name
        assert OPTIMIST.persona == "optimist"
        assert OPTIMIST.role
        assert OPTIMIST.perspective
        
        assert SKEPTIC.name
        assert SKEPTIC.persona in ["pessimist", "skeptic"]
    
    def test_persona_diversity(self):
        """Test that personas have different characteristics."""
        assert OPTIMIST.perspective != SKEPTIC.perspective
        assert OPTIMIST.instructions != SKEPTIC.instructions


class TestConversationModes:
    """Test conversation modes."""
    
    def test_get_mode(self):
        """Test getting conversation modes."""
        friendly_mode = get_mode("friendly")
        assert friendly_mode.config.name == "friendly"
        
        debate_mode = get_mode("debate")
        assert debate_mode.config.name == "debate"
    
    def test_mode_instructions(self):
        """Test mode-specific instructions."""
        debate_mode = get_mode("debate")
        
        # Test agent instructions
        instructions = debate_mode.get_agent_instructions(
            0, 2, {"topic": "Test Topic"}
        )
        assert "Test Topic" in instructions
        assert len(instructions) > 50  # Should be detailed
    
    def test_turn_order(self):
        """Test turn order logic."""
        roundtable_mode = get_mode("roundtable")
        
        # Mock agents list
        agents = [Mock(), Mock(), Mock()]
        
        # Test sequential turn order
        turn1 = roundtable_mode.get_turn_order(agents, 0)
        turn2 = roundtable_mode.get_turn_order(agents, 1)
        turn3 = roundtable_mode.get_turn_order(agents, 2)
        
        assert turn1 == 0
        assert turn2 == 1
        assert turn3 == 2


@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Test convenience functions for creating conversations."""
    
    async def test_create_debate(self):
        """Test creating debate conversation."""
        runner = await create_debate(
            topic="Test Topic",
            max_turns=4
        )
        
        assert isinstance(runner, ConversationRunner)
        assert runner.config.topic == "Test Topic"
        assert runner.config.mode == "debate"
        assert len(runner.config.agents) == 2
    
    async def test_quick_conversation(self):
        """Test quick conversation creation."""
        runner = await quick_conversation(
            preset="friendly",
            topic="Test Topic",
            max_turns=4
        )
        
        assert isinstance(runner, ConversationRunner)
        assert runner.config.topic == "Test Topic"
    
    async def test_invalid_preset(self):
        """Test error handling for invalid preset."""
        with pytest.raises(ValueError):
            await quick_conversation(
                preset="nonexistent",
                topic="Test Topic"
            )


@pytest.mark.asyncio 
class TestConversationRunner:
    """Test conversation runner functionality."""
    
    async def test_runner_creation(self):
        """Test creating conversation runner."""
        config = ConversationConfig(
            topic="Test Topic",
            agents=[OPTIMIST, SKEPTIC],
            mode="friendly",
            max_turns=3
        )
        
        runner = ConversationRunner(config=config)
        assert runner.config == config
        assert not runner.is_running
    
    @patch('duotalk.core.session.ConversationSession')
    async def test_standalone_execution(self, mock_session_class):
        """Test standalone conversation execution."""
        # Mock session
        mock_session = Mock()
        mock_session.initialize.return_value = True
        mock_session.start_conversation.return_value = None
        mock_session_class.return_value = mock_session
        
        config = ConversationConfig(
            topic="Test Topic",
            agents=[OPTIMIST, SKEPTIC],
            mode="friendly",
            max_turns=2
        )
        
        runner = ConversationRunner(config=config)
        
        # Test standalone start (without LiveKit)
        result = await runner.start(use_livekit=False)
        
        # Verify session was created and started
        mock_session_class.assert_called_once()
        mock_session.initialize.assert_called_once()
        mock_session.start_conversation.assert_called_once()


class TestIntegration:
    """Integration tests."""
    
    def test_package_imports(self):
        """Test that all main package components can be imported."""
        from duotalk import (
            ConversationRunner,
            ConversationConfig, 
            AgentConfig,
            create_debate,
            create_roundtable,
            OPTIMIST,
            PESSIMIST
        )
        
        # Should not raise any errors
        assert ConversationRunner
        assert ConversationConfig
        assert AgentConfig
        assert create_debate
        assert create_roundtable
        assert OPTIMIST
        assert PESSIMIST
    
    def test_cli_import(self):
        """Test CLI can be imported."""
        try:
            from duotalk.cli.main import app
            assert app
        except ImportError:
            # CLI dependencies might not be installed in test environment
            pass


def run_tests():
    """Run all tests manually."""
    print("Running DuoTalk Tests")
    print("=" * 30)
    
    # Configuration tests
    print("\n✓ Testing Configuration...")
    test_config = TestConfiguration()
    test_config.test_agent_config_creation()
    test_config.test_conversation_config_creation()
    print("Configuration tests passed!")
    
    # Persona tests
    print("\n✓ Testing Personas...")
    test_personas = TestPersonas()
    test_personas.test_predefined_personas()
    test_personas.test_persona_diversity()
    print("Persona tests passed!")
    
    # Mode tests
    print("\n✓ Testing Conversation Modes...")
    test_modes = TestConversationModes()
    test_modes.test_get_mode()
    test_modes.test_mode_instructions()
    test_modes.test_turn_order()
    print("Mode tests passed!")
    
    # Integration tests
    print("\n✓ Testing Integration...")
    test_integration = TestIntegration()
    test_integration.test_package_imports()
    test_integration.test_cli_import()
    print("Integration tests passed!")
    
    print("\n🎉 All tests completed successfully!")


async def run_async_tests():
    """Run async tests manually."""
    print("\n✓ Testing Async Functions...")
    
    test_convenience = TestConvenienceFunctions()
    await test_convenience.test_create_debate()
    await test_convenience.test_quick_conversation()
    
    test_runner = TestConversationRunner()
    await test_runner.test_runner_creation()
    
    print("Async tests passed!")


if __name__ == "__main__":
    # Run synchronous tests
    run_tests()
    
    # Run async tests
    asyncio.run(run_async_tests())
