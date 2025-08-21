# Task QA: Webhook Receiver

## Test Cases

### Case 1: Valid Slack Message Event
**Input:** POST /webhooks/slack with {"type": "event_callback", "event": {"type": "message", "text": "hello"}}
**Expected:** Returns 200, message appears in queue

### Case 2: URL Verification Challenge
**Input:** POST with {"type": "url_verification", "challenge": "test123"}
**Expected:** Returns 200 with body "test123"

### Case 3: Invalid Signature
**Input:** POST with wrong X-Slack-Signature header
**Expected:** Returns 403 Forbidden

### Case 4: Timeout Handling
**Input:** Valid event but queue is slow
**Expected:** Returns 200 within 3 seconds, message processing continues async

## Validation
- [ ] Function returns correct HTTP status codes
- [ ] Error handling for malformed JSON
- [ ] No side effects on verification requests
- [ ] Messages queued in correct format

## Test Data
Use Slack event samples from: docs/test-data/slack-events.json
Mock queue with in-memory implementation for unit tests