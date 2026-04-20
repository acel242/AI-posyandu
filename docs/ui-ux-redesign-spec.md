# UI/UX Redesign: AI-Posyandu
**Date:** 2026-04-20
**Goal:** Clean, minimalist, aesthetic UI/UX

## Design Direction
Hybrid — Apple Health meets Indonesian Posyandu. Putih dominan, hijau tua sebagai accent.

## Visual System

### Colors
- Primary: `#0D3B20` (deep forest green)
- Accent: `#16A34A` (emerald)
- Success: `#16A34A`
- Warning: `#F59E0B` (amber)
- Danger: `#EF4444` (red)
- Background: `#F8FAF9` (very light green-gray)
- Card: `#FFFFFF` with `0 1px 3px rgba(0,0,0,0.04)`
- Border: `#E5E7EB`

### Typography
- Font: Inter (already in use)
- Headings: 600-700 weight
- Body: 400-500 weight
- Sizes: 14px body, 16px headings, 12px labels

### Spacing & Corners
- Card radius: 12px
- Button radius: 8px
- Chip radius: 20px
- Modal radius: 16px
- Shadows: subtle `0 1px 3px rgba(0,0,0,0.04)` for cards

## Layout

### Login
- `#0D3B20` gradient background
- White centered card, rounded 16px, shadow
- Green circle logo with white "AI" text
- Clean inputs with border
- Emerald green "Masuk" button, full width

### Dashboard (all roles)
- Top navbar: white, with logo + nav items + user avatar
- Welcome banner: `#0D3B20` gradient, rounded 20px, white text
- Stats: 3-4 cards in grid, white, icon in colored circle
- Table: minimal borders, clean, hover effect
- Filters: pill chips, active=green
- FAB: green circle, bottom-right

### Child Form Modal
- White, rounded 16px, shadow
- Header with title + X button
- Clean form fields
- Emerald "Simpan" button

### Status Badges
- Green (normal): `#16A34A` bg, white text
- Yellow (risiko): `#F59E0B` bg, white text
- Red (rujuk): `#EF4444` bg, white text
- Blue (unmeasured): `#3B82F6` bg, white text

## Files to Update
1. `dashboard/src/index.css` — color tokens + typography + components
2. `dashboard/src/pages/Login.jsx` — login redesign
3. `dashboard/src/pages/KaderDashboard.jsx` — welcome + stats + table
4. `dashboard/src/pages/BidanDashboard.jsx` — same + measurement form
5. `dashboard/src/pages/KadesDashboard.jsx` — same
6. `dashboard/src/components/Navbar.jsx` — white navbar
7. `dashboard/src/components/ChildForm.jsx` — modal styling
8. `dashboard/src/components/ChildTable.jsx` — table styling
9. `dashboard/src/components/RiskBadge.jsx` — badge styling
