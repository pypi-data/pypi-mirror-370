# Release QA: Pre-Alpha

## Acceptance Criteria
- [ ] Messages from Slack are ingested and stored
- [ ] Search returns relevant results within 2 seconds
- [ ] System handles 100 messages/minute without loss
- [ ] Database migrations run without data corruption

## E2E Scenarios
1. User sends message in Slack → appears in search within 10 seconds
2. Search for keyword → returns messages containing that word
3. System restart → no message loss, search still works

## Integration Points
- Message Connector ↔ Message Queue: messages delivered in order
- Search API → Vector Store: similarity search returns top-10 results
- Processor → PostgreSQL: all fields correctly mapped to schema

## Rollback Plan
Revert deployments in reverse order (API → Processor → Storage)
Keep previous DB backup for 48 hours
Disable webhook endpoints if ingestion fails

## Sign-off
- [ ] All epics validated
- [ ] No critical bugs
- [ ] Deploy ready