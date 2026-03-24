# Xanadu Stays - Product Requirements Document

## Original Problem Statement
Property listing site for "Xanadu Stays" (premium serviced apartments in Kolkata). Features booking system, SEO optimization, lead capture, and a secure Guest ID Vault for compliance document management.

## Architecture

### Production (Netlify)
- **Static HTML** → Netlify CDN
- **Vault API** → Netlify Function (directory-based: `netlify/functions/vault/`)
- **Routing**: `netlify.toml` redirects `/api/vault/*` → `/.netlify/functions/vault/:splat`
- **Build command**: `cd netlify/functions/vault && npm install`

### Development (Emergent Preview)
- **Frontend**: React dev server on port 3000 (serves static HTML from `/app/frontend/public/`)
- **Backend**: FastAPI on port 8001 (handles bookings, proxies vault to Node.js)
- **Vault Dev Server**: Node.js on port 8002 (wraps Netlify function code)

### Data Storage
- **Bookings**: MongoDB (legacy)
- **Guest ID Vault metadata**: Supabase/PostgreSQL
- **Guest ID Vault files**: Cloudflare R2 (private bucket)

## Features Implemented

### Phase 1-4 (Previous)
- [x] Booking system with calendar, guest selector, dynamic pricing
- [x] Aadhaar upload with 7-year retention (MongoDB)
- [x] Traveller/Host view toggle
- [x] Homepage redesign with trust signals
- [x] SEO optimization (JSON-LD, sitemap, meta tags)
- [x] Lead capture popups, multi-channel CTAs
- [x] Individual property pages (Xanadu 310, 313, 922)

### Phase 5: Guest ID Vault
- [x] Guest record CRUD (name, phone, booking source, property, dates, notes)
- [x] Document upload to Cloudflare R2 (PDF, JPG, PNG, max 5MB)
- [x] Presigned URL generation for secure document downloads
- [x] Search by name or phone
- [x] Filter by property, booking source, status
- [x] 7-year retention calculation
- [x] Soft delete and permanent delete
- [x] Retention Review dashboard
- [x] Supabase Authentication (JWT-based)
- [x] Dynamic config loading (no hardcoded keys in frontend)
- [x] Homepage navigation link to vault
- [x] Single backend source of truth (Netlify Functions)
- [x] Directory-based function structure (vault/ subdirectory)
- [x] .netlifyignore to exclude dev files from deploy
- [x] Uses supabase.from() (not .table())
- [x] No localhost references in production code

## Environment Variables

| Variable | Where Set | Purpose |
|----------|-----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Netlify env / backend/.env | Supabase project URL (returned to frontend via /config) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Netlify env / backend/.env | Public auth key (returned to frontend via /config) |
| `SUPABASE_SERVICE_ROLE_KEY` | Netlify env / backend/.env | Server-side DB operations (NEVER exposed) |
| `R2_ACCOUNT_ID` | Netlify env / backend/.env | Cloudflare R2 endpoint (NEVER exposed) |
| `R2_ACCESS_KEY_ID` | Netlify env / backend/.env | R2 auth (NEVER exposed) |
| `R2_SECRET_ACCESS_KEY` | Netlify env / backend/.env | R2 auth (NEVER exposed) |
| `R2_BUCKET_NAME` | Netlify env / backend/.env | R2 bucket (default: guest-id-documents) |
| `MONGO_URL` | backend/.env | MongoDB connection (bookings, dev only) |
| `DB_NAME` | backend/.env | MongoDB database name (dev only) |

## Backlog
- P1: Git workflow (branch, commit, PR)
- P2: Automated email responses (SendGrid)
- P2: Live availability calendar
- P2: Migrate booking endpoints to Netlify functions (unify architecture)
