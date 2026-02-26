# Airbnb Property Listing Site - PRD

## Original Problem Statement
Build enhanced Airbnb property listing with:
1. Booking inputs (calendar, guest selector, dynamic pricing)
2. Two views (Traveller/Host) with toggle
3. Aadhaar upload with 7-year retention
4. FastAPI + MongoDB backend
5. Clean, responsive UI

## User Personas
- **Travellers**: Book property stays, upload Aadhaar for verification
- **Host (Admin)**: View all bookings, access guest Aadhaar documents

## Core Requirements
- Calendar date picker (check-in/check-out)
- Guest selector (1-4 max)
- Dynamic pricing: ₹2,500 base + ₹500 per extra guest (>2)
- Traveller/Host view toggle
- Aadhaar upload (JPG, PNG, PDF, max 5MB)
- 7-year document retention
- MongoDB storage for bookings
- File storage for Aadhaar documents

## What's Been Implemented (Feb 2026)

### Phase 1 (Initial)
- [x] Fixed UI issues (missing icons, layout)
- [x] Booking modal with QR payment
- [x] Success confirmation flow

### Phase 2 (Current)
- [x] FastAPI backend with MongoDB
- [x] Booking form with dates, guests, name, phone
- [x] Dynamic price calculation
- [x] Aadhaar file upload with validation
- [x] Traveller/Host view toggle
- [x] Host dashboard with booking list
- [x] Aadhaar viewing in Host view
- [x] 7-year retention metadata
- [x] Mobile responsive design
- [x] Created feature/calendar-host-traveller-aadhaar branch

## Tech Stack
- Frontend: Vanilla HTML5, CSS3, JavaScript
- Backend: FastAPI (Python)
- Database: MongoDB
- File Storage: Local filesystem (/app/uploads)

## API Endpoints
- `GET /api/health` - Health check
- `POST /api/bookings` - Create booking (multipart form)
- `GET /api/bookings` - List all bookings
- `GET /api/bookings/{id}` - Get single booking
- `GET /api/aadhaar/{filename}` - Download Aadhaar file
- `DELETE /api/bookings/{id}` - Delete booking

## Pricing Logic
- Base price: ₹2,500/night
- Extra guest charge: ₹500/night (for guests > 2)
- Max guests: 4
- Example: 3 guests, 2 nights = (₹2,500 × 2) + (₹500 × 1 × 2) = ₹6,000

## Test Results
- Backend: 100% (7/7 tests passed)
- Frontend: 95% (all features working)

## Files Modified
- `/app/siddha-skyview-details.html` - Complete booking system
- `/app/backend/server.py` - FastAPI backend
- `/app/backend/requirements.txt` - Python dependencies
- `/app/backend/.env` - Environment variables

## Next Action Items
1. Push to GitHub (feature/calendar-host-traveller-aadhaar branch)
2. Create PR and get reviewed
3. Share preview link

## Future/Backlog (P2)
- Authentication for Host view
- Email/SMS notifications
- Payment gateway integration
- Booking modification/cancellation
- Multiple property support
- Calendar availability blocking
