#!/bin/bash

# Claude Helpers - Human-in-the-loop script (Global Version)
# This script is installed globally with claude-helpers and provides
# voice and text interaction capabilities for Claude Code agents
#
# Usage:
#   claude-helpers ask "question"                    # Text question
#   claude-helpers ask --voice "prompt"              # Voice input
#   claude-helpers ask --voice --duration 60 "prompt" # Voice with max duration

set -euo pipefail

# Configuration - Use current project directory
HELPERS_DIR="${PWD}/.helpers"
QUESTIONS_DIR="${HELPERS_DIR}/questions"
ANSWERS_DIR="${HELPERS_DIR}/answers"
AGENTS_DIR="${HELPERS_DIR}/agents"
QUEUE_DIR="${HELPERS_DIR}/queue"

# Default values
QUESTION_TYPE="text"
MAX_DURATION=30
TIMEOUT=300  # 5 minutes default

# Generate unique agent ID based on process hierarchy
AGENT_ID="agent_$$_$(date +%s%N | cut -b1-13)"

# Create necessary directories
mkdir -p "$QUESTIONS_DIR" "$ANSWERS_DIR" "$AGENTS_DIR" "$QUEUE_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Function to parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --voice)
                QUESTION_TYPE="voice"
                shift
                ;;
            --duration)
                MAX_DURATION="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            -*)
                echo "Unknown option: $1" >&2
                show_usage
                exit 1
                ;;
            *)
                # Remaining arguments form the question/prompt
                QUESTION="$*"
                break
                ;;
        esac
    done
    
    if [ -z "${QUESTION:-}" ]; then
        echo "Error: No question/prompt provided" >&2
        show_usage
        exit 1
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: claude-helpers ask [OPTIONS] <question>

Options:
    --voice         Request voice input instead of text
    --duration N    Max recording duration in seconds (default: 30)
    --timeout N     Max wait time for response in seconds (default: 300)
    --help          Show this help message

Examples:
    claude-helpers ask "What approach should I use?"
    claude-helpers ask --voice "Describe the bug you found"
    claude-helpers ask --voice --duration 60 "Explain the architecture"

Claude Code Integration:
    !claude-helpers ask "question"
    !claude-helpers ask --voice "voice prompt"
EOF
}

# Function to check environment
check_environment() {
    # Check if HIL directory structure exists
    if [ ! -d "$HELPERS_DIR" ]; then
        echo "Error: Project not initialized for HIL. Run 'claude-helpers init --project-only'" >&2
        exit 1
    fi
    
    # Check if listener might be running (basic check)
    if [ ! -w "$QUESTIONS_DIR" ] || [ ! -w "$ANSWERS_DIR" ]; then
        echo "Warning: HIL directories not writable. Is listener running?" >&2
    fi
}

# Function to create question file (JSON format for voice support)
create_question() {
    local question="$1"
    local question_file="${QUESTIONS_DIR}/${AGENT_ID}.json"
    local queue_file="${QUEUE_DIR}/${AGENT_ID}.queue"
    
    # Escape JSON special characters in question
    local escaped_question=$(echo "$question" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n')
    
    # Create JSON question file
    cat > "$question_file" << EOF
{
    "type": "${QUESTION_TYPE}",
    "agent_id": "${AGENT_ID}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "prompt": "${escaped_question}",
    "timeout": ${TIMEOUT},
    "metadata": {
        "max_duration": ${MAX_DURATION},
        "language": "en",
        "require_confirmation": true,
        "fallback_to_text": true
    }
}
EOF
    
    # Add to queue
    echo "$(date +%s):${AGENT_ID}" >> "$queue_file"
    
    # Register agent
    echo "$(date '+%Y-%m-%d %H:%M:%S'):${AGENT_ID}:waiting" > "${AGENTS_DIR}/${AGENT_ID}.status"
    
    log_message "Question created: $question_file (type: ${QUESTION_TYPE})"
    echo "$question_file"
}

# Function to wait for answer
wait_for_answer() {
    local agent_id="$1"
    local timeout="${2:-300}"  # 5 minutes default
    local answer_file="${ANSWERS_DIR}/${agent_id}.json"
    local start_time=$(date +%s)
    
    log_message "Waiting for answer (timeout: ${timeout}s)..."
    
    while [ ! -f "$answer_file" ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log_message "Timeout waiting for answer"
            echo "TIMEOUT: No response received within ${timeout} seconds"
            cleanup_agent "$agent_id"
            exit 1
        fi
        
        sleep 1
    done
    
    # Read answer from JSON
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import json, sys; data=json.load(open('$answer_file')); print(data.get('answer', ''))"
    elif command -v jq >/dev/null 2>&1; then
        jq -r '.answer // ""' "$answer_file"
    else
        # Fallback: simple text extraction (fragile but works for basic cases)
        grep '"answer":' "$answer_file" | sed 's/.*"answer":\s*"\(.*\)".*/\1/' | head -1
    fi
    
    # Cleanup
    cleanup_agent "$agent_id"
}

# Function to cleanup agent files
cleanup_agent() {
    local agent_id="$1"
    
    # Clean both .txt and .json files for backward compatibility
    rm -f "${QUESTIONS_DIR}/${agent_id}.txt" "${QUESTIONS_DIR}/${agent_id}.json"
    rm -f "${ANSWERS_DIR}/${agent_id}.txt" "${ANSWERS_DIR}/${agent_id}.json"
    rm -f "${AGENTS_DIR}/${agent_id}.status"
    rm -f "${QUEUE_DIR}/${agent_id}.queue"
    
    log_message "Cleaned up agent files: $agent_id"
}

# Main execution
main() {
    # Check environment first
    check_environment
    
    # Parse command line arguments
    parse_args "$@"
    
    # Create question and wait for answer
    local question_file=$(create_question "$QUESTION")
    local answer=$(wait_for_answer "$AGENT_ID" "$TIMEOUT")
    
    # Output answer to stdout (becomes next Claude prompt)
    echo "$answer"
}

# Handle interruption
trap 'cleanup_agent "$AGENT_ID"; exit 130' INT TERM

# Execute main function
main "$@"