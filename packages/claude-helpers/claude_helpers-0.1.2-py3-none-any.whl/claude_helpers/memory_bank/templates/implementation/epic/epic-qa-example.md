# Epic QA: Message Ingestion Pipeline

## Integration Tests
- [ ] Webhook receives POST → Parser extracts fields correctly
- [ ] Parser output → Deduplication checks hash in cache
- [ ] Deduplicated message → Writer saves to PostgreSQL
- [ ] Failed message → Goes to DLQ, not lost

## Validation Checklist
- [ ] All tasks completed and tested
- [ ] Components interact as designed
- [ ] No regression in existing features
- [ ] Error handling covers network failures

## Test Scenarios
1. Send new Slack message → stored with correct channel_id, user_id, text
2. Send duplicate message → rejected with "already processed" response
3. Send malformed JSON → returns 400, logged to errors table
4. Database unavailable → message queued for retry

## Dependencies Check
- [ ] PostgreSQL accepting connections
- [ ] Message queue (Redis/RabbitMQ) running
- [ ] Slack webhook URL configured