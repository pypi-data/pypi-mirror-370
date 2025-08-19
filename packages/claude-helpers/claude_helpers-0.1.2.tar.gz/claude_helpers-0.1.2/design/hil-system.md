# Claude Helpers - Human-in-the-Loop (HIL) System Design

## Overview

Multi-agent file-based communication system allowing multiple Claude Code windows to ask questions and receive human answers without breaking execution flow.

## Architecture

### Two-Component System

#### 1. Background Listener (`claude-helpers listen`)
- Single process handles multiple Claude agents
- Watches for question files in `.helpers/questions/`
- Processes questions sequentially via GUI dialogs
- Maintains agent registry and queue status

#### 2. Agent-Side Script (`scripts/ask-human.sh`)
- Auto-generated bash script per project
- Automatically identifies agent by PID/process
- Creates question files and waits for answers
- Returns answer to stdout for Claude

## File Protocol

### Directory Structure
```
.helpers/
├── questions/
│   └── q_<agent_id>_<timestamp>_<uuid>.json   # Questions from agents
├── answers/
│   └── a_<agent_id>_<timestamp>_<uuid>.json   # Answers to agents
├── agents/
│   ├── agent_<pid>.json                       # Agent registry
│   └── active_sessions.json                   # Active agent tracking
├── queue/
│   └── question_queue.json                     # Question queue for UI
└── .listener.pid                               # Listener process PID
```

### Message Formats

#### Question Format
```json
{
  "id": "uuid-here",
  "agent_id": "agent_12345",
  "agent_name": "Claude-Terminal-1", 
  "working_dir": "/home/user/project",
  "timestamp": 1738339200,
  "type": "text|yesno|select",
  "content": "Question text here",
  "options": ["option1", "option2"],  // For select type
  "priority": "normal|high|urgent",
  "answered": false,
  "timeout": 300
}
```

#### Answer Format
```json
{
  "id": "question-uuid",
  "agent_id": "agent_12345",
  "timestamp": 1738339250,
  "type": "answer",
  "content": "Answer text here"
}
```

#### Agent Registration
```json
{
  "agent_id": "agent_12345",
  "pid": 12345,
  "name": "Claude-Terminal-1",
  "working_dir": "/home/user/project",
  "started_at": 1738339200,
  "last_seen": 1738339250,
  "questions_asked": 3,
  "status": "active|waiting|idle"
}
```

## Multi-Agent Listener Implementation

```python
# src/claude_helpers/hil/listener.py
import time
import json
import os
import threading
from pathlib import Path
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .dialog import show_dialog
from ..config import check_config

class MultiAgentQuestionHandler(FileSystemEventHandler):
    def __init__(self, helpers_dir: Path):
        self.helpers_dir = helpers_dir
        self.questions_dir = helpers_dir / "questions"
        self.answers_dir = helpers_dir / "answers"
        self.agents_dir = helpers_dir / "agents"
        self.queue_dir = helpers_dir / "queue"
        
        # Thread-safe question queue
        self.question_queue = deque()
        self.queue_lock = threading.Lock()
        self.active_agents = {}
        
        # Ensure directories exist
        for dir_path in [self.questions_dir, self.answers_dir, self.agents_dir, self.queue_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Start question processor thread
        self.processor_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processor_thread.start()
        
    def on_created(self, event):
        """Handle new question files"""
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        if path.parent == self.questions_dir and path.name.startswith('q_'):
            self.handle_question(path)
    
    def handle_question(self, question_file: Path):
        """Process new question from agent"""
        time.sleep(0.1)  # Ensure file is fully written
        
        try:
            with open(question_file, 'r') as f:
                question = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"ERROR: Could not read question file: {question_file}")
            return
        
        # Update agent registry
        self._update_agent_registry(question)
        
        # Add to queue
        with self.queue_lock:
            self.question_queue.append((question_file, question))
            self._update_queue_file()
        
        agent_name = question.get('agent_name', question.get('agent_id', 'Unknown'))
        print(f"[Agent {agent_name}] Question queued: {question['content'][:50]}...")
    
    def _process_queue(self):
        """Process questions sequentially"""
        while True:
            question_item = None
            
            with self.queue_lock:
                if self.question_queue:
                    question_item = self.question_queue.popleft()
                    self._update_queue_file()
            
            if question_item:
                question_file, question = question_item
                self._handle_single_question(question_file, question)
            else:
                time.sleep(0.5)  # Wait for new questions
    
    def _handle_single_question(self, question_file: Path, question: dict):
        """Handle individual question with dialog"""
        agent_name = question.get('agent_name', question.get('agent_id', 'Unknown'))
        
        # Show question context
        print(f"\n{'='*60}")
        print(f"[{agent_name}] Question:")
        print(f"  {question['content']}")
        
        if question.get('options'):
            print(f"  Options: {', '.join(question['options'])}")
        
        print(f"{'='*60}")
        
        # Show dialog to user
        answer = show_dialog(
            message=f"[{agent_name}]\n\n{question['content']}",
            dialog_type=question.get('type', 'text'),
            options=question.get('options', [])
        )
        
        # Write answer file
        agent_id = question.get('agent_id', 'unknown')
        answer_file = self.answers_dir / f"a_{agent_id}_{question['id']}.json"
        
        answer_data = {
            'id': question['id'],
            'agent_id': agent_id,
            'timestamp': time.time(),
            'type': 'answer',
            'content': answer
        }
        
        with open(answer_file, 'w') as f:
            json.dump(answer_data, f, indent=2)
        
        print(f"[{agent_name}] Answer: {answer}")
        print()
        
        # Update agent status
        if agent_id in self.active_agents:
            self.active_agents[agent_id]['status'] = 'active'
            self._save_agent_info(agent_id)
    
    def _update_agent_registry(self, question):
        """Update agent registry with question info"""
        agent_id = question.get('agent_id')
        if not agent_id:
            return
        
        agent_file = self.agents_dir / f"agent_{agent_id}.json"
        agent_info = {
            'agent_id': agent_id,
            'name': question.get('agent_name', f'Agent-{agent_id}'),
            'working_dir': question.get('working_dir', str(Path.cwd())),
            'last_seen': time.time(),
            'status': 'waiting'
        }
        
        # Load existing info if available
        if agent_file.exists():
            try:
                with open(agent_file, 'r') as f:
                    existing = json.load(f)
                agent_info.update({
                    'started_at': existing.get('started_at', agent_info['last_seen']),
                    'questions_asked': existing.get('questions_asked', 0) + 1
                })
            except:
                pass
        else:
            agent_info.update({
                'started_at': agent_info['last_seen'],
                'questions_asked': 1
            })
        
        # Save agent info
        with open(agent_file, 'w') as f:
            json.dump(agent_info, f, indent=2)
        
        self.active_agents[agent_id] = agent_info
    
    def _update_queue_file(self):
        """Update queue status file"""
        queue_info = {
            'total_questions': len(self.question_queue),
            'active_agents': len(self.active_agents),
            'queue': [
                {
                    'agent_name': q['agent_name'],
                    'content': q['content'][:100] + '...' if len(q['content']) > 100 else q['content'],
                    'timestamp': q['timestamp'],
                    'type': q.get('type', 'text')
                }
                for _, q in list(self.question_queue)
            ]
        }
        
        queue_file = self.queue_dir / "question_queue.json"
        with open(queue_file, 'w') as f:
            json.dump(queue_info, f, indent=2)

def listen_command(project_dir: Path = None):
    """Start multi-agent HIL listener"""
    # Check global config
    if not check_config():
        print("ERROR: Global configuration not found.")
        print("Please run: claude-helpers init")
        return
    
    if project_dir is None:
        project_dir = Path.cwd()
    
    helpers_dir = project_dir / ".helpers"
    
    # Check project initialization
    if not helpers_dir.exists():
        print("ERROR: Project not initialized for HIL.")
        print("Please run: claude-helpers init (in project directory)")
        return
    
    # Create PID file
    pid_file = helpers_dir / ".listener.pid"
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    print(f"✓ Multi-Agent HIL Listener started")
    print(f"  Project: {project_dir}")
    print(f"  Supporting multiple Claude Code sessions")
    print(f"  Watching: {helpers_dir / 'questions'}")
    print("\nPress Ctrl+C to stop\n")
    
    # Start file watcher
    event_handler = MultiAgentQuestionHandler(helpers_dir)
    observer = Observer()
    observer.schedule(event_handler, str(helpers_dir / "questions"), recursive=False)
    observer.start()
    
    try:
        while True:
            # Show status if questions pending
            if event_handler.question_queue:
                print(f"[Status] {len(event_handler.question_queue)} questions in queue, "
                      f"{len(event_handler.active_agents)} active agents")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down...")
        observer.stop()
        # Cleanup
        pid_file.unlink(missing_ok=True)
        for agent_file in event_handler.agents_dir.glob("agent_*.json"):
            agent_file.unlink(missing_ok=True)
    
    observer.join()
    print("✓ Multi-Agent HIL Listener stopped")
```

## Agent-Side Bash Script

```bash
#!/bin/bash
# Multi-agent human-in-the-loop question script
# Auto-generated by claude-helpers

QUESTION="$1"
TYPE="${2:-text}"  # text, yesno, select
OPTIONS="${3:-}"   # comma-separated options for select

HELPERS_DIR=".helpers"
QUESTIONS_DIR="$HELPERS_DIR/questions"
ANSWERS_DIR="$HELPERS_DIR/answers"

# Check if listener is running
if [ ! -f "$HELPERS_DIR/.listener.pid" ]; then
    echo "ERROR: HIL listener not running. Start it with: claude-helpers listen" >&2
    exit 1
fi

# Generate agent identification
AGENT_PID=$$
PARENT_PID=$PPID
TERMINAL_ID=$(ps -p $PARENT_PID -o comm= 2>/dev/null || echo "unknown")
WORKING_DIR=$(pwd)

# Create readable agent name
if [ "$TERMINAL_ID" = "claude" ] || [[ "$TERMINAL_ID" == *"claude"* ]]; then
    AGENT_NAME="Claude-${AGENT_PID}"
else
    AGENT_NAME="Agent-${TERMINAL_ID}-${AGENT_PID}"
fi

AGENT_ID="agent_${AGENT_PID}"

# Generate unique question ID
TIMESTAMP=$(date +%s%N 2>/dev/null || date +%s)
UUID="${TIMESTAMP}_${AGENT_PID}_$$"
QUESTION_ID="$UUID"

# Create question file with agent info
QUESTION_FILE="$QUESTIONS_DIR/q_${AGENT_ID}_${TIMESTAMP}_${UUID}.json"

# Build JSON with agent information
if [ "$TYPE" = "select" ] && [ -n "$OPTIONS" ]; then
    IFS=',' read -ra OPTS <<< "$OPTIONS"
    OPTIONS_JSON=$(printf '"%s",' "${OPTS[@]}" | sed 's/,$//')
    cat > "$QUESTION_FILE" << EOF
{
  "id": "$QUESTION_ID",
  "agent_id": "$AGENT_ID",
  "agent_name": "$AGENT_NAME",
  "working_dir": "$WORKING_DIR",
  "timestamp": $TIMESTAMP,
  "type": "$TYPE",
  "content": "$QUESTION",
  "options": [$OPTIONS_JSON],
  "priority": "normal",
  "answered": false,
  "timeout": 300
}
EOF
else
    cat > "$QUESTION_FILE" << EOF
{
  "id": "$QUESTION_ID",
  "agent_id": "$AGENT_ID",
  "agent_name": "$AGENT_NAME",
  "working_dir": "$WORKING_DIR",
  "timestamp": $TIMESTAMP,
  "type": "$TYPE",
  "content": "$QUESTION",
  "priority": "normal",
  "answered": false,
  "timeout": 300
}
EOF
fi

echo "[HIL:$AGENT_NAME] Question sent, waiting for response..." >&2

# Wait for answer file
ANSWER_FILE="$ANSWERS_DIR/a_${AGENT_ID}_${QUESTION_ID}.json"
TIMEOUT=300
ELAPSED=0

while [ ! -f "$ANSWER_FILE" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 0.5
    ELAPSED=$((ELAPSED + 1))
    
    # Show progress every 60 seconds
    if [ $((ELAPSED % 120)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        echo "[HIL:$AGENT_NAME] Still waiting... (${ELAPSED}s elapsed)" >&2
    fi
done

if [ ! -f "$ANSWER_FILE" ]; then
    echo "ERROR: Timeout waiting for response (${TIMEOUT}s)" >&2
    rm -f "$QUESTION_FILE" 2>/dev/null
    exit 1
fi

# Read answer (cross-platform JSON parsing)
if command -v jq >/dev/null 2>&1; then
    ANSWER=$(jq -r '.content' "$ANSWER_FILE" 2>/dev/null)
elif command -v python3 >/dev/null 2>&1; then
    ANSWER=$(python3 -c "
import json
try:
    with open('$ANSWER_FILE') as f:
        print(json.load(f).get('content', ''))
except:
    print('')
" 2>/dev/null)
else
    # Fallback grep method
    ANSWER=$(grep '"content"' "$ANSWER_FILE" 2>/dev/null | sed 's/.*"content".*:.*"\([^"]*\)".*/\1/')
fi

# Cleanup files
rm -f "$QUESTION_FILE" "$ANSWER_FILE" 2>/dev/null

# Output answer for Claude
echo "$ANSWER"
```

## Dialog System

See `design/dialog-system.md` for cross-platform GUI dialog implementation details.

## Usage Examples

### Basic Text Question
```bash
!./scripts/ask-human.sh "Should I use PostgreSQL or MySQL?"
# Returns: "PostgreSQL"
```

### Yes/No Question
```bash
!./scripts/ask-human.sh "Should I update all test files?" "yesno"
# Returns: "yes" or "no"
```

### Multiple Choice
```bash
!./scripts/ask-human.sh "Which framework?" "select" "Express,Fastify,Koa"
# Returns: "Express" (selected option)
```

### Multi-Agent Scenario
```bash
# Terminal 1: HIL Listener
claude-helpers listen

# Terminal 2: Claude Code session 1 (Agent-12345)
!./scripts/ask-human.sh "Use TypeScript?"

# Terminal 3: Claude Code session 2 (Agent-67890) 
!./scripts/ask-human.sh "Use Bootstrap?"

# Listener processes sequentially:
# [Agent-12345] Question: Use TypeScript?
# [User answers via dialog]
# [Agent-12345] Answer: yes
# 
# [Agent-67890] Question: Use Bootstrap?
# [User answers via dialog]
# [Agent-67890] Answer: no
```

## Error Handling

- **No listener running**: Check PID file, show clear start command
- **Project not initialized**: Prompt to run init in project directory
- **File permissions**: Auto-fix .helpers directory permissions
- **Timeout**: Configurable timeout with clear message and cleanup
- **JSON parsing errors**: Multiple fallback methods for cross-platform compatibility
- **Agent identification**: Graceful fallback for unknown processes

## Testing Strategy

### Unit Tests
- File protocol message format validation
- Agent identification logic
- JSON parsing fallbacks
- Queue management with threading

### Integration Tests  
- Multi-agent question handling
- File system event processing
- Dialog integration
- Cleanup and error recovery

### Manual Testing
- Multiple concurrent Claude Code sessions
- Network filesystem scenarios
- Permission edge cases
- Cross-platform bash script compatibility