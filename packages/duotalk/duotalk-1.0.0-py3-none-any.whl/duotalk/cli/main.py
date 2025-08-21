"""
Simple CLI interface for DuoTalk.
"""

import asyncio
import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.config import ConversationConfig
from ..core.convenience import (
    create_debate, create_roundtable, create_friendly_chat,
    create_interview, create_panel, create_socratic,
    create_business_discussion, create_academic_debate,
    create_creative_brainstorm, create_policy_discussion
)
from ..personas import ALL_PERSONA_NAMES, get_persona_by_name
from ..modes import ALL_MODES

app = typer.Typer(name="duotalk", help="Advanced multi-agent voice conversation system")
console = Console()

# Conversation presets
CONVERSATION_PRESETS = {
    "business": create_business_discussion,
    "academic": create_academic_debate,
    "creative": create_creative_brainstorm,
    "policy": create_policy_discussion,
}


@app.command()
def start(
    topic: str = typer.Argument(..., help="Conversation topic"),
    mode: str = typer.Option("roundtable", help="Conversation mode"),
    personas: List[str] = typer.Option([], help="Persona names to use"),
    max_turns: int = typer.Option(10, help="Maximum conversation turns"),
):
    """Start a conversation with specified parameters."""
    try:
        if mode == "debate":
            config = create_debate(topic, personas or None, max_turns)
        elif mode == "roundtable":
            config = create_roundtable(topic, personas or None, max_turns)
        elif mode == "friendly":
            config = create_friendly_chat(topic, personas or None, max_turns)
        elif mode == "interview":
            config = create_interview(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "panel":
            config = create_panel(topic, personas[0] if personas else None, personas[1:] if len(personas) > 1 else None, max_turns)
        elif mode == "socratic":
            config = create_socratic(topic, personas or None, max_turns)
        else:
            console.print(f"❌ Unknown mode: {mode}. Available modes: {', '.join(ALL_MODES)}")
            raise typer.Exit(1)
        
        console.print(f"🎭 Created {mode} conversation: '{topic}'")
        console.print(f"👥 Participants: {', '.join([agent.name for agent in config.agents])}")
        console.print("📝 Configuration created successfully!")
        console.print("🔧 To actually run conversations, you'll need LiveKit credentials.")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


@app.command()
def preset(
    preset_name: str = typer.Argument(..., help="Preset name"),
    topic: str = typer.Argument(..., help="Conversation topic"),
):
    """Start a conversation using a preset configuration."""
    if preset_name not in CONVERSATION_PRESETS:
        console.print(f"❌ Unknown preset: {preset_name}")
        console.print(f"Available presets: {', '.join(CONVERSATION_PRESETS.keys())}")
        raise typer.Exit(1)
    
    try:
        config = CONVERSATION_PRESETS[preset_name](topic)
        console.print(f"🎭 Created {preset_name} conversation: '{topic}'")
        console.print(f"👥 Participants: {', '.join([agent.name for agent in config.agents])}")
        console.print("📝 Configuration created successfully!")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


@app.command()
def list_personas():
    """List all available personas."""
    table = Table(title="Available Personas")
    table.add_column("Name", style="cyan")
    table.add_column("Persona", style="magenta")
    table.add_column("Role", style="green")
    table.add_column("Perspective", style="yellow")
    
    from ..personas import ALL_PERSONAS
    for persona in ALL_PERSONAS:
        table.add_row(
            persona.name,
            persona.persona,
            persona.role,
            persona.perspective
        )
    
    console.print(table)


@app.command()
def list_modes():
    """List all available conversation modes."""
    console.print(Panel("Available Conversation Modes", title_align="center"))
    
    mode_descriptions = {
        "friendly": "Collaborative discussion where agents build on each other's ideas",
        "debate": "Structured debate with opposing viewpoints and rebuttals",
        "roundtable": "Multi-participant discussion with diverse perspectives",
        "interview": "Interview format with one interviewer and multiple interviewees",
        "panel": "Expert panel with moderator and specialists",
        "socratic": "Question-driven exploration using Socratic method"
    }
    
    for mode, description in mode_descriptions.items():
        console.print(f"[bold cyan]{mode}[/bold cyan]: {description}")


@app.command()
def test():
    """Run a quick test conversation."""
    try:
        config = create_debate("Is pineapple on pizza acceptable?", ["optimist", "skeptic"])
        console.print("🧪 Test conversation created successfully!")
        console.print(f"Topic: {config.topic}")
        console.print(f"Mode: {config.mode}")
        console.print(f"Agents: {', '.join([agent.name for agent in config.agents])}")
        console.print("✅ DuoTalk is working correctly!")
        
    except Exception as e:
        console.print(f"❌ Test failed: {e}")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start an interactive conversation builder."""
    console.print(Panel("🎭 Interactive Conversation Builder", title_align="center"))
    
    # Get topic
    topic = typer.prompt("Enter conversation topic")
    
    # Get mode
    console.print(f"Available modes: {', '.join(ALL_MODES)}")
    mode = typer.prompt("Choose conversation mode", default="roundtable")
    
    if mode not in ALL_MODES:
        console.print(f"❌ Invalid mode. Using 'roundtable' instead.")
        mode = "roundtable"
    
    # Get personas
    console.print(f"Available personas: {', '.join(ALL_PERSONA_NAMES)}")
    personas_input = typer.prompt("Enter persona names (comma-separated)", default="")
    
    if personas_input:
        personas = [p.strip() for p in personas_input.split(",")]
    else:
        personas = None
    
    # Get max turns
    max_turns = typer.prompt("Maximum turns", default=10, type=int)
    
    # Create conversation
    try:
        if mode == "debate":
            config = create_debate(topic, personas, max_turns)
        elif mode == "roundtable":
            config = create_roundtable(topic, personas, max_turns)
        elif mode == "friendly":
            config = create_friendly_chat(topic, personas, max_turns)
        elif mode == "interview":
            config = create_interview(topic, personas[0] if personas else None, personas[1:] if personas and len(personas) > 1 else None, max_turns)
        elif mode == "panel":
            config = create_panel(topic, personas[0] if personas else None, personas[1:] if personas and len(personas) > 1 else None, max_turns)
        elif mode == "socratic":
            config = create_socratic(topic, personas, max_turns)
        else:
            config = create_roundtable(topic, personas, max_turns)
        
        console.print("\n🎉 Conversation created successfully!")
        console.print(f"Topic: {config.topic}")
        console.print(f"Mode: {config.mode}")
        console.print(f"Agents: {', '.join([agent.name for agent in config.agents])}")
        console.print(f"Max turns: {config.max_turns}")
        
    except Exception as e:
        console.print(f"❌ Error creating conversation: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
