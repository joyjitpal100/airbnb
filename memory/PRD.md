# Xanadu Stays - Property Listing Site PRD

## Original Problem Statement
Complete property listing site with booking system, SEO optimization, lead capture, and now **Guest ID Vault** for compliance.

## Latest Feature: Guest ID Vault

### Purpose
Store and track guest identity documents with 7-year retention for compliance.

### Files Created/Modified
| File | Action | Description |
|------|--------|-------------|
| `/app/guest-id-vault.html` | Created | Admin dashboard for Guest ID Vault |
| `/app/backend/server.py` | Modified | Added Supabase endpoints for vault CRUD |
| `/app/backend/.env` | Modified | Added Supabase config variables |
| `/app/backend/requirements.txt` | Modified | Added supabase, python-dateutil |
| `/app/supabase-setup.sql` | Created | Database schema for Supabase |

### Features Implemented
- [x] Add guest records (name, phone, booking source, property, dates, notes)
- [x] Upload ID documents (Aadhaar, Passport, DL) to Supabase Storage
- [x] Search by name or phone
- [x] Filter by property, booking source, status
- [x] 7-year retention calculation (from check_out_date or uploaded_at)
- [x] View guest details with document download
- [x] Soft delete (mark as deleted)
- [x] Permanent delete (only for soft-deleted records)
- [x] Retention Review dashboard (expiring, eligible, deleted)
- [x] File validation (PDF, JPG, PNG, max 5MB)
- [x] Mobile-responsive UI

### Storage Configuration

**File Storage: Cloudflare R2**
- Files uploaded via backend API to R2 bucket
- Presigned URLs generated for secure downloads
- Credentials never exposed to frontend

**Metadata Storage: Supabase**
- Guest records stored in `guest_documents` table
- File path references stored, not actual files

### Environment Variables
```bash
# Supabase (metadata)
SUPABASE_URL=https://smceyhikbpawrdkmqemf.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Cloudflare R2 (file storage)
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=guest-id-documents
R2_PUBLIC_URL=https://your-bucket.r2.dev  # optional
```

### R2 Setup Steps
1. Go to Cloudflare Dashboard → R2
2. Create bucket named `guest-id-documents`
3. Create API token with read/write permissions
4. Copy Account ID, Access Key ID, Secret Access Key
5. Add to `/app/backend/.env`
6. Restart backend: `sudo supervisorctl restart backend`

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/status` | GET | Check if Supabase configured |
| `/api/vault/guests` | POST | Create guest record |
| `/api/vault/guests` | GET | List with search/filter |
| `/api/vault/guests/{id}` | GET | Get single record |
| `/api/vault/guests/{id}/document-url` | GET | Signed URL for document |
| `/api/vault/guests/{id}/soft-delete` | PATCH | Mark as deleted |
| `/api/vault/guests/{id}/permanent` | DELETE | Permanent delete |
| `/api/vault/retention-review` | GET | Retention dashboard data |
| `/api/vault/properties` | GET | Unique properties for filter |

### Auth Note
Currently no authentication. The code is ready for protection:
- Add auth middleware to `/api/vault/*` routes
- Enable RLS in Supabase (schema includes commented policies)
- Restrict access to `guest-id-vault.html` via server config

### Configuration
```python
RETENTION_YEARS = 7  # Change in server.py if needed
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
STORAGE_BUCKET = "guest-id-documents"
```

---

## Previous Implementations

### Phase 1-4 Summary
- Booking system with calendar, guest selector, dynamic pricing
- Aadhaar upload with 7-year retention (MongoDB)
- Traveller/Host view toggle
- Homepage redesign with trust signals
- SEO optimization (JSON-LD, sitemap, meta tags)
- Lead capture popups, multi-channel CTAs
- Analytics placeholders (GA4, Meta Pixel)

## Tech Stack
- Frontend: Vanilla HTML, CSS, JavaScript
- Backend: FastAPI + MongoDB + Supabase
- Storage: Supabase Storage (Guest ID Vault)
- Database: MongoDB (bookings) + Supabase (guest documents)

## Next Steps
1. Add Supabase keys to backend/.env
2. Run supabase-setup.sql in Supabase
3. Create storage bucket
4. Test the vault functionality
5. Push to GitHub
