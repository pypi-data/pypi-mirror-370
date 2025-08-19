# Epic 5: 💬 HIL System

**Priority**: CRITICAL - Main feature integration
**Estimated Time**: 6-7 days
**Dependencies**: Epic 1 (Foundation), Epic 2 (Configuration), Epic 4 (Dialog System)

## Overview

Реализация multi-agent Human-in-the-Loop system с file-based communication protocol. Это самый сложный epic который integrates все previous systems и provides core HIL functionality.

## Definition of Done

- [ ] Multi-agent file protocol fully functional
- [ ] Background listener поддерживает multiple Claude sessions
- [ ] Agent identification и registration working
- [ ] Question queue system с sequential processing
- [ ] File system monitoring robust и efficient
- [ ] Ask-human bash script generated correctly
- [ ] HIL integration работает end-to-end
- [ ] Performance optimized для multiple agents

---

## Task 5.1: File-Based Communication Protocol
**Time**: 1.5 days | **Complexity**: 🔴 High

### Описание
Создать robust file-based protocol для multi-agent communication

### Deliverables
- `src/claude_helpers/hil/protocol.py` - Core protocol implementation
- JSON-based message format
- File naming и organization strategy
- Atomic file operations для concurrency safety

### Protocol Design
```python
@dataclass
class HILMessage:
    id: str
    agent_id: str
    timestamp: datetime
    question: str
    timeout: int
    metadata: Dict[str, Any]
    
    def to_file(self, file_path: Path) -> None:
        """Save message to file atomically"""
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2, ensure_ascii=False, default=str)
        temp_path.rename(file_path)  # Atomic operation
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'HILMessage':
        """Load message from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

@dataclass  
class HILResponse:
    message_id: str
    agent_id: str
    timestamp: datetime
    answer: str
    cancelled: bool = False
    
    def to_file(self, file_path: Path) -> None:
        """Save response to file atomically"""
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2, ensure_ascii=False, default=str)
        temp_path.rename(file_path)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'HILResponse':
        """Load response from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

class HILProtocol:
    def __init__(self, project_dir: Path):
        """Initialize HIL protocol for project directory"""
        self.project_dir = project_dir
        self.helpers_dir = project_dir / ".helpers"
        self.ensure_directories()
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        for subdir in ["questions", "answers", "agents", "queue"]:
            (self.helpers_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def create_question(self, agent_id: str, question: str, 
                       timeout: int = 300) -> str:
        """Create new question and return message ID"""
        message_id = self._generate_message_id()
        message = HILMessage(
            id=message_id,
            agent_id=agent_id,
            timestamp=datetime.now(),
            question=question,
            timeout=timeout,
            metadata={}
        )
        
        # Save to questions directory
        question_file = self.helpers_dir / "questions" / f"{message_id}.json"
        message.to_file(question_file)
        
        # Add to queue
        self._add_to_queue(message_id)
        
        return message_id
    
    def wait_for_answer(self, message_id: str, timeout: int = 300) -> Optional[str]:
        """Wait for answer to specific question"""
        answer_file = self.helpers_dir / "answers" / f"{message_id}.json"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if answer_file.exists():
                try:
                    response = HILResponse.from_file(answer_file)
                    if response.cancelled:
                        return None
                    return response.answer
                except (json.JSONDecodeError, KeyError) as e:
                    # File might be incomplete, wait a bit more
                    time.sleep(0.1)
                    continue
            
            time.sleep(0.5)
        
        # Timeout - clean up
        self._cleanup_question(message_id)
        raise TimeoutError(f"No answer received within {timeout} seconds")
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    
    def _add_to_queue(self, message_id: str) -> None:
        """Add message to processing queue"""
        queue_file = self.helpers_dir / "queue" / f"{message_id}.queue"
        queue_file.touch()
    
    def _cleanup_question(self, message_id: str) -> None:
        """Clean up question files after timeout"""
        files_to_remove = [
            self.helpers_dir / "questions" / f"{message_id}.json",
            self.helpers_dir / "queue" / f"{message_id}.queue"
        ]
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
```

### File Organization Strategy
```
.helpers/
├── questions/           # Pending questions from agents
│   ├── 1642678901234_abc12345.json
│   └── 1642678901567_def67890.json
├── answers/            # Completed answers
│   ├── 1642678901234_abc12345.json  
│   └── 1642678901567_def67890.json
├── agents/             # Agent registration info
│   ├── claude_12345.json
│   └── claude_67890.json
└── queue/              # Processing queue markers
    ├── 1642678901234_abc12345.queue
    └── 1642678901567_def67890.queue
```

### Concurrency Safety
- **Atomic writes**: Use temp files + rename
- **File locking**: Not needed due to atomic operations
- **Queue ordering**: Timestamp-based processing
- **Cleanup**: Timeout-based cleanup to prevent file accumulation

### Acceptance Criteria
- Messages saved/loaded без corruption
- Concurrent access safe (multiple agents)
- File operations atomic и reliable
- Queue ordering maintained properly
- Cleanup prevents file accumulation
- Unicode content handled correctly

### Test Commands
```python
from claude_helpers.hil.protocol import HILProtocol
from pathlib import Path
import tempfile

# Test in temporary directory
with tempfile.TemporaryDirectory() as tmp_dir:
    protocol = HILProtocol(Path(tmp_dir))
    
    # Create question
    msg_id = protocol.create_question("test_agent", "What is 2+2?", 10)
    assert len(msg_id) > 0
    
    # Check files created
    question_file = Path(tmp_dir) / ".helpers" / "questions" / f"{msg_id}.json"
    assert question_file.exists()
    
    # Test cleanup
    import time
    time.sleep(11)  # Wait for timeout
    # Should cleanup automatically
```

---

## Task 5.2: Agent Identification System
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать систему для identification и registration Claude Code agents

### Deliverables
- Agent ID generation based on process info
- Agent registration и heartbeat system
- Agent cleanup для disconnected sessions
- Multi-session management

### Agent Identification Implementation
```python
@dataclass
class AgentInfo:
    id: str
    pid: int
    ppid: int
    command_line: str
    working_directory: str
    start_time: datetime
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    
    def to_file(self, file_path: Path) -> None:
        """Save agent info to file"""
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2, ensure_ascii=False, default=str)
        temp_path.rename(file_path)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'AgentInfo':
        """Load agent info from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

class AgentManager:
    def __init__(self, project_dir: Path):
        """Initialize agent management for project"""
        self.project_dir = project_dir
        self.helpers_dir = project_dir / ".helpers"
        self.agents_dir = self.helpers_dir / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_agent_id(self) -> str:
        """Generate unique agent ID based on process info"""
        import psutil
        
        current_process = psutil.Process()
        parent_process = current_process.parent()
        
        # Create agent ID from process hierarchy
        agent_id = f"claude_{current_process.pid}_{parent_process.pid}"
        
        # Add uniqueness if multiple processes with same PIDs
        counter = 0
        original_id = agent_id
        agent_file = self.agents_dir / f"{agent_id}.json"
        
        while agent_file.exists():
            counter += 1
            agent_id = f"{original_id}_{counter}"
            agent_file = self.agents_dir / f"{agent_id}.json"
        
        return agent_id
    
    def register_agent(self, agent_id: str = None) -> str:
        """Register current process as agent"""
        if not agent_id:
            agent_id = self.generate_agent_id()
        
        import psutil
        current_process = psutil.Process()
        
        agent_info = AgentInfo(
            id=agent_id,
            pid=current_process.pid,
            ppid=current_process.ppid(),
            command_line=" ".join(current_process.cmdline()),
            working_directory=str(self.project_dir),
            start_time=datetime.fromtimestamp(current_process.create_time()),
            last_heartbeat=datetime.now(),
            metadata={}
        )
        
        agent_file = self.agents_dir / f"{agent_id}.json"
        agent_info.to_file(agent_file)
        
        return agent_id
    
    def update_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat timestamp"""
        agent_file = self.agents_dir / f"{agent_id}.json"
        if not agent_file.exists():
            # Re-register if file missing
            self.register_agent(agent_id)
            return
        
        agent_info = AgentInfo.from_file(agent_file)
        agent_info.last_heartbeat = datetime.now()
        agent_info.to_file(agent_file)
    
    def cleanup_stale_agents(self, max_age_minutes: int = 30) -> List[str]:
        """Clean up agents that haven't sent heartbeat recently"""
        stale_agents = []
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                agent_info = AgentInfo.from_file(agent_file)
                
                # Check if process still exists
                import psutil
                try:
                    process = psutil.Process(agent_info.pid)
                    if process.create_time() != agent_info.start_time.timestamp():
                        # PID reused by different process
                        raise psutil.NoSuchProcess(agent_info.pid)
                except psutil.NoSuchProcess:
                    # Process no longer exists
                    agent_file.unlink()
                    stale_agents.append(agent_info.id)
                    continue
                
                # Check heartbeat age
                if agent_info.last_heartbeat < cutoff_time:
                    agent_file.unlink()
                    stale_agents.append(agent_info.id)
            
            except Exception as e:
                # Corrupted file, remove it
                agent_file.unlink()
                stale_agents.append(agent_file.stem)
        
        return stale_agents
    
    def list_active_agents(self) -> List[AgentInfo]:
        """List all currently active agents"""
        # First cleanup stale agents
        self.cleanup_stale_agents()
        
        active_agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                agent_info = AgentInfo.from_file(agent_file)
                active_agents.append(agent_info)
            except Exception:
                # Skip corrupted files
                continue
        
        return sorted(active_agents, key=lambda a: a.start_time)
```

### Agent Registration Flow
1. **Agent Startup**: Generate unique ID based on process info
2. **Registration**: Create agent info file
3. **Heartbeat**: Update timestamp periodically
4. **Cleanup**: Remove stale agents based on heartbeat age
5. **Process Check**: Verify process still exists via PID

### Acceptance Criteria
- Agent IDs уникальны для concurrent sessions
- Process identification robust
- Stale agent cleanup prevents file accumulation
- Registration handles edge cases (PID reuse, etc.)
- Multi-session support works properly

### Test Commands
```python
from claude_helpers.hil.agent import AgentManager
from pathlib import Path
import tempfile
import time

with tempfile.TemporaryDirectory() as tmp_dir:
    manager = AgentManager(Path(tmp_dir))
    
    # Register agent
    agent_id = manager.register_agent()
    assert agent_id.startswith("claude_")
    
    # Update heartbeat
    manager.update_heartbeat(agent_id)
    
    # List active agents
    agents = manager.list_active_agents()
    assert len(agents) == 1
    assert agents[0].id == agent_id
```

---

## Task 5.3: Background Listener Implementation
**Time**: 2 days | **Complexity**: 🔴 High

### Описание
Реализовать background listener который monitors file system и processes questions

### Deliverables
- `src/claude_helpers/hil/listener.py` - Main listener implementation
- File system monitoring с watchdog
- Question queue processing
- Thread-safe question handling
- Graceful shutdown mechanisms

### Background Listener Implementation
```python
class HILListener:
    def __init__(self, project_dirs: List[Path], config: HILConfig):
        """Initialize HIL listener for multiple project directories"""
        self.project_dirs = project_dirs
        self.config = config
        self.protocols = {dir: HILProtocol(dir) for dir in project_dirs}
        self.dialog_manager = DialogManager(config)
        
        # Threading
        self.running = False
        self.question_queue = queue.Queue()
        self.worker_thread = None
        self.file_observers = []
        
        # Processing state
        self.active_questions = {}  # message_id -> processing state
        self.processing_lock = threading.Lock()
    
    def start(self) -> None:
        """Start the background listener"""
        if self.running:
            return
        
        self.running = True
        
        # Start file system watchers
        for project_dir in self.project_dirs:
            self._start_file_watcher(project_dir)
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self._process_questions,
            daemon=True,
            name="HIL-QuestionProcessor"
        )
        self.worker_thread.start()
        
        console.print("[green]HIL Listener started[/green]")
    
    def stop(self) -> None:
        """Stop the background listener gracefully"""
        if not self.running:
            return
        
        console.print("[yellow]Stopping HIL Listener...[/yellow]")
        self.running = False
        
        # Stop file watchers
        for observer in self.file_observers:
            observer.stop()
            observer.join(timeout=5)
        
        # Stop worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=10)
        
        console.print("[red]HIL Listener stopped[/red]")
    
    def _start_file_watcher(self, project_dir: Path) -> None:
        """Start file system watcher for project directory"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class QuestionHandler(FileSystemEventHandler):
            def __init__(self, listener):
                self.listener = listener
                self.project_dir = project_dir
            
            def on_created(self, event):
                if event.is_directory:
                    return
                
                file_path = Path(event.src_path)
                
                # Check if it's a question file
                if (file_path.parent.name == "questions" and 
                    file_path.suffix == ".json"):
                    # Add small delay for file to be completely written
                    threading.Timer(0.1, self._handle_new_question, 
                                  args=[file_path]).start()
            
            def _handle_new_question(self, question_file: Path) -> None:
                try:
                    if question_file.exists():
                        message = HILMessage.from_file(question_file)
                        self.listener.question_queue.put((self.project_dir, message))
                except Exception as e:
                    console.print(f"[red]Error reading question file: {e}[/red]")
        
        # Set up file watcher
        handler = QuestionHandler(self)
        observer = Observer()
        watch_path = project_dir / ".helpers" / "questions"
        watch_path.mkdir(parents=True, exist_ok=True)
        
        observer.schedule(handler, str(watch_path), recursive=False)
        observer.start()
        self.file_observers.append(observer)
    
    def _process_questions(self) -> None:
        """Main question processing loop"""
        console.print("[blue]Question processor started[/blue]")
        
        while self.running:
            try:
                # Get question from queue (with timeout for clean shutdown)
                project_dir, message = self.question_queue.get(timeout=1.0)
                
                # Check if already processing this question
                with self.processing_lock:
                    if message.id in self.active_questions:
                        continue
                    self.active_questions[message.id] = "processing"
                
                # Process the question
                self._handle_question(project_dir, message)
                
            except queue.Empty:
                continue
            except Exception as e:
                console.print(f"[red]Error in question processor: {e}[/red]")
    
    def _handle_question(self, project_dir: Path, message: HILMessage) -> None:
        """Handle individual question"""
        try:
            console.print(f"[blue]Processing question from {message.agent_id}[/blue]")
            
            # Show dialog to user
            answer = self.dialog_manager.show_text_input(
                title=f"Question from Claude Agent ({message.agent_id})",
                message=message.question,
                default_text=""
            )
            
            # Create response
            response = HILResponse(
                message_id=message.id,
                agent_id=message.agent_id,
                timestamp=datetime.now(),
                answer=answer or "",
                cancelled=(answer is None)
            )
            
            # Save response
            protocol = self.protocols[project_dir]
            answer_file = protocol.helpers_dir / "answers" / f"{message.id}.json"
            response.to_file(answer_file)
            
            # Clean up queue marker
            queue_file = protocol.helpers_dir / "queue" / f"{message.id}.queue"
            if queue_file.exists():
                queue_file.unlink()
            
            # Remove from active questions
            with self.processing_lock:
                self.active_questions.pop(message.id, None)
            
            if answer:
                console.print(f"[green]Question answered: {answer[:50]}...[/green]")
            else:
                console.print("[yellow]Question cancelled by user[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error handling question: {e}[/red]")
            
            # Create error response
            error_response = HILResponse(
                message_id=message.id,
                agent_id=message.agent_id,
                timestamp=datetime.now(),
                answer=f"Error: {str(e)}",
                cancelled=True
            )
            
            protocol = self.protocols[project_dir]
            answer_file = protocol.helpers_dir / "answers" / f"{message.id}.json"
            error_response.to_file(answer_file)
            
            with self.processing_lock:
                self.active_questions.pop(message.id, None)

def listen_command(project_dir: Path = None) -> None:
    """Main listen command entry point"""
    from claude_helpers.config import load_config
    
    config = load_config()
    
    # Determine project directories to watch
    if project_dir:
        project_dirs = [project_dir]
    else:
        # Watch current directory if it has .helpers
        current_dir = Path.cwd()
        if (current_dir / ".helpers").exists():
            project_dirs = [current_dir]
        else:
            console.print("[red]No .helpers directory found. Run 'claude-helpers init' first.[/red]")
            return
    
    # Start listener
    listener = HILListener(project_dirs, config.hil)
    
    try:
        listener.start()
        
        # Keep running until interrupted
        console.print("[blue]HIL Listener running. Press Ctrl+C to stop.[/blue]")
        while listener.running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutdown requested by user[/yellow]")
    finally:
        listener.stop()
```

### File System Monitoring
- **Watchdog**: Monitor `.helpers/questions/` for new files
- **Debouncing**: Small delay to ensure file is completely written
- **Multi-project**: Support watching multiple project directories
- **Thread Safety**: Queue-based processing for thread safety

### Question Processing Flow
1. **File Created**: New question file detected
2. **Queue Addition**: Add to processing queue
3. **Dialog Display**: Show question to user via dialog system
4. **Response Capture**: Save user response
5. **Cleanup**: Remove queue marker, update active questions

### Acceptance Criteria
- File system monitoring reliable и responsive
- Multiple projects supported simultaneously
- Thread-safe question processing
- Graceful shutdown без losing questions
- Error handling не crash listener
- Dialog system integration working

### Test Commands
```bash
# Manual integration test
# Terminal 1: Start listener
claude-helpers listen

# Terminal 2: Create test question
mkdir -p .helpers/questions
echo '{"id":"test123","agent_id":"test","timestamp":"2024-01-01T00:00:00","question":"Test question?","timeout":300,"metadata":{}}' > .helpers/questions/test123.json

# Should show dialog in listener terminal
```

---

## Task 5.4: Ask-Human Bash Script Generation
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать template generation для ask-human.sh script с agent support

### Deliverables
- Enhanced bash script template с agent identification
- Script generation в init command
- Cross-platform bash compatibility
- Error handling и timeout management

### Enhanced Ask-Human Script Template
```bash
#!/bin/bash

# Claude Helpers - Ask Human Script (Multi-Agent Support)
# Generated by claude-helpers init command

set -euo pipefail

HELPERS_DIR="$(cd "$(dirname "$0")/../.helpers" && pwd)"
TIMEOUT=${CLAUDE_HELPERS_TIMEOUT:-300}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

# Generate agent ID
generate_agent_id() {
    local pid=$$
    local ppid=$(ps -o ppid= -p $pid | tr -d ' ')
    local base_id="claude_${pid}_${ppid}"
    
    # Check if ID already exists, add counter if needed
    local counter=0
    local agent_id="$base_id"
    
    while [ -f "$HELPERS_DIR/agents/${agent_id}.json" ]; do
        counter=$((counter + 1))
        agent_id="${base_id}_${counter}"
    done
    
    echo "$agent_id"
}

# Create message ID
generate_message_id() {
    local timestamp=$(date +%s%3N)  # milliseconds
    local random_suffix
    
    # Generate random suffix (portable across systems)
    if command -v openssl >/dev/null 2>&1; then
        random_suffix=$(openssl rand -hex 4)
    elif command -v xxd >/dev/null 2>&1; then
        random_suffix=$(head -c 4 /dev/urandom | xxd -p)
    else
        # Fallback using date and process info
        random_suffix=$(printf "%x" $(($(date +%s) % 65536)))
    fi
    
    echo "${timestamp}_${random_suffix}"
}

# Register agent
register_agent() {
    local agent_id="$1"
    local agent_file="$HELPERS_DIR/agents/${agent_id}.json"
    
    # Get process info
    local pid=$$
    local ppid=$(ps -o ppid= -p $pid | tr -d ' ')
    local start_time=$(date -Iseconds)
    local cmd_line="$0 $*"
    local working_dir="$PROJECT_DIR"
    
    # Create agent registration (use portable JSON generation)
    cat > "$agent_file" << EOF
{
    "id": "$agent_id",
    "pid": $pid,
    "ppid": $ppid,
    "command_line": "$cmd_line",
    "working_directory": "$working_dir",
    "start_time": "$start_time",
    "last_heartbeat": "$start_time",
    "metadata": {}
}
EOF
    
    log "Agent registered: $agent_id (PID: $pid)"
}

# Create question file
create_question() {
    local message_id="$1"
    local agent_id="$2"  
    local question="$3"
    local question_file="$HELPERS_DIR/questions/${message_id}.json"
    local queue_file="$HELPERS_DIR/queue/${message_id}.queue"
    local timestamp=$(date -Iseconds)
    
    # Escape question text for JSON (basic escaping)
    local escaped_question=$(echo "$question" | sed 's/"/\\"/g' | sed 's/\\/\\\\/g')
    
    # Create question file (atomic write)
    local temp_file="${question_file}.tmp"
    cat > "$temp_file" << EOF
{
    "id": "$message_id",
    "agent_id": "$agent_id",
    "timestamp": "$timestamp",
    "question": "$escaped_question",
    "timeout": $TIMEOUT,
    "metadata": {}
}
EOF
    
    mv "$temp_file" "$question_file"
    
    # Create queue marker
    touch "$queue_file"
    
    log "Question created: $message_id"
}

# Wait for answer
wait_for_answer() {
    local message_id="$1"
    local answer_file="$HELPERS_DIR/answers/${message_id}.json"
    local start_time=$(date +%s)
    
    log "Waiting for answer (timeout: ${TIMEOUT}s)..."
    
    while [ $(($(date +%s) - start_time)) -lt $TIMEOUT ]; do
        if [ -f "$answer_file" ]; then
            # Parse JSON response (portable parsing)
            if command -v jq >/dev/null 2>&1; then
                # Use jq if available
                local answer=$(jq -r '.answer' "$answer_file" 2>/dev/null)
                local cancelled=$(jq -r '.cancelled' "$answer_file" 2>/dev/null)
                
                if [ "$cancelled" = "true" ]; then
                    log "Question was cancelled by user"
                    cleanup_files "$message_id"
                    return 1
                fi
                
                echo "$answer"
                cleanup_files "$message_id"
                return 0
            else
                # Basic JSON parsing fallback
                local answer_line=$(grep '"answer"' "$answer_file" | head -n1)
                local cancelled_line=$(grep '"cancelled"' "$answer_file" | head -n1)
                
                if echo "$cancelled_line" | grep -q "true"; then
                    log "Question was cancelled by user"
                    cleanup_files "$message_id"
                    return 1
                fi
                
                # Extract answer (basic parsing)
                local answer=$(echo "$answer_line" | sed 's/.*"answer": *"//' | sed 's/".*//')
                echo "$answer"
                cleanup_files "$message_id"
                return 0
            fi
        fi
        
        sleep 0.5
    done
    
    log "Timeout waiting for answer"
    cleanup_files "$message_id"
    return 2
}

# Cleanup files
cleanup_files() {
    local message_id="$1"
    
    rm -f "$HELPERS_DIR/questions/${message_id}.json"
    rm -f "$HELPERS_DIR/queue/${message_id}.queue"
}

# Ensure required directories exist
ensure_directories() {
    mkdir -p "$HELPERS_DIR"/{questions,answers,agents,queue}
}

# Main function
main() {
    # Check arguments
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <question>" >&2
        echo "Ask a question to the human operator" >&2
        exit 1
    fi
    
    local question="$*"
    
    # Ensure directories exist
    ensure_directories
    
    # Generate IDs
    local agent_id
    agent_id=$(generate_agent_id)
    local message_id
    message_id=$(generate_message_id)
    
    # Register agent
    register_agent "$agent_id"
    
    # Create and send question
    create_question "$message_id" "$agent_id" "$question"
    
    # Wait for answer
    if wait_for_answer "$message_id"; then
        exit 0
    else
        exit $?
    fi
}

# Run main function
main "$@"
```

### Cross-Platform Compatibility Features
- **Portable JSON**: Basic JSON generation без dependencies
- **Random Generation**: Multiple fallbacks для random IDs
- **Date Handling**: ISO format compatible across platforms
- **Process Info**: Portable process информация extraction
- **File Operations**: Atomic file operations

### Error Handling
- **Timeout Management**: Configurable timeouts
- **File Cleanup**: Proper cleanup on timeout/error
- **Process Registration**: Robust agent identification
- **JSON Safety**: Basic JSON escaping

### Template Integration
```python
def get_ask_human_script_template() -> str:
    """Get the ask-human.sh script template"""
    # Return the full bash script above as string
    return BASH_SCRIPT_TEMPLATE

def generate_ask_script(project_dir: Path) -> None:
    """Generate and install ask-human.sh script"""
    script_content = get_ask_human_script_template()
    
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    script_file = scripts_dir / "ask-human.sh"
    script_file.write_text(script_content, encoding='utf-8')
    
    # Make executable on Unix systems
    if platform.system() != 'Windows':
        script_file.chmod(0o755)
    
    console.print(f"[green]Generated ask-human.sh script: {script_file}[/green]")
```

### Acceptance Criteria
- Script runs на обеих platforms (Linux/macOS)
- Agent identification unique и robust
- Question/answer cycle works end-to-end
- Timeout handling functional
- File cleanup prevents accumulation
- JSON parsing works с и без jq
- Error handling comprehensive

### Test Commands
```bash
# Test script generation
claude-helpers init
ls -la scripts/ask-human.sh

# Test script execution (requires listener running)
./scripts/ask-human.sh "What is the project structure?"

# Test timeout behavior
CLAUDE_HELPERS_TIMEOUT=5 ./scripts/ask-human.sh "Quick question?"
```

---

## Task 5.5: Integration Testing & Performance
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
End-to-end testing HIL system и performance optimization

### Deliverables
- Integration tests для full HIL workflow
- Performance benchmarks
- Multi-agent stress testing
- Memory usage optimization
- Error scenario testing

### Integration Test Suite
```python
class TestHILIntegration:
    def test_full_hil_workflow(self, tmp_path):
        """Test complete HIL workflow end-to-end"""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        # Setup project
        protocol = HILProtocol(project_dir)
        agent_manager = AgentManager(project_dir)
        
        # Register agent
        agent_id = agent_manager.register_agent()
        
        # Create question
        question_id = protocol.create_question(agent_id, "Test question?")
        
        # Simulate listener processing (mock dialog)
        with patch('claude_helpers.hil.dialog.show_dialog') as mock_dialog:
            mock_dialog.return_value = "Test answer"
            
            # Process question
            # ... test logic
        
        # Verify answer received
        answer = protocol.wait_for_answer(question_id, timeout=5)
        assert answer == "Test answer"
    
    def test_multi_agent_scenario(self, tmp_path):
        """Test multiple agents asking questions simultaneously"""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        # Create multiple agents
        agents = []
        protocols = []
        
        for i in range(3):
            protocol = HILProtocol(project_dir)
            agent_manager = AgentManager(project_dir)
            agent_id = agent_manager.register_agent()
            
            agents.append(agent_id)
            protocols.append(protocol)
        
        # Create questions from all agents
        question_ids = []
        for i, (agent_id, protocol) in enumerate(zip(agents, protocols)):
            qid = protocol.create_question(agent_id, f"Question from agent {i}?")
            question_ids.append(qid)
        
        # Simulate concurrent processing
        # ... test concurrent handling
    
    def test_error_scenarios(self, tmp_path):
        """Test various error conditions"""
        project_dir = tmp_path / "test-project"
        
        # Test corrupted files
        # Test permission issues  
        # Test timeout scenarios
        # Test cleanup after errors
        pass
    
    def test_performance_benchmarks(self, tmp_path):
        """Performance benchmarks for HIL system"""
        project_dir = tmp_path / "test-project"
        
        # Benchmark question creation
        start_time = time.time()
        for i in range(100):
            protocol = HILProtocol(project_dir)
            agent_manager = AgentManager(project_dir)
            agent_id = agent_manager.register_agent()
            protocol.create_question(agent_id, f"Question {i}")
        
        creation_time = time.time() - start_time
        assert creation_time < 5.0  # Should create 100 questions in < 5s
        
        # Benchmark file system monitoring
        # Benchmark concurrent processing
        pass
```

### Performance Optimization
```python
class OptimizedHILListener(HILListener):
    """Optimized version of HIL listener"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Performance optimizations
        self._file_cache = {}  # Cache for frequently accessed files
        self._batch_size = 10  # Process questions in batches
        self._debounce_time = 0.1  # Debounce file events
    
    def _batch_process_questions(self):
        """Process questions in batches for better performance"""
        questions_batch = []
        
        try:
            # Collect batch of questions
            while len(questions_batch) < self._batch_size:
                project_dir, message = self.question_queue.get(timeout=0.1)
                questions_batch.append((project_dir, message))
        except queue.Empty:
            pass
        
        # Process batch
        if questions_batch:
            self._process_question_batch(questions_batch)
```

### Memory Usage Monitoring
```python
def monitor_memory_usage():
    """Monitor memory usage during HIL operations"""
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Run HIL operations
    # ... operations
    
    # Force garbage collection
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable
    assert memory_increase < 50 * 1024 * 1024  # < 50MB increase
```

### Acceptance Criteria
- Full HIL workflow test passes
- Multi-agent scenarios работают correctly
- Performance benchmarks meet targets
- Memory usage stays within bounds
- Error scenarios handled gracefully
- Stress tests complete successfully

### Test Commands
```bash
# Run integration tests
uv run pytest tests/integration/test_hil_integration.py -v

# Run performance tests
uv run pytest tests/integration/test_hil_performance.py -v

# Run stress tests
uv run pytest tests/integration/test_hil_stress.py -v
```

---

## Epic 5 Completion Criteria

### Must Have
- [x] Multi-agent file protocol fully functional
- [x] Background listener supports multiple Claude sessions
- [x] Agent identification и registration robust
- [x] Question queue sequential processing working
- [x] Ask-human bash script generated correctly
- [x] Dialog system integration seamless
- [x] Performance optimized для production use
- [x] Error handling comprehensive

### Success Metrics
- Question processing latency: < 500ms from file creation to dialog
- Multi-agent support: > 10 concurrent agents
- Memory usage: < 100MB for background listener
- File system monitoring: < 50ms response time
- Error recovery rate: > 95% successful question handling
- Stress test: Handle 1000 questions without failure

### Integration Points
- **Configuration System**: Uses HIL config settings
- **Dialog System**: Critical dependency - provides user interaction
- **Voice System**: Independent - can be used together
- **Foundation**: Uses all core infrastructure

### Handoff to Final Epic
После Epic 5, HIL System is fully functional:

1. **End-to-End Working**: Complete HIL workflow operational
2. **Multi-Agent Ready**: Supports multiple Claude Code sessions
3. **Performance Optimized**: Ready for production use
4. **Robust Error Handling**: Handles all error scenarios gracefully

**Next Steps**: Epic 6 (Final Integration) для testing, packaging, и release preparation.

**Critical Achievement**: Core functionality complete - users можно start using voice и HIL features!