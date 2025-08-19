"""Voice recording and transcription command for Claude Helpers."""

import sys
import time
import signal
import logging
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich import box

from .config import load_config_with_env_override, ConfigNotFoundError, ConfigValidationError
from .audio import create_recorder_for_transcription, RecordingError, DeviceError, get_default_device
from .audio.recorder import CrossPlatformRecorder
from .transcription import create_whisper_client, TranscriptionError, NetworkError, APIError

logger = logging.getLogger(__name__)
console = Console(file=sys.stderr)  # Use stderr for UI, stdout for Claude output


class VoiceError(Exception):
    """Base voice command error."""
    pass


class VoiceRecordingUI:
    """Rich CLI interface for voice recording."""
    
    def __init__(self, console: Console):
        self.console = console
        self.is_cancelled = False
        
        # Setup signal handlers for graceful interruption
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
    
    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        self.is_cancelled = True
    
    def show_setup_info(self, config, device_name: Optional[str] = None, actual_sample_rate: Optional[int] = None):
        """Show recording setup information."""
        setup_info = Table(show_header=False, box=box.ROUNDED)
        setup_info.add_column("Setting", style="cyan")
        setup_info.add_column("Value", style="white")
        
        sample_rate_to_show = actual_sample_rate or config.audio.sample_rate
        setup_info.add_row("Sample Rate", f"{sample_rate_to_show} Hz")
        setup_info.add_row("Channels", "Mono" if config.audio.channels == 1 else "Stereo")
        setup_info.add_row("Audio Device", device_name or "Default")
        
        self.console.print(Panel(
            setup_info,
            title="🎤 Voice Recording Setup",
            title_align="left",
            border_style="blue"
        ))
    
    def show_recording_prompt(self):
        """Display recording instructions."""
        instructions = Text()
        instructions.append("Press ", style="white")
        instructions.append("ENTER", style="bold green")
        instructions.append(" to start recording\n", style="white")
        instructions.append("Press ", style="white") 
        instructions.append("ENTER", style="bold red")
        instructions.append(" again to stop recording\n", style="white")
        instructions.append("Press ", style="white")
        instructions.append("Ctrl+C", style="bold yellow")
        instructions.append(" to cancel", style="white")
        
        self.console.print(Panel(
            instructions,
            title="📝 Instructions",
            border_style="green"
        ))
        
        self.console.print("[bold]Ready to record. Press ENTER to start...[/bold]")
        
        try:
            input()  # Wait for Enter key
            return not self.is_cancelled
        except (KeyboardInterrupt, EOFError):
            self.is_cancelled = True
            return False
    
    def start_recording_display(self):
        """Show recording in progress interface."""
        return RecordingDisplay(self.console)
    
    def show_transcription_progress(self):
        """Display transcription progress."""
        return TranscriptionProgress(self.console)
    
    def display_result(self, transcription: str):
        """Show final transcription result."""
        self.console.print(Panel(
            transcription,
            title="✅ Transcription Complete",
            border_style="green",
            padding=(1, 2)
        ))
    
    def display_error(self, error_msg: str, suggestions: Optional[list] = None):
        """Display error message with optional suggestions."""
        error_panel = Text(error_msg, style="red")
        
        if suggestions:
            error_panel.append("\n\nSuggestions:\n", style="yellow")
            for i, suggestion in enumerate(suggestions, 1):
                error_panel.append(f"{i}. {suggestion}\n", style="white")
        
        self.console.print(Panel(
            error_panel,
            title="❌ Error",
            border_style="red"
        ))


class RecordingDisplay:
    """Live display for recording progress."""
    
    def __init__(self, console: Console):
        self.console = console
        self.start_time = time.time()
        self.live = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.live = Live(self._get_display(), console=self.console, refresh_per_second=4)
        self.live.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()
    
    def _get_display(self):
        """Generate current display."""
        duration = time.time() - self.start_time
        
        # Create recording status table
        status = Table(show_header=False, box=box.ROUNDED)
        status.add_column("Item", style="cyan", width=12)
        status.add_column("Status", style="white")
        
        status.add_row("🔴 Recording", "IN PROGRESS")
        status.add_row("⏱️  Duration", f"{duration:.1f}s")
        status.add_row("🎯 Quality", "Optimized for OpenAI Whisper")
        
        instructions = Text()
        instructions.append("Press ", style="white")
        instructions.append("ENTER", style="bold red")
        instructions.append(" to stop recording", style="white")
        
        return Panel(
            f"{status}\n\n{instructions}",
            title="🎙️  Recording Audio...",
            border_style="red"
        )
    
    def update(self, duration: float, volume: Optional[float] = None):
        """Update display with current stats."""
        if self.live:
            self.live.update(self._get_display())


class TranscriptionProgress:
    """Progress display for transcription."""
    
    def __init__(self, console: Console):
        self.console = console
        self.live = None
    
    def __enter__(self):
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )
        
        self.task_id = progress.add_task("Transcribing audio...", total=None)
        self.live = Live(
            Panel(progress, title="🧠 AI Processing", border_style="blue"),
            console=self.console
        )
        self.live.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()


def voice_command() -> None:
    """Main voice command entry point.
    
    Records audio from microphone and transcribes it using OpenAI Whisper.
    Outputs transcribed text to stdout for Claude Code integration.
    """
    ui = VoiceRecordingUI(console)
    
    try:
        # Load configuration
        config = load_config_with_env_override()
        
        # Check if we have a valid device and get its actual sample rate
        if config.audio.device_id is None:
            device = get_default_device()
            device_name = device.name if device else "Default"
            actual_sample_rate = device.sample_rate if device else 44100
            device_id = device.id if device else None
        else:
            from .audio.devices import get_device_info
            try:
                device_info = get_device_info(config.audio.device_id)
                device_name = device_info.name
                actual_sample_rate = int(device_info.default_sample_rate)
                device_id = config.audio.device_id
            except Exception as e:
                console.print(f"[yellow]Warning: Could not get device info: {e}[/yellow]")
                device_name = f"Device {config.audio.device_id}"
                actual_sample_rate = config.audio.sample_rate
                device_id = config.audio.device_id
        
        # Show setup information
        ui.show_setup_info(config, device_name, actual_sample_rate)
        
        # Initialize recorder with device's native sample rate
        recorder = CrossPlatformRecorder(
            device_id=device_id,
            sample_rate=actual_sample_rate,
            channels=config.audio.channels
        )
        
        # Initialize transcription client
        whisper = create_whisper_client(config.openai_api_key)
        
        # Show recording prompt and wait for user
        if not ui.show_recording_prompt():
            console.print("\n[yellow]Recording cancelled by user[/yellow]")
            sys.exit(1)
        
        # Start recording
        recorder.start_recording()
        
        # Show live recording display
        with ui.start_recording_display() as display:
            try:
                input()  # Wait for Enter to stop
            except (KeyboardInterrupt, EOFError):
                ui.is_cancelled = True
        
        # Check if cancelled during recording
        if ui.is_cancelled:
            if recorder.is_recording():
                recorder.stop_recording()  # Clean stop
            console.print("\n[yellow]Recording cancelled by user[/yellow]")
            sys.exit(1)
        
        # Stop recording and get audio data
        audio_data = recorder.stop_recording()
        
        if len(audio_data) == 0:
            console.print("[red]No audio data captured. Please check your microphone.[/red]")
            sys.exit(1)
        
        # Show transcription progress
        with ui.show_transcription_progress():
            result = whisper.transcribe_audio(
                audio_data,
                sample_rate=actual_sample_rate,
                language=None  # Auto-detect language for better quality
            )
        
        # Display result in UI
        ui.display_result(result.text)
        
        # Output to stdout for Claude Code (this becomes the next prompt)
        print(result.text)
        
    except ConfigNotFoundError as e:
        ui.display_error(
            "Configuration not found",
            [
                "Run 'claude-helpers init --global-only' to set up your API key",
                "Or set OPENAI_API_KEY environment variable",
                "Make sure you have a valid OpenAI account with API access"
            ]
        )
        sys.exit(1)
        
    except ConfigValidationError as e:
        ui.display_error(
            f"Configuration error: {e}",
            [
                "Check your configuration file for invalid values", 
                "Run 'claude-helpers init --global-only' to reconfigure",
                "Verify your OpenAI API key format"
            ]
        )
        sys.exit(1)
        
    except DeviceError as e:
        ui.display_error(
            f"Audio device error: {e}",
            [
                "Check that your microphone is connected and working",
                "On macOS: Grant microphone permission in System Preferences",
                "On Linux: Check audio system (PulseAudio/ALSA) is running",
                "Try selecting a different audio device"
            ]
        )
        sys.exit(1)
        
    except RecordingError as e:
        ui.display_error(
            f"Recording failed: {e}",
            [
                "Check that your microphone is not being used by another app",
                "Verify audio device permissions",
                "Try restarting the audio service on your system"
            ]
        )
        sys.exit(1)
        
    except NetworkError as e:
        ui.display_error(
            f"Network error: {e}",
            [
                "Check your internet connection",
                "Verify you can access OpenAI API (api.openai.com)",
                "If behind a proxy, configure it in your system settings"
            ]
        )
        sys.exit(1)
        
    except APIError as e:
        ui.display_error(
            f"API error: {e}",
            [
                "Check your OpenAI API key is valid and active",
                "Verify you have sufficient API credits",
                "Wait a moment if you're hitting rate limits"
            ]
        )
        sys.exit(1)
        
    except TranscriptionError as e:
        ui.display_error(
            f"Transcription failed: {e}",
            [
                "Try recording again with clearer audio",
                "Ensure the recording is at least 1 second long",
                "Check your OpenAI API key and credits"
            ]
        )
        sys.exit(1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Recording cancelled by user[/yellow]")
        sys.exit(1)
        
    except Exception as e:
        logger.exception("Unexpected error in voice command")
        ui.display_error(
            f"Unexpected error: {e}",
            [
                "This is likely a bug. Please report it",
                "Try restarting the command",
                "Check the logs for more details"
            ]
        )
        sys.exit(1)


if __name__ == "__main__":
    voice_command()