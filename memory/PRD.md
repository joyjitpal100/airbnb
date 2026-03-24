# Xanadu Stays - Product Requirements Document

## Original Problem Statement
Property listing site for "Xanadu Stays" (premium serviced apartments in Kolkata). Features booking system, SEO optimization, lead capture, and a secure Guest ID Vault for compliance document management.

## Architecture

### Production (Netlify)
- **Static HTML** → Netlify CDN
- **Vault API** → Netlify Functions (Node.js)
- **Routing**: `netlify.toml` redirects `/api/vault/*` → `/.netlify/functions/vault`

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

### Phase 5: Guest ID Vault (Current)
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
- [x] Navigation link from homepage to vault
- [x] Single backend source of truth (Netlify Functions)
- [x] FastAPI vault code removed (proxy only)

## Environment Variables

| Variable | Where Set | Purpose |
|----------|-----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Netlify env / backend/.env | Supabase project URL (returned to frontend) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Netlify env / backend/.env | Public auth key (returned to frontend) |
| `SUPABASE_SERVICE_ROLE_KEY` | Netlify env / backend/.env | Server-side DB operations (NEVER exposed) |
| `R2_ACCOUNT_ID` | Netlify env / backend/.env | Cloudflare R2 endpoint (NEVER exposed) |
| `R2_ACCESS_KEY_ID` | Netlify env / backend/.env | R2 auth (NEVER exposed) |
| `R2_SECRET_ACCESS_KEY` | Netlify env / backend/.env | R2 auth (NEVER exposed) |
| `R2_BUCKET_NAME` | Netlify env / backend/.env | R2 bucket (default: guest-id-documents) |
| `MONGO_URL` | backend/.env | MongoDB connection (bookings) |
| `DB_NAME` | backend/.env | MongoDB database name |

## Key Files

| File | Purpose |
|------|---------|
| `netlify/functions/vault.js` | Canonical vault backend (all CRUD + auth + file ops) |
| `netlify/functions/shared.js` | Supabase + R2 client initialization, utilities |
| `netlify/functions/dev-server.js` | Local dev wrapper (NOT deployed) |
| `netlify.toml` | Netlify build + redirect config |
| `guest-id-vault.html` | Vault admin dashboard UI |
| `index.html` | Marketing homepage |
| `backend/server.py` | FastAPI (bookings + vault proxy) |
| `supabase-setup.sql` | Database schema for vault |

## API Endpoints

### Vault (Netlify Function)
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/vault/config` | GET | No | Returns public Supabase config |
| `/api/vault/status` | GET | No | Service configuration status |
| `/api/vault/guests` | GET | Yes | List records with search/filter |
| `/api/vault/guests` | POST | Yes | Create record + upload document |
| `/api/vault/guests/:id` | GET | Yes | Get single record |
| `/api/vault/guests/:id/document-url` | GET | Yes | Presigned download URL |
| `/api/vault/guests/:id/soft-delete` | PATCH | Yes | Mark as deleted |
| `/api/vault/guests/:id/permanent` | DELETE | Yes | Permanent delete (soft-deleted only) |
| `/api/vault/retention-review` | GET | Yes | Retention dashboard data |
| `/api/vault/properties` | GET | Yes | Unique property names |

### Bookings (FastAPI/MongoDB)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/bookings` | POST | Create booking |
| `/api/bookings` | GET | List bookings |
| `/api/bookings/:id` | GET | Get booking |
| `/api/bookings/:id` | DELETE | Delete booking |

## Deployment Steps (Netlify)

1. Push code to GitHub
2. Connect repo to Netlify
3. Set environment variables in Netlify Dashboard → Settings → Environment:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `R2_ACCOUNT_ID`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`
4. Run `supabase-setup.sql` in your Supabase project
5. Create R2 bucket named `guest-id-documents` in Cloudflare
6. Deploy - Netlify auto-publishes static HTML + bundles functions

## Backlog
- P1: Git workflow (branch, commit, PR)
- P2: Automated email responses (SendGrid)
- P2: Live availability calendar
- P2: Migrate booking endpoints to Netlify functions (unify architecture)
