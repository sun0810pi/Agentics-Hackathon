# Backend – Control Plane (FastAPI)

This backend acts as the **control plane** of the Fintech Invoice Reconciliation System.

It is responsible for:
- Receiving client requests (Web / Desktop)
- Managing job lifecycle
- Orchestrating asynchronous execution via AWS SQS
- Providing job status & results

❗ This backend **does NOT execute heavy business logic or agents**.

---

## Responsibilities

### What this backend DOES
- Accept Excel uploads
- Validate request metadata
- Upload files to S3
- Create job records
- Push messages to SQS
- Expose job status APIs

### What this backend DOES NOT do
- Process Excel files
- Run Agent 1–5 logic
- Perform invoice matching or fraud detection
- Send Slack / Telegram notifications
