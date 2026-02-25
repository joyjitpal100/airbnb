# CLAUDE.md — Airbnb / Xanadu Property Listing Site

## Project Overview

This is a **static HTML/CSS property listing website** for **Xanadu**, a serviced apartment rental company based in Kolkata, India. It operates as a marketing and booking-assist site, directing visitors to Airbnb listings or a WhatsApp contact for direct bookings.

- **Type**: Static multi-page website (no build system, no frameworks)
- **Tech stack**: Vanilla HTML5, CSS3, minimal vanilla JavaScript
- **Business contact**: WhatsApp +91 8918585499

---

## Repository Structure

```
airbnb/
├── index.html                    # Main landing page (property listing)
├── siddha-skyview-details.html   # Detail page for Siddha SkyView Studio
├── README.md                     # Minimal project description
├── CLAUDE.md                     # This file
└── Images/
    ├── 604.jpg                   # Main image for Siddha SkyView (living room)
    ├── 604-1.jpg                 # Secondary image (bedroom)
    ├── 604-2.jpeg                # Third image (pool)
    ├── Sona.jpeg                 # Host profile photo
    └── c8b3a273-....jpeg         # Additional property image
```

---

## Pages and Navigation Flow

### `index.html` — Landing / Listing Page
- Sticky header with nav link
- Hero section: greeting text + WhatsApp CTA button
- **Property list** (4 clickable cards):
  - **Siddha SkyView Studio** → navigates to `siddha-skyview-details.html` (internal)
  - **Xanadu 922, 313, 310** → open respective Airbnb URLs in a new tab
- Features grid (6 value-proposition cards in 3-column CSS Grid)
- "Discover" section: 2-column grid with image + description text

### `siddha-skyview-details.html` — Property Detail Page
- Sticky navbar with back button (`javascript:history.back()`) + property title
- Image gallery: CSS Grid with a main image spanning 2 rows and 2 side images
- Property info card: location, capacity (4 guests, 1 bed, 2 beds, 1 bath)
- Rating section: "Guest Favorite" badge, score 4.86, 86 reviews
- Host section: Sona — Superhost, 3 years hosting
- Features/amenities list (10 items with SVG icons)
- Description text block
- Google Maps embed (placeholder iframe)
- Fixed bottom booking button (Airbnb pink `#e31c5f`)

**Navigation flow:**
```
index.html
  ├── Siddha SkyView Studio → siddha-skyview-details.html
  │                                └── Back button → index.html
  ├── Xanadu 922 → airbnb.co.in/h/xanadu922 (new tab)
  ├── Xanadu 313 → airbnb.co.in/h/xanadu313 (new tab)
  └── Xanadu 310 → airbnb.co.in/h/xanadu310 (new tab)
```

---

## Tech Stack & Conventions

### HTML
- HTML5 with semantic elements (`<header>`, `<nav>`)
- All CSS is embedded in `<style>` tags within each HTML file (no external stylesheets)
- All JavaScript is embedded in `<script>` tags at the bottom of HTML files
- Image paths are **relative** (e.g., `src="604.jpg"`) — images must be in the same directory

### CSS
- CSS reset: `* { margin: 0; padding: 0; box-sizing: border-box; }`
- Global font: `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`
- Layout: CSS Grid for multi-column sections, Flexbox for alignment
- **Single responsive breakpoint**: `@media (max-width: 768px)` — collapses grids to single column
- Hover transitions use `transform: translateY(-Npx)` and `box-shadow`

### Color Palette
| Token | Hex | Usage |
|-------|-----|-------|
| Airbnb pink | `#e31c5f` | Booking button, ratings, CTA accents |
| Tan/beige | `#c0aa90` | Property list item background |
| Dark gray | `#333` | Primary text, headings |
| Medium gray | `#555` / `#777` | Secondary text, meta info |
| White | `#fff` | Card backgrounds, navbar |
| Body gradient | `#f5f7fa → #e4e8ee` | Page background (index.html) |

### JavaScript
- Minimal vanilla JS, no frameworks or libraries
- Event delegation via `querySelectorAll().forEach()`
- Property routing logic in `index.html`: detects "Siddha SkyView Studio" by `textContent` match to do an internal navigation vs. `window.open()` for others
- No async operations, no API calls, no state management

---

## Development Workflow

### Running Locally
No build step required. Open files directly in a browser or serve with a local HTTP server:

```bash
# Python (recommended to avoid relative-path issues)
python3 -m http.server 8000
# Then open http://localhost:8000

# Node.js alternative
npx serve .
```

### Editing
- Edit `index.html` for changes to the landing/listing page
- Edit `siddha-skyview-details.html` for the property detail page
- Add new images to the repository root (same directory as HTML files)
- There are no build, lint, or test steps

### Adding a New Property Page
1. Create a new `<property-name>-details.html` following the structure of `siddha-skyview-details.html`
2. Add a new `.property-item` div in `index.html`'s `.property-list` section with a `data-url` attribute
3. Update the JS routing block in `index.html` to detect the new property name and navigate internally

---

## Key Decisions & Constraints

- **No external CSS or JS files**: All styles and scripts are inline. This avoids caching benefits but simplifies deployment — any static host works with zero configuration.
- **Images are repo-local**: Property photos (604.jpg, 604-1.jpg, 604-2.jpeg, Sona.jpeg) are committed to the repository and referenced by relative paths. The detail page assumes images are in the same directory as the HTML file.
- **Icon images referenced but not present**: `siddha-skyview-details.html` references `icon1.svg` through `icon10.svg` for amenity icons; these files do not currently exist in the repository and will render as broken images.
- **Google Maps placeholder**: The `<iframe>` in the detail page has `src="https://www.google.com/maps/embed?pb=..."` — the `pb=` parameter is empty; a real embed URL is needed.
- **Booking button is decorative**: The "Book Now" button in the detail page has no `onclick` handler and performs no action.
- **Desktop-first responsive**: Designed for desktop; mobile styles are applied via a single `768px` breakpoint override.

---

## Git Workflow

- **Primary branch**: `master`
- **Feature/task branches**: follow the `claude/<description>-<id>` naming convention
- Commits have been simple and descriptive (e.g., `"Update siddha-skyview-details.html"`)
- No `.gitignore` — all files including binary images are tracked

---

## Known Issues / Improvement Areas

| Issue | Location | Notes |
|-------|----------|-------|
| Missing SVG icon files (`icon1.svg`–`icon10.svg`) | `siddha-skyview-details.html:270-280` | Amenity icons won't display |
| Empty Google Maps embed URL | `siddha-skyview-details.html:292` | Replace `pb=...` with actual embed URL |
| Booking button has no action | `siddha-skyview-details.html:296` | Link to Airbnb or WhatsApp |
| No `alt` text on `Sona.jpeg` host image | `siddha-skyview-details.html:260` | Accessibility gap |
| Routing logic uses fragile `textContent` match | `index.html:305` | Brittle if property name changes |
| No `<meta>` description or OG tags | Both pages | SEO/social sharing not optimised |
| Inline CSS prevents caching | Both pages | Consider extracting to `styles.css` if site grows |
