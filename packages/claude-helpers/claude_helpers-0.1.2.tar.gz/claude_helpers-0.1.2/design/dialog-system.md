# Claude Helpers - Cross-Platform Dialog System Design

## Overview

Cross-platform GUI dialog system for human-in-the-loop interactions, with automatic tool detection and graceful fallbacks from GUI to terminal input.

## Supported Platforms & Tools

### macOS
- **Primary**: AppleScript (`osascript`) - Native system dialogs
- **Fallback**: Terminal input

### Linux
- **Primary**: Zenity (GTK+ dialogs)
- **Secondary**: Yad (enhanced Zenity fork)
- **Tertiary**: Dialog (text-based UI)
- **Fallback**: Terminal input

## Dialog Types

### Text Input
```python
answer = show_dialog("What is your name?", "text")
# Returns: "John Doe"
```

### Yes/No Questions
```python
answer = show_dialog("Should I proceed?", "yesno") 
# Returns: "yes" or "no"
```

### Multiple Choice
```python
answer = show_dialog("Choose framework:", "select", ["React", "Vue", "Svelte"])
# Returns: "React" (selected option)
```

## Implementation

### Main Dialog Interface
```python
# src/claude_helpers/hil/dialog.py
import platform
import subprocess
import shlex
from typing import List, Optional

class CrossPlatformDialog:
    def __init__(self):
        self.platform = platform.system().lower()
        self.available_tools = self._detect_tools()
    
    def _detect_tools(self) -> List[str]:
        """Detect available dialog tools on current platform"""
        tools = []
        
        if self.platform == 'darwin':  # macOS
            tools.append('osascript')
        elif self.platform == 'linux':
            # Check GUI tools availability
            for tool in ['zenity', 'yad', 'dialog']:
                try:
                    subprocess.run([tool, '--version'], 
                                 capture_output=True, 
                                 check=True,
                                 timeout=5)
                    tools.append(tool)
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    pass
        
        # Terminal input always available as final fallback
        tools.append('terminal')
        return tools
    
    def show_dialog(self, message: str, 
                   dialog_type: str = 'text', 
                   options: List[str] = None) -> str:
        """Show dialog using best available method"""
        
        # Try each available tool in priority order
        for tool in self.available_tools:
            try:
                if tool == 'osascript':
                    return self._osascript_dialog(message, dialog_type, options)
                elif tool == 'zenity':
                    return self._zenity_dialog(message, dialog_type, options)
                elif tool == 'yad':
                    return self._yad_dialog(message, dialog_type, options)
                elif tool == 'dialog':
                    return self._dialog_dialog(message, dialog_type, options)
                elif tool == 'terminal':
                    return self._terminal_dialog(message, dialog_type, options)
            except Exception as e:
                print(f"Dialog tool {tool} failed: {e}", file=sys.stderr)
                continue
        
        # Ultimate fallback
        return input(f"{message}: ")
```

### macOS AppleScript Implementation
```python
def _osascript_dialog(self, message: str, dialog_type: str, options: List[str]) -> str:
    """macOS native dialogs via AppleScript"""
    
    if dialog_type == 'yesno':
        script = f'''
        display dialog {shlex.quote(message)} ¬
            buttons {{"No", "Yes"}} ¬
            default button "Yes" ¬
            with title "Claude Helpers"
        return button returned of result
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        return "yes" if result.stdout.strip() == "Yes" else "no"
    
    elif dialog_type == 'select' and options:
        choices = '", "'.join(options)
        script = f'''
        choose from list {{"{choices}"}} ¬
            with prompt {shlex.quote(message)} ¬
            with title "Claude Helpers"
        return result as string
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout.strip().replace('false', '')  # Handle cancel
    
    else:  # text input
        script = f'''
        display dialog {shlex.quote(message)} ¬
            default answer "" ¬
            buttons {{"OK"}} ¬
            default button "OK" ¬
            with title "Claude Helpers"
        return text returned of result
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
```

### Linux Zenity Implementation
```python
def _zenity_dialog(self, message: str, dialog_type: str, options: List[str]) -> str:
    """Linux Zenity GTK+ dialogs"""
    
    if dialog_type == 'yesno':
        result = subprocess.run([
            'zenity', '--question', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--width', '400'
        ], timeout=30)
        return "yes" if result.returncode == 0 else "no"
    
    elif dialog_type == 'select' and options:
        cmd = [
            'zenity', '--list', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--column', 'Options',
            '--width', '400',
            '--height', '300'
        ]
        cmd.extend(options)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    
    else:  # text input
        result = subprocess.run([
            'zenity', '--entry', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--width', '400'
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
```

### Linux Yad Implementation
```python
def _yad_dialog(self, message: str, dialog_type: str, options: List[str]) -> str:
    """Linux Yad dialogs (enhanced Zenity)"""
    
    if dialog_type == 'yesno':
        result = subprocess.run([
            'yad', '--question', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--width', '400',
            '--center'
        ], timeout=30)
        return "yes" if result.returncode == 0 else "no"
    
    elif dialog_type == 'select' and options:
        cmd = [
            'yad', '--list', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--column', 'Options',
            '--width', '400',
            '--height', '300',
            '--center',
            '--no-headers'
        ]
        cmd.extend(options)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    
    else:  # text input
        result = subprocess.run([
            'yad', '--entry', 
            '--text', message,
            '--title', 'Claude Helpers',
            '--width', '400',
            '--center'
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
```

### Linux Dialog Implementation (TUI)
```python
def _dialog_dialog(self, message: str, dialog_type: str, options: List[str]) -> str:
    """Linux dialog text-based UI"""
    
    if dialog_type == 'yesno':
        result = subprocess.run([
            'dialog', '--yesno', message, 
            '10', '60'
        ], timeout=30)
        return "yes" if result.returncode == 0 else "no"
    
    elif dialog_type == 'select' and options:
        # Build menu items: tag item ...
        menu_items = []
        for i, option in enumerate(options, 1):
            menu_items.extend([str(i), option])
        
        result = subprocess.run([
            'dialog', '--menu', message,
            '15', '60', str(len(options))
        ] + menu_items, 
        capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            selection = int(result.stdout.strip())
            return options[selection - 1]
        return ""
    
    else:  # text input
        result = subprocess.run([
            'dialog', '--inputbox', message,
            '10', '60'
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
```

### Terminal Fallback
```python
def _terminal_dialog(self, message: str, dialog_type: str, options: List[str]) -> str:
    """Terminal fallback - works everywhere"""
    print(f"\n{'='*60}")
    print(f"[Claude Helpers] {message}")
    print('='*60)
    
    if dialog_type == 'yesno':
        while True:
            answer = input("Enter (y/n): ").lower().strip()
            if answer in ['y', 'yes']:
                return 'yes'
            elif answer in ['n', 'no']:
                return 'no'
            print("Please enter 'y' for yes or 'n' for no")
    
    elif dialog_type == 'select' and options:
        print("\nOptions:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print()
        
        while True:
            try:
                choice = int(input(f"Select number (1-{len(options)}): ")) - 1
                if 0 <= choice < len(options):
                    return options[choice]
                print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    else:  # text input
        return input("Answer: ").strip()

# Global instance
dialog = CrossPlatformDialog()

def show_dialog(message: str, dialog_type: str = 'text', options: List[str] = None) -> str:
    """Show cross-platform dialog"""
    return dialog.show_dialog(message, dialog_type, options or [])
```

## Error Handling & Resilience

### Tool Detection Errors
```python
def _detect_tools(self) -> List[str]:
    """Robust tool detection with error handling"""
    tools = []
    
    if self.platform == 'darwin':
        # Test osascript availability
        try:
            subprocess.run(['osascript', '-e', 'return "test"'], 
                         capture_output=True, check=True, timeout=5)
            tools.append('osascript')
        except:
            pass
    
    elif self.platform == 'linux':
        # Test each GUI tool
        for tool in ['zenity', 'yad', 'dialog']:
            try:
                # Test with version check
                result = subprocess.run([tool, '--version'], 
                                     capture_output=True, 
                                     check=True,
                                     timeout=5)
                
                # Additional functionality tests
                if tool == 'zenity':
                    # Test if zenity can create actual dialogs
                    subprocess.run(['zenity', '--info', '--text', 'test', '--timeout', '1'], 
                                 capture_output=True, timeout=5)
                
                tools.append(tool)
            except:
                continue
    
    # Terminal always available
    tools.append('terminal')
    return tools
```

### Execution Timeouts
```python
def _safe_execute(self, cmd: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute command with timeout and error handling"""
    try:
        return subprocess.run(cmd, 
                            capture_output=True, 
                            text=True, 
                            timeout=timeout,
                            check=False)  # Don't raise on non-zero exit
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Dialog timeout after {timeout} seconds")
    except FileNotFoundError:
        raise RuntimeError(f"Dialog tool not found: {cmd[0]}")
    except Exception as e:
        raise RuntimeError(f"Dialog execution failed: {str(e)}")
```

### Graceful Degradation
```python
def show_dialog(self, message: str, dialog_type: str = 'text', options: List[str] = None) -> str:
    """Show dialog with graceful degradation"""
    last_error = None
    
    for tool in self.available_tools:
        try:
            if tool == 'terminal':
                # Terminal fallback always works
                return self._terminal_dialog(message, dialog_type, options)
            else:
                # Try GUI tool
                result = self._execute_gui_dialog(tool, message, dialog_type, options)
                if result is not None:  # Success
                    return result
                    
        except Exception as e:
            last_error = e
            print(f"Dialog tool {tool} failed: {e}", file=sys.stderr)
            continue
    
    # Ultimate fallback if everything fails
    print(f"All dialog tools failed. Last error: {last_error}", file=sys.stderr)
    return input(f"{message}: ")
```

## Integration with HIL System

### Dialog Context Enhancement
```python
def show_dialog(message: str, dialog_type: str = 'text', options: List[str] = None,
                agent_info: dict = None) -> str:
    """Enhanced dialog with agent context"""
    
    # Add agent context to message
    if agent_info:
        agent_name = agent_info.get('name', 'Unknown Agent')
        working_dir = agent_info.get('working_dir', '')
        context_message = f"[{agent_name}]\nProject: {working_dir}\n\n{message}"
    else:
        context_message = message
    
    return dialog.show_dialog(context_message, dialog_type, options)
```

### Queue Status Integration
```python
def show_dialog_with_queue_info(message: str, dialog_type: str = 'text', 
                               options: List[str] = None,
                               queue_position: int = 1,
                               total_questions: int = 1) -> str:
    """Show dialog with queue information"""
    
    if total_questions > 1:
        queue_info = f"[Question {queue_position}/{total_questions}]\n\n"
        message = queue_info + message
    
    return dialog.show_dialog(message, dialog_type, options)
```

## Testing Strategy

### Platform-Specific Tests
```python
# tests/test_dialog_system.py
import pytest
import platform
from claude_helpers.hil.dialog import CrossPlatformDialog

class TestDialogSystem:
    def test_tool_detection(self):
        """Test tool detection on current platform"""
        dialog = CrossPlatformDialog()
        tools = dialog.available_tools
        
        # Terminal should always be available
        assert 'terminal' in tools
        
        # Platform-specific checks
        if platform.system() == 'Darwin':
            # macOS should have osascript
            assert 'osascript' in tools
        elif platform.system() == 'Linux':
            # Linux might have zenity, yad, or dialog
            gui_tools = [t for t in tools if t != 'terminal']
            assert len(gui_tools) >= 0  # May have none in CI
    
    def test_terminal_fallback(self):
        """Test terminal fallback works"""
        dialog = CrossPlatformDialog()
        # Mock user input
        with patch('builtins.input', return_value='test answer'):
            result = dialog._terminal_dialog("Test question?", "text")
            assert result == 'test answer'
    
    def test_dialog_types(self):
        """Test different dialog types"""
        dialog = CrossPlatformDialog()
        
        # Text input
        with patch('builtins.input', return_value='text response'):
            result = dialog.show_dialog("Enter text:", "text")
            assert result == 'text response'
        
        # Yes/no
        with patch('builtins.input', return_value='y'):
            result = dialog.show_dialog("Proceed?", "yesno")
            assert result == 'yes'
        
        # Select
        with patch('builtins.input', return_value='2'):
            result = dialog.show_dialog("Choose:", "select", ["A", "B", "C"])
            assert result == 'B'
```

### Integration Tests
- Test with actual GUI tools in desktop environments
- Test fallback behavior when GUI not available
- Test timeout handling and recovery
- Test with various message lengths and special characters