# Epic 2: ⚙️ Configuration System

**Priority**: CRITICAL - Core dependency for all features
**Estimated Time**: 4-5 days
**Dependencies**: Epic 1 (Foundation)

## Overview

Реализация двухуровневой системы конфигурации (global + project), init команды, и template generation. Это основа для всех feature systems.

## Definition of Done

- [ ] Global configuration loading/saving работает
- [ ] Project initialization создает все необходимые файлы
- [ ] Platform-specific config directories используются правильно
- [ ] Init command поддерживает global-only и project-only режимы
- [ ] Template generation для bash scripts и CLAUDE.md работает
- [ ] Configuration validation и error handling реализованы
- [ ] Cross-platform compatibility проверена

---

## Task 2.1: Configuration Data Models
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать Pydantic models для конфигурации с validation

### Deliverables
- `src/claude_helpers/config.py` с data models
- Type-safe configuration loading
- Validation rules и error messages

### Core Models
```python
class AudioConfig(BaseModel):
    device_id: Optional[int] = None
    sample_rate: int = 44100
    channels: int = 1

class HILConfig(BaseModel):
    dialog_tool: str = "auto"
    timeout: int = 300

class GlobalConfig(BaseModel):
    openai_api_key: str
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hil: HILConfig = Field(default_factory=HILConfig)
    version: str = "0.1.0"
    
    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v
```

### Acceptance Criteria
- Models создаются с правильными defaults
- Validation rules работают правильно
- Error messages понятные и helpful
- Type hints полные и правильные
- JSON serialization/deserialization работает

### Test Commands
```python
from claude_helpers.config import GlobalConfig, AudioConfig
config = GlobalConfig(openai_api_key="sk-test123")
assert config.audio.sample_rate == 44100
# Test validation
try:
    GlobalConfig(openai_api_key="invalid-key")
    assert False, "Should have raised validation error"
except ValueError:
    pass
```

---

## Task 2.2: Configuration File Management
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Реализовать loading/saving configuration files с platform detection

### Deliverables
- Configuration file path resolution (platform-specific)
- Safe file operations с proper error handling
- Backup/restore functionality для corrupt configs

### Core Functions
```python
def get_config_file() -> Path:
    """Get platform-appropriate config file path"""

def check_config() -> bool:
    """Check if valid global config exists"""

def load_config() -> GlobalConfig:
    """Load and validate global configuration"""

def save_config(config: GlobalConfig) -> None:
    """Save configuration with secure permissions"""

def backup_config() -> Optional[Path]:
    """Create backup of current config"""
```

### Platform-Specific Paths
- **Linux**: `~/.config/claude-helpers/config.json`
- **macOS**: `~/Library/Application Support/claude-helpers/config.json`

### Acceptance Criteria
- Config files созданы с 600 permissions (user only)
- Platform-specific directories используются правильно
- Corrupt config files обрабатываются gracefully
- Backup functionality работает
- Concurrent access безопасный

### Test Commands
```python
from claude_helpers.config import get_config_file, save_config, load_config
from claude_helpers.config import GlobalConfig

# Test save/load cycle
config = GlobalConfig(openai_api_key="sk-test123")
save_config(config)
loaded = load_config()
assert loaded.openai_api_key == "sk-test123"

# Test permissions
config_file = get_config_file()
import stat
assert oct(config_file.stat().st_mode)[-3:] == '600'
```

---

## Task 2.3: Environment Variable Support
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Добавить support для environment variable overrides

### Deliverables
- Environment variable loading
- Priority system (env vars > config file > defaults)
- Documentation для supported env vars

### Supported Environment Variables
- `OPENAI_API_KEY` - Override API key
- `CLAUDE_HELPERS_CONFIG_DIR` - Override config directory
- `CLAUDE_HELPERS_DEBUG` - Enable debug mode

### Implementation
```python
def load_config_with_env_override() -> GlobalConfig:
    """Load configuration with environment variable override"""
    config = load_config()
    
    # Override API key from environment if available
    env_api_key = os.getenv('OPENAI_API_KEY')
    if env_api_key:
        config.openai_api_key = env_api_key
    
    return config
```

### Acceptance Criteria
- Environment variables корректно override config values
- Priority system работает правильно
- Debug mode функциональный
- Custom config directory поддерживается

### Test Commands
```bash
export OPENAI_API_KEY="sk-env-test"
python -c "from claude_helpers.config import load_config_with_env_override; print(load_config_with_env_override().openai_api_key)"
# Should print: sk-env-test
```

---

## Task 2.4: Init Command - Global Setup
**Time**: 1.5 days | **Complexity**: 🔴 High

### Описание
Реализовать глобальную настройку в init команде

### Deliverables
- Interactive global configuration setup
- API key validation
- Audio device selection
- Update existing configuration option

### Implementation Features
- API key input с validation
- Audio device enumeration и selection
- Confirmation prompts для overwrites
- Rich CLI interface с good UX

### Core Functions
```python
@click.command()
@click.option('--global-only', is_flag=True, help='Only configure global settings')
def init(global_only):
    """Initialize global config and optionally set up current project"""

def setup_global_config():
    """Interactive global configuration setup"""

def setup_audio_config(config_data: dict):
    """Interactive audio device configuration"""

def validate_api_key(key: str) -> bool:
    """Validate API key format and optionally test with OpenAI"""
```

### UX Requirements
- Clear progress indicators
- Helpful error messages
- Ability to skip optional steps
- Confirmation before overwriting existing config
- Colored output для better visibility

### Acceptance Criteria
- Interactive prompts работают correctly
- API key validation functional
- Audio device selection works on both platforms
- Existing configuration updates safely
- Error states handled gracefully

### Test Commands
```bash
# Test new configuration
claude-helpers init --global-only
# Should prompt for API key and audio device

# Test updating existing config
claude-helpers init --global-only
# Should detect existing config and offer to update

# Test with environment variable
export OPENAI_API_KEY="sk-test123"
claude-helpers init --global-only
# Should use env var as default
```

---

## Task 2.5: Project Template System
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать систему templates для project files

### Deliverables
- Template functions для bash scripts и CLAUDE.md
- Variable substitution system
- Template validation

### Templates to Create
1. **ask-human.sh script** - Multi-agent HIL bash script
2. **CLAUDE.md instructions** - HIL usage instructions
3. **Project .gitignore entries** - .helpers exclusions

### Template Functions
```python
def get_ask_human_script_template() -> str:
    """Generate ask-human.sh bash script content"""

def get_claude_md_template() -> str:
    """Generate CLAUDE.md HIL instructions"""

def get_gitignore_entries() -> str:
    """Get gitignore entries for Claude Helpers"""

def render_template(template: str, variables: Dict[str, Any]) -> str:
    """Render template with variable substitution"""
```

### Variable Substitution Support
- Project-specific paths
- Platform-specific commands
- Customizable timeouts и settings

### Acceptance Criteria
- Templates генерируются без errors
- Variable substitution работает correctly  
- Generated files are syntactically valid
- Templates updated легко в будущем

### Test Commands
```python
from claude_helpers.config import get_ask_human_script_template
script = get_ask_human_script_template()
assert "#!/bin/bash" in script
assert "HELPERS_DIR" in script

# Test that generated script is valid bash
import tempfile
import subprocess
with tempfile.NamedTemporaryFile(mode='w', suffix='.sh') as f:
    f.write(script)
    f.flush()
    result = subprocess.run(['bash', '-n', f.name])
    assert result.returncode == 0  # Valid bash syntax
```

---

## Task 2.6: Init Command - Project Setup
**Time**: 1 day | **Complexity**: 🔴 High

### Описание
Реализовать project-level setup в init команде

### Deliverables
- `.helpers/` directory structure creation
- Script generation и installation
- CLAUDE.md creation/updating
- .gitignore modification

### Project Setup Features
- Create complete `.helpers/` directory structure
- Generate и install executable `scripts/ask-human.sh`
- Create или update `CLAUDE.md` with HIL instructions
- Add `.helpers/` to `.gitignore` automatically
- Detect existing project setup

### Directory Structure Created
```
.helpers/
├── questions/
├── answers/
├── agents/
└── queue/

scripts/
└── ask-human.sh  (executable)

CLAUDE.md         (created or updated)
.gitignore        (updated)
```

### Implementation
```python
def setup_project():
    """Set up current project for Claude Helpers"""

def setup_gitignore(project_dir: Path):
    """Add .helpers to .gitignore"""

def setup_ask_script(project_dir: Path):
    """Create executable ask-human.sh script"""

def setup_claude_md(project_dir: Path):
    """Create or update CLAUDE.md with HIL instructions"""
```

### Acceptance Criteria
- All directories созданы с proper permissions
- Scripts are executable и syntactically valid
- CLAUDE.md содержит correct HIL instructions
- .gitignore updated без duplication
- Existing files не corrupted

### Test Commands
```bash
# Test in empty directory
mkdir test-project && cd test-project
claude-helpers init
ls -la .helpers/
test -x scripts/ask-human.sh
grep "HUMAN-IN-THE-LOOP" CLAUDE.md
grep ".helpers" .gitignore

# Test in existing project with CLAUDE.md
echo "Existing content" > CLAUDE.md
claude-helpers init
grep "Existing content" CLAUDE.md  # Should still be there
grep "HUMAN-IN-THE-LOOP" CLAUDE.md  # Should be added
```

---

## Task 2.7: Configuration Error Handling
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Comprehensive error handling для всех configuration operations

### Deliverables
- Custom exception classes
- User-friendly error messages
- Recovery mechanisms
- Debug logging

### Error Categories
1. **File System Errors** - Permissions, disk space, etc.
2. **Validation Errors** - Invalid configuration values
3. **Platform Errors** - Unsupported platform, missing dependencies
4. **Network Errors** - API key validation failures

### Custom Exceptions
```python
class ConfigError(Exception):
    """Base configuration error"""

class ConfigNotFoundError(ConfigError):
    """Configuration file not found"""

class ConfigValidationError(ConfigError):
    """Configuration validation failed"""

class PlatformNotSupportedError(ConfigError):
    """Platform not supported"""
```

### Error Messages должны включать:
- Clear explanation of the problem
- Specific steps to resolve
- Relevant command examples
- Links to documentation if needed

### Acceptance Criteria
- All error scenarios имеют appropriate exceptions
- Error messages are user-friendly и actionable
- Recovery mechanisms work where possible
- Debug information available when needed

### Test Commands
```python
# Test various error conditions
from claude_helpers.config import load_config, ConfigNotFoundError
import os

# Remove config file and test error
config_file = get_config_file()
if config_file.exists():
    os.remove(config_file)

try:
    load_config()
    assert False, "Should have raised ConfigNotFoundError"
except ConfigNotFoundError as e:
    assert "claude-helpers init" in str(e)
```

---

## Epic 2 Completion Criteria

### Must Have
- [x] Global configuration system fully functional
- [x] Project setup creates all required files
- [x] Cross-platform compatibility verified
- [x] Template system working для all file types
- [x] Error handling comprehensive и user-friendly
- [x] Environment variable support working
- [x] Init command handles all scenarios correctly

### Success Metrics
- Init command completes in < 30 seconds
- Configuration loading/saving < 100ms
- Zero file corruption incidents
- 100% error scenarios handled gracefully
- Platform detection accuracy: 100%

### Integration Points
- **Voice System**: Будет использовать audio configuration
- **Dialog System**: Будет использовать HIL configuration
- **HIL System**: Будет использовать project setup files

### Handoff to Next Epics
После Epic 2, параллельная разработка Voice и Dialog systems возможна:

1. **Voice System** depends on: audio config, global config loading
2. **Dialog System** depends on: HIL config, platform detection
3. Both systems can develop независимо и test separately

**Next Steps**: Epic 3 (Voice) и Epic 4 (Dialog) могут начать development параллельно.