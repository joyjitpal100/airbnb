# Xanadu Stays - Property Listing Site PRD

## Original Problem Statement
Complete property listing site with:
1. Booking system (calendar, guest selector, dynamic pricing, Aadhaar upload)
2. Two views (Traveller/Host)
3. Conversion-optimized homepage
4. SEO optimization (JSON-LD, meta tags, sitemap)
5. Lead capture infrastructure (popups, multi-channel CTAs)
6. Analytics integration (GA4, Meta Pixel placeholders)

## User Personas
- **Travellers**: Book serviced apartments, discover via search
- **Host (Sona)**: Manage bookings, track leads

## What's Been Implemented (Feb 2026)

### Phase 1 - Initial Setup
- [x] Basic booking modal with QR payment

### Phase 2 - Booking System
- [x] FastAPI + MongoDB backend
- [x] Dynamic pricing (₹2,500 + ₹500/extra guest)
- [x] Aadhaar upload with 7-year retention
- [x] Traveller/Host view toggle

### Phase 3 - Homepage Redesign
- [x] Hero carousel with brand headline
- [x] Trust signals & reviews section
- [x] Property cards with pricing
- [x] About Host section

### Phase 4 - SEO & Lead Capture (Current)
#### SEO Optimization
- [x] JSON-LD structured data (LodgingBusiness, Apartment)
- [x] Individual property pages with unique URLs:
  - /siddha-skyview-details.html
  - /xanadu-922.html
  - /xanadu-313.html
  - /xanadu-310.html
- [x] SEO-optimized titles with keywords
- [x] Descriptive alt text on all 11 images
- [x] Meta tags (og:title, og:description, canonical)
- [x] sitemap.xml with 5 pages
- [x] robots.txt allowing full crawling
- [x] Long-tail keywords targeted:
  - "furnished apartment near Kolkata airport"
  - "studio for rent New Town Kolkata"
  - "serviced apartment CC2 mall"

#### Lead Capture Infrastructure
- [x] Email capture popup (10% off first stay)
- [x] Exit-intent popup (phone capture → WhatsApp)
- [x] Multi-channel CTAs:
  - WhatsApp (+91 89185 85499)
  - Phone (tel: link)
  - Email (joyjitpal@gmail.com)
  - Instagram (@xanadustays)
- [x] UTM tracking on all WhatsApp links
- [x] Google Analytics 4 placeholder
- [x] Meta Pixel placeholder

## Tech Stack
- Frontend: Vanilla HTML5, CSS3, JavaScript
- Backend: FastAPI + MongoDB
- Fonts: Plus Jakarta Sans
- Analytics: GA4, Meta Pixel (placeholders)

## Test Results
- Phase 3: Frontend 100%
- Phase 4: SEO 98%, Lead Capture 90%

## Files Modified/Created
- `/app/index.html` - Complete SEO + lead capture
- `/app/xanadu-922.html` - New property page
- `/app/xanadu-313.html` - New property page
- `/app/xanadu-310.html` - New property page
- `/app/sitemap.xml` - SEO sitemap
- `/app/robots.txt` - Crawler rules

## Analytics Setup Required
Replace placeholders with actual IDs:
1. GA4: Replace `GA_MEASUREMENT_ID` with your GA4 ID
2. Meta Pixel: Replace `PIXEL_ID` with your Facebook Pixel ID

## Next Action Items
1. Push to GitHub (feature/calendar-host-traveller-aadhaar)
2. Create PR and get reviewed
3. Submit sitemap.xml to Google Search Console
4. Add actual GA4 and Meta Pixel IDs

## Future/Backlog (P2)
- Real-time availability calendar sync
- Review widget integration (Google/Airbnb)
- Mailchimp/Sendinblue email automation
- Retargeting ads setup
- A/B testing on lead capture popups
