# Epic 4: 🖥️ Dialog System

**Priority**: HIGH - HIL dependency (can develop parallel with Voice)
**Estimated Time**: 4-5 days
**Dependencies**: Epic 1 (Foundation), Epic 2 (Configuration)

## Overview

Реализация cross-platform GUI dialog system с fallback mechanisms. Это critical dependency для HIL System и независима от Voice System для parallel development.

## Definition of Done

- [ ] Cross-platform dialog detection работает
- [ ] macOS AppleScript dialogs functional
- [ ] Linux GUI dialogs (Zenity/Yad/Dialog) working
- [ ] Terminal fallback system complete
- [ ] Dialog system API unified и consistent
- [ ] Error handling и fallback chain robust
- [ ] Performance optimization для dialog response time

---

## Task 4.1: Dialog Tool Detection
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать систему для detection available dialog tools на каждой платформе

### Deliverables
- `src/claude_helpers/hil/dialog_detection.py`
- Platform-specific tool enumeration
- Capability testing для each tool
- Priority ordering для fallback chain

### Core Detection Functions
```python
@dataclass
class DialogTool:
    name: str
    command: str
    capabilities: List[str]
    priority: int
    platform: str
    available: bool

def detect_available_tools() -> List[DialogTool]:
    """Detect all available dialog tools on current platform"""

def get_best_tool(required_capabilities: List[str]) -> Optional[DialogTool]:
    """Get best available tool for required capabilities"""

def test_tool_functionality(tool: DialogTool) -> bool:
    """Test if dialog tool works properly"""

class DialogCapability(Enum):
    TEXT_INPUT = "text_input"
    PASSWORD_INPUT = "password_input"
    FILE_SELECTION = "file_selection"
    CONFIRMATION = "confirmation"
    MESSAGE_DISPLAY = "message_display"
    CHOICE_SELECTION = "choice_selection"
```

### Platform-Specific Tools

#### macOS Detection
```python
def detect_macos_tools() -> List[DialogTool]:
    return [
        DialogTool("applescript", "osascript", 
                  [DialogCapability.TEXT_INPUT, DialogCapability.CONFIRMATION], 1, "macos", True),
        DialogTool("terminal", "built-in", 
                  [DialogCapability.TEXT_INPUT, DialogCapability.CONFIRMATION], 10, "macos", True),
    ]
```

#### Linux Detection
```python
def detect_linux_tools() -> List[DialogTool]:
    tools = []
    
    # Check for Zenity
    if shutil.which("zenity"):
        tools.append(DialogTool("zenity", "zenity", 
                               [DialogCapability.TEXT_INPUT, DialogCapability.FILE_SELECTION], 1, "linux", True))
    
    # Check for Yad
    if shutil.which("yad"):
        tools.append(DialogTool("yad", "yad", 
                               [DialogCapability.TEXT_INPUT, DialogCapability.CHOICE_SELECTION], 2, "linux", True))
    
    # Check for Dialog
    if shutil.which("dialog"):
        tools.append(DialogTool("dialog", "dialog", 
                               [DialogCapability.TEXT_INPUT, DialogCapability.CONFIRMATION], 3, "linux", True))
    
    # Terminal fallback always available
    tools.append(DialogTool("terminal", "built-in", 
                           [DialogCapability.TEXT_INPUT, DialogCapability.CONFIRMATION], 10, "linux", True))
    
    return tools
```

### Acceptance Criteria
- All available tools на platform корректно detected
- Tool capabilities accurately assessed
- Priority ordering логичный для user experience
- Tool testing не требует user interaction
- Detection быстрый (< 1 second)

### Test Commands
```python
from claude_helpers.hil.dialog_detection import detect_available_tools, get_best_tool
from claude_helpers.hil.dialog_detection import DialogCapability

tools = detect_available_tools()
assert len(tools) > 0, "Should find at least terminal fallback"

# Test getting best tool for text input
best = get_best_tool([DialogCapability.TEXT_INPUT])
assert best is not None, "Should find tool for text input"
assert DialogCapability.TEXT_INPUT in best.capabilities
```

---

## Task 4.2: macOS AppleScript Dialog Implementation
**Time**: 1.5 days | **Complexity**: 🔴 High

### Описание
Реализовать AppleScript-based dialogs для macOS с full functionality

### Deliverables
- `src/claude_helpers/hil/dialogs/applescript.py`
- Text input dialogs с customization
- Confirmation dialogs
- Choice selection dialogs
- Error handling для AppleScript execution

### AppleScript Dialog Implementation
```python
class AppleScriptDialog:
    def __init__(self):
        """Initialize AppleScript dialog handler"""
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input dialog"""
        script = f'''
        display dialog "{message}" \\
            default answer "{default_text}" \\
            with title "{title}" \\
            buttons {{"Cancel", "OK"}} \\
            default button "OK"
        '''
        return self._execute_script(script)
    
    def show_confirmation(self, title: str, message: str, 
                         buttons: List[str] = None) -> Optional[str]:
        """Show confirmation dialog"""
        if not buttons:
            buttons = ["Cancel", "OK"]
        
        buttons_str = '{' + ', '.join(f'"{btn}"' for btn in buttons) + '}'
        script = f'''
        display dialog "{message}" \\
            with title "{title}" \\
            buttons {buttons_str} \\
            default button "{buttons[-1]}"
        '''
        return self._execute_script(script)
    
    def show_choice_selection(self, title: str, message: str, 
                            choices: List[str]) -> Optional[str]:
        """Show choice selection dialog"""
        choices_str = '{' + ', '.join(f'"{choice}"' for choice in choices) + '}'
        script = f'''
        choose from list {choices_str} \\
            with title "{title}" \\
            with prompt "{message}"
        '''
        return self._execute_script(script)
    
    def _execute_script(self, script: str) -> Optional[str]:
        """Execute AppleScript and parse result"""
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            return self._parse_applescript_result(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            if "User canceled" in e.stderr:
                return None  # User cancelled
            raise DialogError(f"AppleScript error: {e.stderr}")
    
    def _parse_applescript_result(self, result: str) -> str:
        """Parse AppleScript result format"""
        # AppleScript returns various formats, need to parse correctly
        if result.startswith("text returned:"):
            return result.split(":", 1)[1].strip()
        elif result == "false":
            return None  # User cancelled
        else:
            return result
```

### AppleScript Specifics
- **Text Input**: `display dialog` with `default answer`
- **Confirmation**: `display dialog` с custom buttons
- **Choice Selection**: `choose from list` command
- **Error Handling**: Parse AppleScript error codes
- **User Cancellation**: Handle gracefully

### Security Considerations
- AppleScript injection prevention
- Safe string escaping
- Timeout management
- Process cleanup

### Acceptance Criteria
- Text input dialogs работают с Unicode text
- Confirmation dialogs поддерживают custom buttons
- Choice selection handles multiple options
- User cancellation detected properly
- AppleScript errors handled gracefully
- Dialog appearance native и consistent

### Test Commands
```python
from claude_helpers.hil.dialogs.applescript import AppleScriptDialog

dialog = AppleScriptDialog()

# Test text input (manual testing required)
result = dialog.show_text_input("Test", "Enter some text:", "default")
# User interaction required

# Test confirmation
result = dialog.show_confirmation("Test", "Do you agree?", ["No", "Yes"])
# User interaction required

# Test script execution safety
try:
    dialog.show_text_input("Test", 'Malicious"; rm -rf /; echo "', "")
    # Should not execute dangerous commands
except:
    pass
```

---

## Task 4.3: Linux GUI Dialog Implementation
**Time**: 1.5 days | **Complexity**: 🔴 High

### Описание
Реализовать GUI dialogs для Linux using Zenity, Yad, и Dialog

### Deliverables
- `src/claude_helpers/hil/dialogs/zenity.py`
- `src/claude_helpers/hil/dialogs/yad.py`
- `src/claude_helpers/hil/dialogs/dialog.py`
- Unified interface для all Linux dialog tools
- Command generation и result parsing

### Zenity Implementation
```python
class ZenityDialog:
    def __init__(self):
        """Initialize Zenity dialog handler"""
        if not shutil.which("zenity"):
            raise DialogError("Zenity not available")
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input using Zenity"""
        cmd = [
            "zenity", "--entry",
            f"--title={title}",
            f"--text={message}",
            f"--entry-text={default_text}"
        ]
        return self._execute_command(cmd)
    
    def show_confirmation(self, title: str, message: str, 
                         buttons: List[str] = None) -> Optional[str]:
        """Show confirmation using Zenity"""
        cmd = [
            "zenity", "--question",
            f"--title={title}",
            f"--text={message}",
            "--no-wrap"
        ]
        
        # Zenity question dialog returns 0 for Yes, 1 for No
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return "Yes"
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                return "No"
            return None  # User cancelled or error
    
    def show_choice_selection(self, title: str, message: str, 
                            choices: List[str]) -> Optional[str]:
        """Show choice selection using Zenity list"""
        cmd = [
            "zenity", "--list",
            f"--title={title}",
            f"--text={message}",
            "--column=Options"
        ] + choices
        return self._execute_command(cmd)
    
    def _execute_command(self, cmd: List[str]) -> Optional[str]:
        """Execute Zenity command and return result"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # User cancelled
                return None
            raise DialogError(f"Zenity error: {e.stderr}")
```

### Yad Implementation
```python
class YadDialog:
    def __init__(self):
        """Initialize Yad dialog handler"""
        if not shutil.which("yad"):
            raise DialogError("Yad not available")
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input using Yad"""
        cmd = [
            "yad", "--entry",
            f"--title={title}",
            f"--text={message}",
            f"--entry-text={default_text}",
            "--button=Cancel:1",
            "--button=OK:0"
        ]
        return self._execute_command(cmd)
    
    def show_form_input(self, title: str, fields: List[FormField]) -> Optional[Dict[str, str]]:
        """Show multi-field form using Yad (unique feature)"""
        cmd = ["yad", "--form", f"--title={title}"]
        
        for field in fields:
            if field.field_type == "text":
                cmd.append(f"--field={field.label}")
            elif field.field_type == "password":
                cmd.append(f"--field={field.label}:H")  # Hidden field
        
        result = self._execute_command(cmd)
        if result:
            # Parse Yad form output (pipe-separated)
            values = result.split('|')
            return {field.name: value for field, value in zip(fields, values)}
        return None
```

### Dialog (ncurses) Implementation
```python
class NcursesDialog:
    def __init__(self):
        """Initialize ncurses Dialog handler"""
        if not shutil.which("dialog"):
            raise DialogError("Dialog not available")
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input using Dialog"""
        cmd = [
            "dialog", "--inputbox", message, "8", "60", default_text,
            "--title", title
        ]
        return self._execute_command(cmd)
    
    def _execute_command(self, cmd: List[str]) -> Optional[str]:
        """Execute Dialog command with proper TTY handling"""
        try:
            # Dialog needs TTY for ncurses
            result = subprocess.run(cmd, capture_output=True, text=True, check=True,
                                  stdin=sys.stdin, stderr=subprocess.PIPE)
            return result.stderr.strip()  # Dialog outputs to stderr
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:  # User cancelled
                return None
            raise DialogError(f"Dialog error: {e.stderr}")
```

### Acceptance Criteria
- Все dialog tools работают в своих environments
- Command injection prevented
- UTF-8 text поддерживается properly
- Error handling consistent across tools
- User cancellation handled uniformly
- Tool-specific features используются appropriately

### Test Commands
```bash
# Test Zenity (if available)
zenity --info --text="Test message" --title="Test"

# Test Yad (if available) 
yad --entry --title="Test" --text="Enter text:"

# Test Dialog (if available)
dialog --inputbox "Enter text:" 8 60
```

---

## Task 4.4: Terminal Fallback System
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Реализовать terminal-based dialog fallback для environments без GUI

### Deliverables
- `src/claude_helpers/hil/dialogs/terminal.py`
- Rich CLI-based input dialogs
- Cross-platform terminal compatibility
- Secure password input support

### Terminal Dialog Implementation
```python
class TerminalDialog:
    def __init__(self):
        """Initialize terminal-based dialog handler"""
        self.console = Console(stderr=True)  # Use stderr для UI
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input in terminal"""
        self.console.print(Panel.fit(f"[bold]{title}[/bold]"))
        self.console.print(f"{message}")
        
        if default_text:
            self.console.print(f"[dim](default: {default_text})[/dim]")
        
        try:
            result = Prompt.ask("Enter text", default=default_text or None, console=self.console)
            return result if result else None
        except KeyboardInterrupt:
            return None
    
    def show_password_input(self, title: str, message: str) -> Optional[str]:
        """Show secure password input"""
        self.console.print(Panel.fit(f"[bold]{title}[/bold]"))
        self.console.print(f"{message}")
        
        try:
            return Prompt.ask("Enter password", password=True, console=self.console)
        except KeyboardInterrupt:
            return None
    
    def show_confirmation(self, title: str, message: str, 
                         buttons: List[str] = None) -> Optional[str]:
        """Show confirmation in terminal"""
        if not buttons:
            buttons = ["No", "Yes"]
        
        self.console.print(Panel.fit(f"[bold]{title}[/bold]"))
        self.console.print(f"{message}")
        
        try:
            return Confirm.ask(f"Choose", default=False, console=self.console)
        except KeyboardInterrupt:
            return None
    
    def show_choice_selection(self, title: str, message: str, 
                            choices: List[str]) -> Optional[str]:
        """Show choice selection in terminal"""
        self.console.print(Panel.fit(f"[bold]{title}[/bold]"))
        self.console.print(f"{message}")
        
        # Create numbered choices
        for i, choice in enumerate(choices, 1):
            self.console.print(f"  {i}. {choice}")
        
        try:
            while True:
                selection = IntPrompt.ask(
                    "Select option (number)", 
                    choices=list(range(1, len(choices) + 1)),
                    console=self.console
                )
                return choices[selection - 1]
        except KeyboardInterrupt:
            return None
    
    def show_multi_field_form(self, title: str, fields: List[FormField]) -> Optional[Dict[str, str]]:
        """Show multi-field form in terminal"""
        self.console.print(Panel.fit(f"[bold]{title}[/bold]"))
        
        results = {}
        try:
            for field in fields:
                if field.field_type == "password":
                    result = self.show_password_input(field.label, "")
                else:
                    result = self.show_text_input(field.label, "", field.default or "")
                
                if result is None:  # User cancelled
                    return None
                
                results[field.name] = result
            
            return results
        except KeyboardInterrupt:
            return None
```

### Rich CLI Features
- **Panels**: Визуально separated dialog sections
- **Colors**: Different colors для different elements
- **Progress**: Progress bars для multi-step forms
- **Validation**: Input validation с error messages
- **Keyboard**: Proper keyboard interrupt handling

### Terminal Compatibility
- **Cross-platform**: Works on Windows/macOS/Linux terminals
- **Unicode Support**: Proper UTF-8 handling
- **Screen Size**: Adaptive to terminal dimensions
- **Color Support**: Graceful fallback если no colors

### Acceptance Criteria
- All dialog types работают в terminal environment
- User experience intuitive и consistent
- Keyboard interrupts handled gracefully
- Unicode text supported properly
- Terminal размеры respected
- Password input secure (не показывает characters)

### Test Commands
```python
from claude_helpers.hil.dialogs.terminal import TerminalDialog

dialog = TerminalDialog()

# Test text input
result = dialog.show_text_input("Test Input", "Enter some text:", "default")
print(f"Result: {result}")

# Test confirmation
result = dialog.show_confirmation("Test Confirm", "Do you agree?")
print(f"Confirmed: {result}")

# Test choice selection  
result = dialog.show_choice_selection("Test Choice", "Pick one:", ["Option 1", "Option 2", "Option 3"])
print(f"Selected: {result}")
```

---

## Task 4.5: Unified Dialog Interface
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Создать unified interface that automatically selects best dialog method

### Deliverables
- `src/claude_helpers/hil/dialog.py` unified interface
- Automatic tool selection logic
- Configuration override support
- Consistent API across all platforms

### Unified Dialog Interface
```python
class DialogManager:
    def __init__(self, config: HILConfig):
        """Initialize with configuration preferences"""
        self.config = config
        self.available_tools = detect_available_tools()
        self._dialog_implementations = self._initialize_implementations()
    
    def show_text_input(self, title: str, message: str, 
                       default_text: str = "") -> Optional[str]:
        """Show text input using best available method"""
        tool = self._get_best_tool([DialogCapability.TEXT_INPUT])
        impl = self._dialog_implementations[tool.name]
        return impl.show_text_input(title, message, default_text)
    
    def show_confirmation(self, title: str, message: str, 
                         buttons: List[str] = None) -> Optional[str]:
        """Show confirmation using best available method"""
        tool = self._get_best_tool([DialogCapability.CONFIRMATION])
        impl = self._dialog_implementations[tool.name]
        return impl.show_confirmation(title, message, buttons)
    
    def show_choice_selection(self, title: str, message: str, 
                            choices: List[str]) -> Optional[str]:
        """Show choice selection using best available method"""
        tool = self._get_best_tool([DialogCapability.CHOICE_SELECTION])
        impl = self._dialog_implementations[tool.name]
        return impl.show_choice_selection(title, message, choices)
    
    def _get_best_tool(self, required_capabilities: List[DialogCapability]) -> DialogTool:
        """Get best tool for capabilities, respecting config preferences"""
        # Check config override first
        if self.config.dialog_tool != "auto":
            preferred = next((t for t in self.available_tools 
                            if t.name == self.config.dialog_tool), None)
            if preferred and preferred.available:
                return preferred
        
        # Find best available tool
        suitable_tools = [t for t in self.available_tools 
                         if all(cap in t.capabilities for cap in required_capabilities)]
        
        if not suitable_tools:
            # Fallback to terminal
            return next(t for t in self.available_tools if t.name == "terminal")
        
        return min(suitable_tools, key=lambda t: t.priority)
    
    def _initialize_implementations(self) -> Dict[str, Any]:
        """Initialize dialog implementations for available tools"""
        implementations = {}
        
        for tool in self.available_tools:
            if tool.name == "applescript":
                implementations["applescript"] = AppleScriptDialog()
            elif tool.name == "zenity":
                implementations["zenity"] = ZenityDialog()
            elif tool.name == "yad":
                implementations["yad"] = YadDialog()
            elif tool.name == "dialog":
                implementations["dialog"] = NcursesDialog()
            elif tool.name == "terminal":
                implementations["terminal"] = TerminalDialog()
        
        return implementations

# Convenience function for simple usage
def show_dialog(dialog_type: str, title: str, message: str, **kwargs) -> Optional[str]:
    """Convenience function for showing dialogs"""
    from claude_helpers.config import load_config
    
    config = load_config()
    manager = DialogManager(config.hil)
    
    if dialog_type == "text_input":
        return manager.show_text_input(title, message, kwargs.get("default_text", ""))
    elif dialog_type == "confirmation":
        return manager.show_confirmation(title, message, kwargs.get("buttons"))
    elif dialog_type == "choice":
        return manager.show_choice_selection(title, message, kwargs.get("choices", []))
    else:
        raise ValueError(f"Unknown dialog type: {dialog_type}")
```

### Configuration Integration
```python
# In HILConfig class
class HILConfig(BaseModel):
    dialog_tool: str = "auto"  # "auto", "applescript", "zenity", "yad", "dialog", "terminal"
    timeout: int = 300         # Dialog timeout in seconds
```

### Acceptance Criteria
- Unified interface работает на всех platforms
- Automatic tool selection логичен и consistent
- Configuration overrides respected
- Fallback chain работает properly
- All dialog types supported uniformly
- Error handling consistent

### Test Commands
```python
from claude_helpers.hil.dialog import show_dialog

# Test unified interface
result = show_dialog("text_input", "Test", "Enter text:", default_text="hello")
print(f"Text result: {result}")

result = show_dialog("confirmation", "Test", "Do you agree?")
print(f"Confirmation result: {result}")

result = show_dialog("choice", "Test", "Pick one:", choices=["A", "B", "C"])
print(f"Choice result: {result}")
```

---

## Epic 4 Completion Criteria

### Must Have
- [x] Dialog tool detection работает на обеих платформах
- [x] macOS AppleScript dialogs functional
- [x] Linux GUI dialogs working с multiple tools
- [x] Terminal fallback complete и user-friendly
- [x] Unified interface provides consistent API
- [x] Configuration integration working
- [x] Error handling robust для all tools

### Success Metrics
- Dialog response time: < 2 seconds to show
- Tool detection accuracy: 100% reliable
- Fallback chain success: > 95% working dialogs
- Cross-platform compatibility: Linux + macOS
- User experience consistency across tools

### Integration Points
- **Configuration System**: Uses HIL config для tool preferences
- **Voice System**: Independent - но может share error dialogs
- **HIL System**: Critical dependency - provides user interaction

### Handoff to Next Epics
После Epic 4, Dialog System готов для HIL integration:

1. **Standalone Testing**: All dialog methods работают independently
2. **Configuration Ready**: Tool selection respects user preferences  
3. **Error Handling**: Robust fallback chain established
4. **API Stable**: Unified interface ready для HIL system usage

**Parallel Development**: Epic 3 (Voice System) может развиваться параллельно с Epic 4.

**Next Steps**: Epic 5 (HIL System) может start после completion Epic 4 (Dialog System is critical dependency).