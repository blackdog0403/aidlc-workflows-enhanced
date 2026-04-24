# Test Scenario: Serverless Order Management API

## User Request
"Build a serverless order management API for an e-commerce platform. It handles user authentication via Cognito, order CRUD operations, payment processing via Stripe integration, and order status notifications via email (SES) and push (SNS). Expected load: 1,000 orders/minute peak, 99.9% availability, sub-200ms p99 latency for read operations. Target: AWS, TypeScript, CDK for IaC."

## Project Context
- Greenfield project
- Team: 3 backend developers
- Timeline: 8 weeks
- Budget: moderate (serverless-first to minimize ops cost)
- No existing codebase
