# Task: Webhook Receiver

## Component
→ `/architecture/releases/01-pre-alpha/components/message-connector.md#http-interface`

## What to Do
Create HTTP endpoint that receives POST webhooks from Slack Events API and returns 200 OK with challenge verification

## Implementation
**Location:** src/connectors/slack/webhook.py
**Type:** new

### Changes
- Add POST /webhooks/slack endpoint
- Implement challenge-response for Slack verification
- Parse event payload and push to message queue
- Return 200 immediately (async processing)

## Input/Output
**Input:** Slack Event JSON (type: message, channel: C123, text: "hello")
**Output:** Message queued to "ingest.messages" topic

## Notes
Must respond within 3 seconds or Slack will retry
Store raw payload for debugging