# Guidance

## For Users

### Querying Agents
- Use the dedicated Slack channel for each agent.
- Mention the bot: `@BotName your question here`.
- For Client Success Agent: Start with `client_id: question`.
- Keep queries clear and concise.
- Responses are in plain text.

### Best Practices
- Ask specific questions for better answers.
- If no answer, try rephrasing.
- Respect data isolation; don't ask cross-client questions.

## For Admins

### Configuration
- Ensure all folder IDs are correct and accessible.
- Test API keys before deployment.
- Set up monitoring alerts.

### Troubleshooting
- Check logs in terminal or file.
- Verify network connectivity for APIs.
- If ChromaDB issues, delete and re-ingest.

### Scaling
- For high load, use multiple instances with load balancer.
- Monitor API usage to avoid limits.
- Consider caching frequent queries.

## Development Guidance

- Follow PEP 8 for code style.
- Add type hints.
- Write unit tests for new functions.
- Document all functions and classes.

## Compliance
- Ensure GDPR/CCPA compliance for data handling.
- Audit logs for sensitive data access.
- No data retention beyond necessary.