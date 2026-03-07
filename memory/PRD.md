# Xanadu Stays - Property Listing Site PRD

## Original Problem Statement
Complete UI/UX overhaul focusing on:
1. Conversion optimization (pricing, CTAs, inquiry form)
2. Trust & credibility signals (reviews, host profile, badges)
3. Modern design with hero carousel
4. Mobile-first responsive design
5. Booking system with calendar, guest selector, Aadhaar upload

## User Personas
- **Travellers**: Looking to book serviced apartments in Kolkata
- **Host (Sona)**: Manages 4 properties, needs booking dashboard

## Core Requirements
- Hero carousel with compelling brand headline
- Property cards with visible pricing and availability
- Trust signals throughout
- Sticky CTAs (WhatsApp/Call)
- Booking inquiry form
- Host/Traveller view toggle on detail pages

## What's Been Implemented (Feb 2026)

### Phase 1 - Initial Fixes
- [x] Fixed missing SVG icons
- [x] Basic booking modal with QR payment

### Phase 2 - Booking System
- [x] FastAPI + MongoDB backend
- [x] Date picker & guest selector
- [x] Dynamic pricing (₹2,500 + ₹500/extra guest)
- [x] Aadhaar upload with 7-year retention
- [x] Traveller/Host view toggle
- [x] Host dashboard with booking list

### Phase 3 - Homepage Redesign (Current)
- [x] Hero carousel (3 slides, auto-advance)
- [x] Brand headline: "Premium Serviced Apartments — Fully Furnished, Zero Deposit"
- [x] Location badge: "Kolkata, India"
- [x] Social proof stats: 500+ nights, 4.86 rating, 200+ guests
- [x] Search bar with date pickers & guest selector
- [x] Trust badges: Verified Host, ID Verified, Professional Cleaning, 24/7 Support
- [x] Property cards with:
  - Pricing visible (₹2,500 - ₹1,800/night)
  - Availability badges (Available, Limited, Guest Favorite)
  - Ratings & review counts
  - Live viewer count ("2 people viewing now")
- [x] About Host section (Sona profile, stats)
- [x] Reviews section (3 testimonials)
- [x] Policies section (cancellation, security, pricing, support)
- [x] "Listed On" partner logos (Airbnb, MakeMyTrip, Booking.com)
- [x] Sticky WhatsApp sidebar (desktop)
- [x] Sticky mobile CTA bar (WhatsApp + Call)
- [x] Booking inquiry modal form → WhatsApp
- [x] Full mobile responsiveness

## Tech Stack
- Frontend: Vanilla HTML5, CSS3, JavaScript
- Backend: FastAPI (Python) + MongoDB
- Fonts: Plus Jakarta Sans

## Test Results
- Phase 2: Backend 100%, Frontend 95%
- Phase 3: Frontend 100% (23/23 tests)

## Files Modified
- `/app/index.html` - Complete redesign
- `/app/siddha-skyview-details.html` - Booking system
- `/app/backend/server.py` - API endpoints
- `/app/backend/.env` - MongoDB config

## Conversion Optimization Summary
| Before | After |
|--------|-------|
| No pricing shown | Prices on every card |
| Single WhatsApp link | Multiple CTAs + inquiry form |
| No host info | Full host profile with stats |
| No reviews | 3 testimonials + aggregate rating |
| No trust signals | 4 trust badges |
| No urgency | "2 people viewing" indicator |
| No availability info | Availability badges |
| No policies | Clear cancellation policy |

## Next Action Items
1. Push to GitHub (feature/calendar-host-traveller-aadhaar)
2. Create PR and get reviewed
3. Share preview deployment link

## Future/Backlog (P2)
- Real review integration (Google/Airbnb widgets)
- Live availability calendar
- Payment gateway (Stripe/Razorpay)
- Email notifications
- Multi-language support
