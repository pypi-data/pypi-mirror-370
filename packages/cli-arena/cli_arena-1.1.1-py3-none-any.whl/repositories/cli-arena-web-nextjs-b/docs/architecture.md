# Architecture Overview

## Purpose
A unique barcode web app for generating, storing, and analyzing barcodes (EAN, QR, Code128, etc.) with a Next.js frontend and Postgres backend.

## Components
- **Frontend:** Next.js (TypeScript)
- **Backend API:** Next.js API routes
- **Database:** PostgreSQL (db/init.sql)
- **CI/CD:** GitHub Actions
- **Containerization:** Docker, docker-compose

## Unique Features
- Multi-format barcode generation
- Barcode analytics dashboard
- REST API for barcode CRUD
- User authentication

## Data Model
See `db/init.sql` for schema.
