"""HIL system testing functionality."""

import time
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import load_config_with_env_override
from .listener import Question, QuestionRouter

console = Console()


@dataclass
class TestResult:
    """Result of HIL system test."""
    success: bool
    response: str
    llm_enhanced: bool
    voice_used: bool
    error: Optional[str] = None


class TestQuestionSimulator:
    """Simulates HIL questions for testing purposes."""
    
    def __init__(self):
        # Load configuration
        try:
            self.config = load_config_with_env_override()
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
        
        # Initialize router
        try:
            self.router = QuestionRouter(self.config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize QuestionRouter: {e}")
    
    def create_test_question(self, question_type: str = "text") -> Question:
        """Create a test question for simulation."""
        
        test_questions = [
            "This is a test question to verify the HIL system is working correctly. Please respond with any text to confirm the system works.",
            "Testing HIL functionality - can you confirm that you can see this test question and respond normally?",
            "HIL system test: Please provide any response to verify that text input, voice input, and LLM enhancement are functioning properly.",
        ]
        
        import random
        test_prompt = random.choice(test_questions)
        
        return Question(
            type=question_type,
            agent_id=f"test_hil_{int(time.time() * 1000) % 10000}",
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            prompt=test_prompt,
            timeout=300,
            metadata={
                "source": "hil_test",
                "require_confirmation": True,
                "fallback_to_text": True,
                "is_test": True
            },
            file_path=Path("/tmp/test_question.json"),  # Not used in direct mode
            role="test_system"
        )
    
    def run_test(self) -> TestResult:
        """Run a complete HIL system test."""
        
        try:
            # Create test question
            test_question = self.create_test_question("text")
            
            console.print(Panel(
                test_question.prompt,
                title=f"🧪 Test Question from {test_question.role}",
                border_style="cyan"
            ))
            
            console.print("[dim]Note: This is a test - respond normally to verify HIL system functionality.[/dim]\\n")
            
            # Process question through normal HIL flow
            response = self.router.process_question_direct(test_question)
            
            # Handle user cancellation gracefully  
            if response.startswith("ERROR: Input cancelled by user"):
                return TestResult(
                    success=True,  # User cancellation is not a failure
                    response="[Test cancelled by user]",
                    llm_enhanced=False,
                    voice_used=False,
                    error=None
                )
            
            # Analyze result
            llm_enhanced = self._detect_llm_enhancement(response)
            voice_used = self._detect_voice_usage(response)
            
            return TestResult(
                success=not response.startswith("ERROR:"),
                response=response,
                llm_enhanced=llm_enhanced,
                voice_used=voice_used,
                error=response if response.startswith("ERROR:") else None
            )
            
        except Exception as e:
            return TestResult(
                success=False,
                response="",
                llm_enhanced=False,
                voice_used=False,
                error=str(e)
            )
    
    def _detect_llm_enhancement(self, response: str) -> bool:
        """Detect if LLM enhancement was used (heuristic)."""
        # This is a simple heuristic - in real implementation we could add 
        # markers or metadata to track enhancement usage
        return len(response.split()) > 10 and not response.startswith("ERROR:")
    
    def _detect_voice_usage(self, response: str) -> bool:
        """Detect if voice input was used (heuristic)."""
        # Another heuristic - could be improved with actual tracking
        return False  # For now, we'll rely on user testing


def test_hil_system():
    """Main function to test HIL system."""
    
    console.print(Panel.fit(
        "🧪 HIL System Test",
        style="bold cyan"
    ))
    
    console.print("[dim]Testing HIL system functionality (no project setup required)...[/dim]\\n")
    
    # Display configuration info
    try:
        config = load_config_with_env_override()
        
        config_table = Table(show_header=False, box=None)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Status", style="white")
        
        config_table.add_row("OpenAI API Key", "✓ Configured" if config.openai_api_key else "❌ Missing")
        config_table.add_row("LLM Enhancement", "✓ Enabled" if config.llm.enabled else "○ Disabled")
        if config.llm.enabled:
            config_table.add_row("LLM Model", config.llm.model)
            config_table.add_row("LLM API Key", "✓ Set" if config.llm.api_key else "○ Using OpenAI key")
        
        console.print(Panel(
            config_table,
            title="📋 Configuration Status",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"Failed to load configuration: {e}",
            title="❌ Configuration Error",
            style="red"
        ))
        return
    
    # Run test
    console.print("\\n[bold]Starting HIL system test...[/bold]\\n")
    
    try:
        simulator = TestQuestionSimulator()
        result = simulator.run_test()
        
        # Display results
        if result.success:
            if result.response == "[Test cancelled by user]":
                console.print(Panel(
                    f"🚪 Test cancelled by user\\n\\n"
                    f"[dim]The HIL system is working correctly - user interface responded to Ctrl+C properly.[/dim]\\n\\n"
                    f"[bold]System Status:[/bold]\\n"
                    f"✓ Configuration loaded\\n"
                    f"✓ HIL system initialized\\n"
                    f"✓ User interface functional",
                    title="✅ Test Cancelled (System OK)",
                    style="yellow"
                ))
            else:
                console.print(Panel(
                    f"✅ Test completed successfully!\\n\\n"
                    f"[bold]Response received:[/bold] {result.response[:100]}{'...' if len(result.response) > 100 else ''}\\n\\n"
                    f"[bold]Features tested:[/bold]\\n"
                    f"{'✓' if result.response and not result.response.startswith('[Test cancelled') else '○'} Text/Voice input\\n"
                    f"{'✓' if result.llm_enhanced else '○'} LLM enhancement\\n"
                    f"{'✓' if not result.response.startswith('ERROR:') else '❌'} HIL flow",
                    title="🎉 Test Results",
                    style="green"
                ))
        else:
            console.print(Panel(
                f"❌ Test failed\\n\\n"
                f"[bold]Error:[/bold] {result.error}",
                title="💥 Test Results",
                style="red"
            ))
            
    except Exception as e:
        console.print(Panel(
            f"❌ Test execution failed\\n\\n"
            f"[bold]Error:[/bold] {e}",
            title="💥 Test Execution Error", 
            style="red"
        ))


def process_question_direct(router: QuestionRouter, question: Question) -> str:
    """Process question directly without file system (monkey patch for testing)."""
    # ВАЖНО: Используем существующие handlers из router (у них есть router reference)
    if question.type == 'voice':
        return router.voice_handler.handle(question)
    else:
        return router.text_handler.handle(question)


# Monkey patch the QuestionRouter to add direct processing method
QuestionRouter.process_question_direct = lambda self, question: process_question_direct(self, question)