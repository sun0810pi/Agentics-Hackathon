# Fintech Invoice Reconciliation System

## Architecture Overview
This system separates control plane and execution plane.

- FastAPI: orchestration & access
- SQS: async job queue
- AWS Lambda: agent workers (Agent 1–5)

## Flow
Client → FastAPI → SQS → Lambda Agents → Notification

## Why this architecture?
- Non-blocking request handling
- Event-driven processing
- Horizontally scalable workers

## Tech Stack
- FastAPI
- AWS Lambda
- SQS
- S3
- Slack / Telegram Bot

## Demo
1. Upload Excel
2. Job queued
3. Agent pipeline executed
4. Result notified
