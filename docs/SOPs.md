# Standard Operating Procedures (SOPs)

## 1. System Startup

1. Verify all environment variables are set in `.env`.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Execute data ingestion: `python src/ingest.py`.
4. Start the server: `uvicorn src.main:app --host 0.0.0.0 --port 8000`.
5. Confirm Slack app is installed and channels are set.

## 2. Data Ingestion

- **Frequency**: Daily at 2 AM via cron or scheduler.
- **Process**:
  1. Run `src/ingest.py`.
  2. Check logs for success/failures.
  3. If failures, retry after fixing issues (e.g., API limits).
- **Manual Uploads**:
  1. Use POST to `/admin/upload/{agent}`.
  2. Provide admin password.
  3. For client success, include client_id.

## 3. Monitoring

- Monitor server logs for errors.
- Check ChromaDB for data integrity.
- Slack responses should be within 5 seconds.
- Alert if API calls fail repeatedly.

## 4. Security Procedures

- Store secrets in environment variables only.
- Rotate API keys quarterly.
- No write access to external services.
- Validate all inputs and outputs.

## 5. Backup and Recovery

- Backup `.env` securely.
- Backup ChromaDB directory weekly.
- In case of failure, restore from backup and re-ingest data.

## 6. Incident Response

- If data leak suspected, immediately revoke API keys.
- Notify users of downtime.
- Log incidents and review for improvements.

## 7. Updates and Maintenance

- Update packages: `pip install --upgrade -r requirements.txt`.
- Test updates in staging environment.
- Schedule downtime for major updates.