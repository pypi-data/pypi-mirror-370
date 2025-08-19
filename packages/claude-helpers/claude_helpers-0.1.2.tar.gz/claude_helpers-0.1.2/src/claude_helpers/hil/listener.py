"""HIL Listener - Background daemon for human-in-the-loop interactions."""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from rich.console import Console
from rich.panel import Panel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from ..config import GlobalConfig

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class Question:
    """Question from agent."""
    type: str  # "text" or "voice"
    agent_id: str
    timestamp: str
    prompt: str
    timeout: int
    metadata: Dict[str, Any]
    file_path: Path
    role: Optional[str] = None  # Question author role


class QuestionHandler(ABC):
    """Abstract base for question handlers."""
    
    @abstractmethod
    def handle(self, question: Question) -> str:
        """Handle a question and return the answer."""
        pass


class TextQuestionHandler(QuestionHandler):
    """Handles text-based questions with dynamic mode switching."""
    
    def __init__(self, config: GlobalConfig):
        self.config = config
        self.voice_handler = None  # Lazy init if needed
    
    def handle(self, question: Question) -> str:
        """Display text prompt and get user response."""
        from rich.prompt import Prompt
        from rich.table import Table
        
        # Display question with role info
        agent_display = f"Agent {question.agent_id[:8]}"
        if question.role:
            agent_display += f" ({question.role})"
        
        console.print(Panel(
            question.prompt,
            title=f"🤔 Question from {agent_display}",
            border_style="cyan"
        ))
        
        # Show input options
        options = Table(show_header=False, box=None)
        options.add_column("Option", style="cyan")
        options.add_column("Action", style="white")
        options.add_row("[Enter]", "Type text response")
        options.add_row("[V]", "Switch to voice input")
        options.add_row("[Ctrl+C]", "Cancel")
        console.print(options)
        
        # Get response with mode switching
        while True:
            try:
                response = Prompt.ask("Your response (or 'v' for voice)")
                
                # Check for mode switch
                if response.lower() == 'v':
                    console.print("[cyan]Switching to voice input...[/cyan]")
                    return self._switch_to_voice(question)
                
                if not response.strip():
                    console.print("[yellow]Empty response, please try again[/yellow]")
                    continue
                
                # NEW: Post-processing option
                enhanced_response = self._maybe_enhance_response(response, question)
                return enhanced_response
                
            except (KeyboardInterrupt, EOFError):
                console.print("[red]❌ Input cancelled by user[/red]")
                return "ERROR: Input cancelled by user"
            except Exception as e:
                logger.exception(f"Unexpected error in text input: {e}")
                console.print(f"[red]❌ Input error: {e}[/red]")
                return f"ERROR: Input error: {e}"
    
    def _maybe_enhance_response(self, response: str, question: Question) -> str:
        """Optionally enhance response with LLM."""
        
        # Check if post-processor is available
        if not hasattr(self, 'router') or not self.router or not self.router.postprocessor:
            # No post-processor available, show confirmation and return original
            logger.debug("No LLM post-processor available for text response")
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return response
        
        if not self.router.postprocessor.is_enabled():
            # Post-processor disabled, show confirmation and return original
            logger.debug("LLM post-processor disabled for text response")
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return response
        
        # Ask for enhancement with user context
        from rich.prompt import Prompt, Confirm
        
        console.print("\n🤖 [cyan]LLM Enhancement Available[/cyan]")
        if not Confirm.ask("Enhance response with LLM?", default=False):
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return response
        
        user_instruction = Prompt.ask(
            "Additional instructions for LLM enhancement",
            default="Please improve clarity, structure, and completeness while preserving meaning"
        )
        
        console.print("[cyan]⏳ Enhancing response with LLM...[/cyan]")
        
        try:
            enhanced = self.router.postprocessor.enhance_text_response(
                text=response,
                user_instruction=user_instruction,
                is_transcription=False,
                question_context=question.prompt
            )
            
            # Show enhanced version
            console.print(Panel(
                enhanced,
                title="🤖 LLM Enhanced Response",
                border_style="green"
            ))
            
            # Confirm usage
            if Confirm.ask("Use enhanced version?", default=True):
                console.print(f"[green]✅ Sending enhanced answer to agent {question.agent_id[:8]}...[/green]")
                return enhanced
            else:
                console.print(f"[green]✅ Sending original answer to agent {question.agent_id[:8]}...[/green]")
                return response
                
        except Exception as e:
            console.print(f"[red]❌ LLM enhancement failed: {e}[/red]")
            console.print(f"[green]✅ Sending original answer to agent {question.agent_id[:8]}...[/green]")
            return response
    
    def _switch_to_voice(self, question: Question) -> str:
        """Switch to voice input mode."""
        if self.voice_handler is None:
            self.voice_handler = VoiceQuestionHandler(self.config)
            # CRITICAL: Pass router reference to new voice handler
            if hasattr(self, 'router') and self.router:
                self.voice_handler.router = self.router
        
        # Modify question to indicate voice mode
        question.type = 'voice'
        question.metadata['switched_from_text'] = True
        return self.voice_handler.handle(question)


class VoiceQuestionHandler(QuestionHandler):
    """Handles voice recording requests from agents."""
    
    def __init__(self, config: GlobalConfig):
        self.config = config
        self._init_recorder()
        self._init_whisper()
    
    def _init_recorder(self):
        """Initialize audio recorder."""
        from ..audio.recorder import CrossPlatformRecorder
        from ..audio.devices import get_default_device, get_device_info
        
        # Get device configuration
        if self.config.audio.device_id is None:
            device = get_default_device()
            self.device_name = device.name if device else "Default"
            self.sample_rate = device.sample_rate if device else 44100
            self.device_id = device.id if device else None
        else:
            try:
                device_info = get_device_info(self.config.audio.device_id)
                self.device_name = device_info.name
                self.sample_rate = int(device_info.default_sample_rate)
                self.device_id = self.config.audio.device_id
            except Exception as e:
                logger.warning(f"Could not get device info: {e}")
                self.device_name = f"Device {self.config.audio.device_id}"
                self.sample_rate = self.config.audio.sample_rate
                self.device_id = self.config.audio.device_id
        
        # Create recorder
        self.recorder = CrossPlatformRecorder(
            device_id=self.device_id,
            sample_rate=self.sample_rate,
            channels=self.config.audio.channels
        )
    
    def _init_whisper(self):
        """Initialize Whisper client."""
        from ..transcription import create_whisper_client
        self.whisper = create_whisper_client(self.config.openai_api_key)
    
    def handle(self, question: Question) -> str:
        """Handle a voice question request."""
        
        try:
            # Show recording UI with option to switch to text
            agent_display = f"Agent {question.agent_id[:8]}"
            if question.role:
                agent_display += f" ({question.role})"
            
            console.print(Panel(
                question.prompt,
                title=f"🎤 Voice Request from {agent_display}",
                border_style="blue"
            ))
            
            # Show input mode options before recording
            from rich.table import Table
            from rich.prompt import Prompt
            
            options = Table(show_header=False, box=None)
            options.add_column("Option", style="cyan")
            options.add_column("Action", style="white")
            options.add_row("[Enter]", "Start voice recording")
            options.add_row("[T]", "Switch to text input instead")
            options.add_row("[Ctrl+C]", "Cancel")
            console.print(options)
            
            # Get user choice
            try:
                choice = Prompt.ask("Choose input method (Enter for voice, T for text)", default="")
                if choice.lower() == 't':
                    console.print("[cyan]Switching to text input...[/cyan]")
                    return self._fallback_to_text(question.prompt, question)
            except (KeyboardInterrupt, EOFError):
                console.print("[red]❌ Input cancelled by user[/red]")
                return "ERROR: Input cancelled by user"
            
            # Record audio
            audio_data = self._record_with_ui(
                max_duration=question.metadata.get('max_duration', 30)
            )
            
            if audio_data is None:
                return "ERROR: Recording cancelled by user"
            
            # Transcribe with auto language detection
            console.print("[cyan]Transcribing audio...[/cyan]")
            result = self.whisper.transcribe_audio(
                audio_data,
                sample_rate=self.sample_rate,
                language=None  # Auto-detect language
            )
            
            # Preview and edit if requested
            if question.metadata.get('require_confirmation', True):
                final_text = self._preview_and_edit(result.text)
                if final_text is None:
                    console.print("[red]❌ Answer cancelled[/red]")
                    return "ERROR: Recording cancelled after transcription"
                
                # NEW: LLM enhancement for transcription
                enhanced_text = self._maybe_enhance_transcription(final_text, question)
                return enhanced_text
            
            # For non-confirmation mode, show immediate send confirmation
            console.print(f"[green]✅ Sending transcription to agent {question.agent_id[:8]}...[/green]")
            return result.text
            
        except Exception as e:
            logger.exception("Voice recording failed")
            
            # Fallback to text if configured
            if question.metadata.get('fallback_to_text', True):
                console.print(f"[yellow]Voice recording failed: {e}[/yellow]")
                console.print("[cyan]Falling back to text input...[/cyan]")
                return self._fallback_to_text(question.prompt, question)
            else:
                return f"ERROR: Voice recording failed: {e}"
    
    def _record_with_ui(self, max_duration: int) -> Optional[bytes]:
        """Record audio with UI feedback."""
        from rich.prompt import Confirm
        
        console.print(f"[green]Ready to record (max {max_duration}s)[/green]")
        console.print("Press [bold]Enter[/bold] to start recording...")
        
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            return None
        
        # Start recording
        self.recorder.start_recording()
        console.print("[red]🔴 Recording... Press Enter to stop[/red]")
        
        # Wait for stop or timeout
        start_time = time.time()
        try:
            # Simple blocking wait for Enter
            input()
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            # Stop recording
            audio_data = self.recorder.stop_recording()
        
        duration = time.time() - start_time
        console.print(f"[green]✅ Recorded {duration:.1f} seconds[/green]")
        
        return audio_data
    
    def _preview_and_edit(self, transcription: str) -> Optional[str]:
        """Show transcription preview with edit capability and mode switching."""
        from rich.prompt import Prompt
        from rich.table import Table
        
        console.print(Panel(
            transcription,
            title="📝 Transcription Preview",
            border_style="blue"
        ))
        
        # Show options
        options = Table(show_header=False, box=None)
        options.add_column("Option", style="cyan")
        options.add_column("Action", style="white")
        options.add_row("[Enter]", "Accept transcription")
        options.add_row("[Edit]", "Type to edit text")
        options.add_row("[R]", "Record again")
        options.add_row("[T]", "Switch to text input")
        options.add_row("[Ctrl+C]", "Cancel")
        console.print(options)
        
        while True:
            try:
                # Recreate prompt with current transcription to fix re-record bug
                edited = Prompt.ask(
                    "Action (Enter to accept, or edit text)",
                    default=transcription,
                    show_default=False
                )
                
                # Check for special commands
                if edited.lower() == 'r':
                    console.print("[cyan]Recording again...[/cyan]")
                    audio_data = self._record_with_ui(
                        max_duration=30
                    )
                    if audio_data:
                        console.print("[cyan]Transcribing new recording...[/cyan]")
                        result = self.whisper.transcribe_audio(
                            audio_data,
                            sample_rate=self.sample_rate,
                            language=None
                        )
                        transcription = result.text
                        console.print(Panel(
                            transcription,
                            title="📝 New Transcription",
                            border_style="blue"
                        ))
                        continue
                    else:
                        console.print("[yellow]Recording cancelled[/yellow]")
                        continue
                
                if edited.lower() == 't':
                    console.print("[cyan]Switching to text input...[/cyan]")
                    return self._fallback_to_text("Please provide your response:", question)
                
                if edited.strip() == "":
                    return None  # User cancelled
                
                # User edited the text - return the edited version
                logger.debug("User completed transcription editing")
                return edited
                
            except (KeyboardInterrupt, EOFError):
                logger.info("User cancelled transcription editing")
                return None
            except Exception as e:
                logger.warning(f"Error in transcription editing: {e}")
                return transcription
    
    def _maybe_enhance_transcription(self, text: str, question: Question) -> str:
        """Optionally enhance transcription with LLM."""
        
        
        # Check if post-processor is available
        if not hasattr(self, 'router') or not self.router or not self.router.postprocessor:
            # No post-processor available, show confirmation and return original
            logger.debug("No LLM post-processor available")
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return text
        
        if not self.router.postprocessor.is_enabled():
            # Post-processor disabled, show confirmation and return original  
            logger.debug("LLM post-processor disabled")
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return text
        
        from rich.prompt import Prompt, Confirm
        
        # Ask if user wants LLM enhancement for transcription
        console.print("\n🤖 [cyan]LLM Transcription Enhancement Available[/cyan]")
        console.print("[dim]This can improve transcription accuracy and structure while preserving meaning.[/dim]")
        if not Confirm.ask("Enhance transcription with LLM?", default=False):
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return text
        
        # Get additional context from user
        user_instruction = Prompt.ask(
            "Additional context/instructions for LLM transcription improvement",
            default="Please improve clarity and fix transcription errors while preserving exact meaning and context"
        )
        
        console.print("[cyan]⏳ Enhancing transcription with LLM...[/cyan]")
        
        try:
            enhanced = self.router.postprocessor.enhance_text_response(
                text=text,
                user_instruction=user_instruction,
                is_transcription=True,
                question_context=question.prompt
            )
            
            # Show enhanced version
            console.print(Panel(
                enhanced,
                title="🤖 LLM Enhanced Transcription",
                border_style="green"
            ))
            
            # Final confirmation
            if Confirm.ask("Use enhanced version?", default=True):
                console.print(f"[green]✅ Sending enhanced transcription to agent {question.agent_id[:8]}...[/green]")
                return enhanced
            else:
                console.print(f"[green]✅ Sending original transcription to agent {question.agent_id[:8]}...[/green]")
                return text
                
        except Exception as e:
            console.print(f"[red]❌ LLM enhancement failed: {e}[/red]")
            console.print(f"[green]✅ Sending original transcription to agent {question.agent_id[:8]}...[/green]")
            return text
    
    def _fallback_to_text(self, prompt: str, question: Question = None) -> str:
        """Fallback to text input with optional LLM enhancement."""
        from rich.prompt import Prompt
        
        console.print(Panel(
            prompt,
            title="📝 Text Input (Voice Fallback)",
            border_style="yellow"
        ))
        
        try:
            response = Prompt.ask("Your response")
            if not response.strip():
                return "ERROR: Empty response"
            
            # If we have question context, offer LLM enhancement like text handler
            if question and hasattr(self, 'router') and self.router and self.router.postprocessor:
                return self._maybe_enhance_response_for_fallback(response, question)
            
            return response
        except (KeyboardInterrupt, EOFError):
            return "ERROR: Input cancelled by user"
    
    def _maybe_enhance_response_for_fallback(self, response: str, question: Question) -> str:
        """Enhance fallback text response with LLM (same logic as TextQuestionHandler)."""
        if not self.router.postprocessor.is_enabled():
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return response
        
        from rich.prompt import Prompt, Confirm
        
        console.print("\n🤖 [cyan]LLM Enhancement Available[/cyan]")
        if not Confirm.ask("Enhance response with LLM?", default=False):
            console.print(f"[green]✅ Sending answer to agent {question.agent_id[:8]}...[/green]")
            return response
        
        user_instruction = Prompt.ask(
            "Additional instructions for LLM enhancement",
            default="Please improve clarity, structure, and completeness while preserving meaning"
        )
        
        console.print("[cyan]⏳ Enhancing response with LLM...[/cyan]")
        
        try:
            enhanced = self.router.postprocessor.enhance_text_response(
                text=response,
                user_instruction=user_instruction,
                is_transcription=False,
                question_context=question.prompt
            )
            
            # Show enhanced version
            console.print(Panel(
                enhanced,
                title="🤖 LLM Enhanced Response",
                border_style="green"
            ))
            
            # Confirm usage
            if Confirm.ask("Use enhanced version?", default=True):
                console.print(f"[green]✅ Sending enhanced answer to agent {question.agent_id[:8]}...[/green]")
                return enhanced
            else:
                console.print(f"[green]✅ Sending original answer to agent {question.agent_id[:8]}...[/green]")
                return response
                
        except Exception as e:
            console.print(f"[red]❌ LLM enhancement failed: {e}[/red]")
            console.print(f"[green]✅ Sending original answer to agent {question.agent_id[:8]}...[/green]")
            return response


class QuestionRouter:
    """Routes questions to appropriate handlers."""
    
    def __init__(self, config: GlobalConfig):
        self.config = config
        
        # Initialize post-processor FIRST
        try:
            from .postprocessing import HILPostProcessor
            logger.info(f"[DEBUG] Initializing HILPostProcessor with config.llm.enabled = {config.llm.enabled}")
            logger.info(f"[DEBUG] config.llm.api_key: {'SET' if config.llm.api_key else 'NOT_SET'}")
            self.postprocessor = HILPostProcessor(config.llm)
            logger.info(f"[DEBUG] HILPostProcessor created, is_enabled = {self.postprocessor.is_enabled()}")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM post-processor: {e}")
            self.postprocessor = None
        
        # Initialize handlers AFTER postprocessor
        self.text_handler = TextQuestionHandler(config)
        self.voice_handler = VoiceQuestionHandler(config)
        
        # Pass router reference to handlers for post-processing access
        self.text_handler.router = self
        self.voice_handler.router = self
        
        
        # Router and handlers fully initialized
    
    def process_question(self, question_file: Path) -> str:
        """Route question to appropriate handler based on type."""
        try:
            # Read question file
            file_content = question_file.read_text()
            data = json.loads(file_content)
            
            # Extract role from formatted question if present
            prompt = data['prompt']
            role = None
            if prompt.startswith('[') and '] ' in prompt:
                end_bracket = prompt.find('] ')
                if end_bracket > 1:
                    role = prompt[1:end_bracket]
                    prompt = prompt[end_bracket + 2:]  # Remove role prefix from prompt
            
            # Parse into Question object
            question = Question(
                type=data.get('type', 'text'),
                agent_id=data['agent_id'],
                timestamp=data['timestamp'],
                prompt=prompt,
                timeout=data.get('timeout', 300),
                metadata=data.get('metadata', {}),
                file_path=question_file,
                role=role
            )
            
            # Route to handler
            if question.type == 'voice':
                return self.voice_handler.handle(question)
            else:
                return self.text_handler.handle(question)
                
        except json.JSONDecodeError as e:
            # Try legacy text format
            logger.debug(f"JSON decode failed: {e}, falling back to legacy text format")
            prompt = question_file.read_text().strip()
            question = Question(
                type='text',
                agent_id=question_file.stem,
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                prompt=prompt,
                timeout=300,
                metadata={},
                file_path=question_file,
                role=None
            )
            return self.text_handler.handle(question)
        except Exception as e:
            logger.exception(f"Failed to process question: {e}")
            return f"ERROR: Failed to process question: {e}"


class HILEventHandler(FileSystemEventHandler):
    """Handles file system events for HIL questions."""
    
    def __init__(self, router: QuestionRouter, helpers_dir: Path):
        self.router = router
        self.helpers_dir = helpers_dir
        self.questions_dir = helpers_dir / "questions"
        self.answers_dir = helpers_dir / "answers"
    
    def on_created(self, event):
        """Handle new question files."""
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = Path(event.src_path)
            
            # Check if it's a question file
            if file_path.parent == self.questions_dir:
                if file_path.suffix in ['.txt', '.json']:
                    self._handle_question(file_path)
    
    def _handle_question(self, question_file: Path):
        """Process a question and save the answer."""
        try:
            agent_id = question_file.stem
            logger.info(f"Processing question from agent {agent_id}")
            
            # Wait for file to be fully written and ensure it's readable (race condition fix)
            max_attempts = 5
            file_content = None
            
            for attempt in range(max_attempts):
                try:
                    time.sleep(0.1 * (attempt + 1))  # Progressive backoff
                    file_content = question_file.read_text()
                    if file_content.strip():  # File has content
                        break
                except (FileNotFoundError, PermissionError, OSError) as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed to read question file after {max_attempts} attempts: {e}")
                        return
                    logger.debug(f"Attempt {attempt + 1} failed to read {question_file}: {e}")
                    
            if not file_content or not file_content.strip():
                logger.error(f"Question file {question_file} is empty or unreadable")
                return
            
            # Get answer from handler
            answer = self.router.process_question(question_file)
            
            # Save answer
            answer_file = self.answers_dir / f"{agent_id}.json"
            answer_data = {
                "answer": answer,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "agent_id": agent_id
            }
            answer_file.write_text(json.dumps(answer_data, indent=2))
            
            logger.info(f"Answer saved for agent {agent_id}")
            
            # Show user confirmation that answer was delivered
            console.print(f"[green]📤 Answer delivered to agent {agent_id[:8]}[/green]")
            console.print(Panel(
                f"Ready for next question...",
                title="🎧 HIL Listener - Waiting",
                border_style="cyan"
            ))
            
            # Clean up question file to prevent reprocessing
            try:
                question_file.unlink()
                logger.debug(f"Cleaned up question file: {question_file}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup question file {question_file}: {cleanup_error}")
            
            # Log return to waiting state
            logger.info(f"Completed processing for agent {agent_id}, returning to queue monitoring")
            
        except Exception as e:
            logger.exception(f"Failed to handle question: {e}")
            
            # Create error response for agent
            try:
                agent_id = question_file.stem
                error_answer = f"ERROR: HIL processing failed: {str(e)}"
                answer_file = self.answers_dir / f"{agent_id}.json"
                error_data = {
                    "answer": error_answer,
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "agent_id": agent_id,
                    "error": True
                }
                answer_file.write_text(json.dumps(error_data, indent=2))
                logger.info(f"Created error response for agent {agent_id}")
                
                # Show user error notification
                console.print(f"[red]❌ HIL Error for agent {agent_id[:8]}: {e}[/red]")
                console.print(Panel(
                    f"Error response sent to agent. Ready for next question...",
                    title="🎧 HIL Listener - Error Recovery",
                    border_style="red"
                ))
                
            except Exception as recovery_error:
                logger.error(f"Failed to create error response: {recovery_error}")
            
            # Even on error, try to cleanup the question file
            try:
                question_file.unlink()
                logger.debug(f"Cleaned up question file after error: {question_file}")
            except Exception:
                pass


def listen_command(helpers_dir: Optional[Path] = None):
    """Start the HIL listener daemon."""
    from ..config import load_config_with_env_override
    
    # Load configuration
    config = load_config_with_env_override()
    
    # Determine helpers directory
    if helpers_dir is None:
        helpers_dir = Path.cwd() / ".helpers"
    
    # Create directories if needed
    questions_dir = helpers_dir / "questions"
    answers_dir = helpers_dir / "answers"
    questions_dir.mkdir(parents=True, exist_ok=True)
    answers_dir.mkdir(parents=True, exist_ok=True)
    
    # Create router and handler
    router = QuestionRouter(config)
    event_handler = HILEventHandler(router, helpers_dir)
    
    # Setup file watcher
    observer = Observer()
    observer.schedule(event_handler, str(questions_dir), recursive=False)
    
    # Start listening
    console.print(Panel(
        f"Listening for questions in: {questions_dir}",
        title="🎧 HIL Listener Started",
        border_style="green"
    ))
    
    observer.start()
    
    try:
        logger.info("HIL Listener started successfully - monitoring queue")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping listener...[/yellow]")
        logger.info("HIL Listener stopping...")
        observer.stop()
    
    observer.join()
    console.print("[green]Listener stopped.[/green]")


if __name__ == "__main__":
    listen_command()