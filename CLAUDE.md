# CLAUDE.md — Xanadu Stays Property Listing Site

## Project Overview

This is a **multi-page property listing website** for **Xanadu Stays**, a serviced apartment rental company based in Kolkata, India. The site handles marketing, direct bookings (with Aadhaar KYC), UPI payment confirmation, and guest ID management.

- **Type**: Static HTML/CSS frontend + Python Flask backend API
- **Tech stack**: Vanilla HTML5, CSS3, vanilla JavaScript (frontend); Python/Flask, Supabase (backend)
- **Hosting**: Netlify (static frontend) + separate backend server
- **Business contact**: WhatsApp +91 8918585499

---

## Repository Structure

```
airbnb/
├── index.html                    # Main landing/listing page
├── siddha-skyview-details.html   # Siddha SkyView detail + booking (traveller/host dual view)
├── xanadu-922.html               # Xanadu 922 property detail page
├── xanadu-313.html               # Xanadu 313 property detail page
├── xanadu-310.html               # Xanadu 310 property detail page
├── guest-id-vault.html           # Guest KYC/ID submission and admin management
├── CLAUDE.md                     # This file
├── README.md                     # Minimal project description
│
├── Images/                       # All image assets (served from repo root)
│   ├── 604.jpg                   # Living room (hero slide 1, property card)
│   ├── 604-1.jpg                 # Bedroom (hero slide 2, xanadu-922 hero)
│   ├── 604-2.jpeg                # Pool (hero slide 3, image grid)
│   ├── Sona.jpeg                 # Host profile photo
│   ├── c8b3a273-....jpeg         # Additional property image
│   └── payment-qr.png            # UPI payment QR code
│
├── backend/                      # Python/Flask API server
│   ├── server.py                 # Flask app with booking & guest-ID endpoints
│   ├── requirements.txt          # Python dependencies (flask, supabase, etc.)
│   └── tests/
│       └── test_vault_api.py     # API unit tests
├── backend_test.py               # Standalone backend test script
├── supabase-setup.sql            # Supabase (PostgreSQL) schema
│
├── frontend/                     # React scaffold (mostly passes through to public/)
│   ├── package.json
│   ├── public/                   # Mirrors root HTML + images for local dev
│   └── src/
│       ├── index.js              # React entry point
│       └── setupProxy.js         # Dev proxy → localhost:8001
│
├── netlify/
│   └── functions/vault/
│       ├── vault.js              # Netlify Function: guest-ID vault endpoint
│       └── shared.js             # Shared utilities for functions
│
├── netlify.toml                  # Netlify build/deploy config
├── .netlifyignore                # Files excluded from Netlify deploy
├── robots.txt                    # SEO: search engine directives
├── sitemap.xml                   # XML sitemap (6 pages)
├── serve.json                    # Static file server config
├── dev-server.js                 # Local Node.js dev server
├── .gitignore                    # Git exclusions
└── memory/
    └── PRD.md                    # Product Requirements Document
```

---

## Pages and Navigation Flow

```
index.html (HOME)
  ├── "Siddha SkyView Studio" card → siddha-skyview-details.html
  │     ├── [Traveller view] Booking form → payment modal → success modal
  │     ├── [Host view] Bookings dashboard → Aadhaar document preview modal
  │     └── Back button → index.html
  │
  ├── "Xanadu 922" card → xanadu-922.html
  │     ├── "Book via WhatsApp" → wa.me/918918585499 (new tab)
  │     └── "View on Airbnb" → airbnb.co.in/h/xanadu922 (new tab)
  │
  ├── "Xanadu 313" card → xanadu-313.html (same pattern as 922)
  ├── "Xanadu 310" card → xanadu-310.html (same pattern as 922)
  │
  ├── Nav "Guest ID Vault" → guest-id-vault.html
  ├── Nav "Book Now" CTA → openInquiryModal() → WhatsApp redirect
  └── Sticky sidebar WhatsApp/phone → external links
```

---

## Page Descriptions

### `index.html` — Landing Page
- **Sticky navbar**: Logo "XanaduStays", nav links (Properties, Reviews, About, Guest ID Vault), "Book Now" CTA
- **Hero carousel**: 3 slides (604.jpg, 604-1.jpg, 604-2.jpeg), auto-rotates every 5s, dot indicators
- **Search bar**: Check-in / Check-out / Guests inputs → redirects to `siddha-skyview-details.html`
- **Property cards grid**: 4 cards (Siddha SkyView, 922, 313, 310) with badge, rating, price
- **Host section**: Sona's profile with superhost stats
- **Reviews section**: Aggregate score + 3 individual review cards
- **Policies section**: 6 policy cards (check-in, checkout, cancellation, etc.)
- **Contact channels**: WhatsApp, Phone, Email, Instagram (4-column grid)
- **Inquiry modal**: Form → builds WhatsApp message → opens `wa.me/918918585499`
- **Email capture popup**: Appears after 15 seconds (persisted via localStorage)
- **Exit intent popup**: Fires on `mouseout` (desktop only, persisted via localStorage)
- **Analytics**: Google Analytics (`gtag`) + Facebook Pixel (`fbq`)

### `siddha-skyview-details.html` — Property Detail + Booking
- **Dual-view toggle**: Traveller (default) / Host — switched via `switchView()`
- **Traveller view**:
  - Image grid (main 2-row span + 2 side images)
  - Property info: Kolkata apartment, 4 guests, 1 bed, 2 beds, 1 bath
  - **Booking form**: Name, Phone, Check-in, Check-out, Guests, Aadhaar upload (JPG/PNG/PDF ≤5 MB)
  - Dynamic price summary: ₹2,500/night base + ₹500/night per extra guest (>2)
  - "Book Now" button disabled until all fields + file are provided
  - Payment modal: QR code (`payment-qr.png`), "I Have Paid" → `confirmPayment()`
  - Success modal: Booking confirmation with auto-generated ID
- **Host view**:
  - Bookings dashboard (fetched from `/api/bookings`)
  - Per-booking: ID, guest name, dates, guests, total, phone, submission date
  - "View Aadhaar" button → modal with image preview or PDF link

### `xanadu-922.html`, `xanadu-313.html`, `xanadu-310.html` — Property Pages
Lightweight, identical structure:
- Sticky navbar with back button → `index.html`
- Hero image
- Property metadata (guests, bedrooms, beds, rating)
- Amenities grid (2-col desktop / 1-col mobile)
- Two CTA buttons: WhatsApp (green `#25d366`) + Airbnb link (pink `#e31c5f`)

### `guest-id-vault.html` — KYC / Guest ID Management
- **Guest view**: Submit form (Name, Email, Phone, Aadhaar upload, consent checkboxes)
- **Admin view**: List of submitted IDs with document preview modal and revoke/delete action
- **API endpoints used**: `POST /api/guest-ids`, `GET /api/guest-ids`, `DELETE /api/guest-ids/{id}`

---

## Backend API (Python/Flask)

**Entry point**: `backend/server.py`
**Dev port**: `8001` (hardcoded in frontend JS when `hostname === 'localhost'`)
**Prod URL**: `window.location.origin` (same-origin via Netlify proxy or deployed server)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/bookings` | Create booking; accepts `multipart/form-data` with Aadhaar file |
| GET | `/api/bookings` | Retrieve all bookings (host dashboard) |
| GET | `/api/aadhaar/{filename}` | Serve uploaded Aadhaar document |
| POST | `/api/guest-ids` | Submit guest KYC ID |
| GET | `/api/guest-ids` | List all guest IDs |
| DELETE | `/api/guest-ids/{id}` | Revoke/delete a guest ID |

**Database**: Supabase (PostgreSQL). Schema defined in `supabase-setup.sql`.

### Running the Backend Locally
```bash
cd backend
pip install -r requirements.txt
python server.py        # Starts on http://localhost:8001
```

### Running Backend Tests
```bash
cd backend
python -m pytest tests/test_vault_api.py
# or from repo root:
python backend_test.py
```

---

## Frontend Dev Setup

The `frontend/` directory is a React scaffold that proxies API calls to `localhost:8001`:

```bash
cd frontend
npm install
npm start           # React dev server; proxies /api/* → localhost:8001
```

For **static-only** development (no React build needed):
```bash
# From repo root
python3 -m http.server 8000
# or
node dev-server.js
# or
npx serve .
```

---

## Netlify Deployment

- **Config**: `netlify.toml`
- **Excluded files**: `.netlifyignore`
- **Serverless functions**: `netlify/functions/vault/vault.js` handles the guest-ID vault endpoint in production
- **Static assets**: HTML files + images from repo root are deployed as-is
- The frontend React build output (if generated) would go to `frontend/build/`

---

## Tech Stack & Conventions

### HTML
- HTML5 semantic elements (`<header>`, `<nav>`, `<main>`)
- All CSS is embedded in `<style>` tags per file — no external stylesheets
- All JS is embedded in `<script>` tags at the bottom of each file
- Image paths are **relative** (`src="604.jpg"`) — images must be in the same directory as the HTML file

### CSS
- CSS reset: `* { margin: 0; padding: 0; box-sizing: border-box; }`
- **Primary font**: "Plus Jakarta Sans" (Google Fonts, weights 400–700); fallback: `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`
- Layout: CSS Grid for multi-column sections; Flexbox for alignment
- Responsive breakpoints: `@media (max-width: 900px)` and `@media (max-width: 768px)` and `@media (max-width: 600px)`
- Hover transitions: `transform: translateY(-Npx)` + `box-shadow` changes
- Font scaling: `clamp()` for responsive heading sizes

### Color Palette
| Token | Hex | Usage |
|-------|-----|-------|
| Airbnb pink | `#e31c5f` | Primary CTAs, bookings, accents |
| Teal/green | `#00a699` | Secondary accents, confirmations, host verified badge |
| Dark | `#1a1a1a` / `#222` / `#333` | Text, headings, footer background |
| Light gray | `#f7f7f7` / `#fafafa` | Body backgrounds |
| Gold | `#ffc107` | Star ratings |
| WhatsApp green | `#25d366` | WhatsApp buttons |

### JavaScript
- Vanilla JS, no frameworks or libraries
- **API URL detection**:
  ```javascript
  const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8001'
    : window.location.origin;
  ```
- **Booking constants**:
  ```javascript
  const BASE_PRICE = 2500;        // ₹ per night
  const EXTRA_GUEST_PRICE = 500;  // ₹ per extra guest per night (beyond 2)
  const MAX_GUESTS = 4;
  const WHATSAPP_NUMBER = '918918585499';
  ```
- Async `fetch()` for all API calls (bookings, guest IDs, Aadhaar retrieval)
- `localStorage` for persisting popup-shown flags (`emailPopupShown`, `exitPopupShown`)
- Property card routing in `index.html` uses `textContent` match on "Siddha SkyView Studio" to navigate internally vs. `window.open()` for Airbnb URLs

---

## Adding a New Property Page

1. Create `<property-name>.html` following the structure of `xanadu-922.html`
2. Add a card in `index.html`'s property grid
3. Update the JS routing block to navigate internally or open an external URL
4. Update `sitemap.xml` with the new page URL
5. Add the new page to the navbar if appropriate

---

## Git Workflow

- **Primary branch**: `master`
- **Feature/task branches**: `claude/<description>-<id>` naming convention
- `.gitignore` is present; binary images are tracked in the repo
- No build artifacts to commit — HTML/CSS/JS are source files

---

## Known Issues / Improvement Areas

| Issue | Location | Notes |
|-------|----------|-------|
| Missing SVG icon files (`icon1.svg`–`icon10.svg`) | `siddha-skyview-details.html` | Amenity icons render as broken images |
| Empty Google Maps embed URL | `siddha-skyview-details.html` | `pb=` param is empty; needs real embed URL |
| No `alt` text on `Sona.jpeg` | `siddha-skyview-details.html` | Accessibility gap |
| Fragile property routing via `textContent` match | `index.html` | Breaks if property name text changes |
| No OG / meta description tags | `xanadu-*.html`, `guest-id-vault.html` | SEO/social sharing not optimised on detail pages |
| Inline CSS prevents browser caching | All pages | Extract to `styles.css` if site grows |
| `frontend/` React scaffold largely unused | `frontend/` | Static files in `frontend/public/` duplicate root HTML |
| `uploads/` directory not gitignored | `uploads/` | Aadhaar files should never be committed |
| Booking button in host dashboard has no pagination | `siddha-skyview-details.html` | `loadBookings()` fetches all records with no limit |
