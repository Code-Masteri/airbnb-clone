```
 █████╗ ██╗██████╗ ██████╗ ███╗   ██╗██████╗
██╔══██╗██║██╔══██╗██╔══██╗████╗  ██║██╔══██╗
███████║██║██████╔╝██████╔╝██╔██╗ ██║██████╔╝
██╔══██║██║██╔══██╗██╔══██╗██║╚██╗██║██╔══██╗
██║  ██║██║██║  ██║██████╔╝██║ ╚████║██████╔╝
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═══╝╚═════╝
```

> A full-stack Airbnb clone. Search, filter, book, cancel, and share listings — with a dynamic pricing algorithm, Google auth, CDN image uploads, and shareable URLs. Built to production standards.

![Next.js](https://img.shields.io/badge/Next.js_14-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Prisma](https://img.shields.io/badge/Prisma-2D3748?style=flat-square&logo=prisma)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38BDF8?style=flat-square&logo=tailwind-css&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=flat-square&logo=cloudinary)
![NextAuth](https://img.shields.io/badge/NextAuth.js-black?style=flat-square)

---

## What makes this different from other clones

Most Airbnb clones render a list of cards and call it done. This one goes further.

The **pricing algorithm** adjusts nightly rates dynamically based on demand signals, listing popularity, and date range — longer stays get a discount, peak-demand periods cost more. The **advanced search and filter system** works entirely through URL query params, making every search result a shareable, bookmarkable link. Paste it anywhere and the exact filtered view opens — same category, location, dates, guest count, price range, and amenities. Images go straight to **Cloudinary CDN** and serve optimised WebP at the right resolution per device. Auth is **Google OAuth via NextAuth** with session handling, protected routes, and persistent user data via **Prisma + MongoDB**.

Everything is responsive. Designed mobile-first.

---

## Tech stack

| Layer            | Technology                 |
| ---------------- | -------------------------- |
| Framework        | Next.js 14 (App Router)    |
| Language         | TypeScript                 |
| Frontend         | React 18                   |
| Styling          | Tailwind CSS               |
| ORM              | Prisma                     |
| Database         | MongoDB (Atlas)            |
| Auth             | NextAuth.js — Google OAuth |
| Image storage    | Cloudinary CDN             |
| Form handling    | React Hook Form            |
| Form validation  | Zod                        |
| Date picker      | React Date Range           |
| State management | Zustand                    |

---

## Features

**Auth**

- Google OAuth via NextAuth.js
- Persistent sessions with JWT
- Protected routes — guests redirected to login for booking and listing actions
- User profile with hosted listings and trip history

**Listings**

- Create a listing with multi-step form (location → details → photos → pricing)
- Cloudinary CDN upload with drag-and-drop image picker
- Category tags (Beach, Mountains, Cabins, Pools, Farms, etc.)
- Edit and delete your own listings
- Listing detail page with full photo display, host card, and amenities

**Search and filter**

- Filter by: category, location, dates, guest count, price range, amenities
- All filters encoded in URL query params — every search is a shareable link
- Map-based location input
- Instant results with no full-page reload

**Booking**

- React Date Range calendar with unavailable dates blocked out
- Real-time price breakdown as dates are selected
- Reserve a listing — creates a confirmed booking
- Cancel a reservation from the trips dashboard
- Hosts can cancel incoming reservations from their dashboard
- Blocked dates update in real time after a booking is confirmed

**Pricing algorithm**

- Base nightly rate set by the host
- Length-of-stay discount: 7+ nights = 10% off, 28+ nights = 20% off
- Demand multiplier: scales based on how many bookings the listing has in the last 30 days
- Season factor: configurable peak pricing by month
- Service fee applied at checkout (fixed percentage)
- Full breakdown shown to guest before confirming

**Shareable URLs**

- Every search, filter combination, and listing is a stable URL
- Share a filtered search and the recipient lands on the exact same view
- Works across sessions and devices — no login required to view

**UX**

- Fully responsive — mobile, tablet, desktop
- Loading skeletons for all async states
- Toast notifications for actions (booking confirmed, listing saved, etc.)
- Empty states with clear CTAs
- Image optimisation via Next.js Image + Cloudinary

---

## Project structure

```
airbnb-clone/
├── app/
│   ├── layout.tsx                      # Root layout — providers, navbar, modals
│   ├── page.tsx                        # Home — listing grid + category filter bar
│   ├── listings/
│   │   └── [listingId]/
│   │       └── page.tsx                # Listing detail + booking panel
│   ├── trips/
│   │   └── page.tsx                    # Guest — my reservations
│   ├── reservations/
│   │   └── page.tsx                    # Host — incoming reservations
│   ├── favorites/
│   │   └── page.tsx                    # Saved listings
│   ├── properties/
│   │   └── page.tsx                    # Host — my listings
│   └── api/
│       ├── auth/
│       │   └── [...nextauth]/
│       │       └── route.ts            # NextAuth Google OAuth handler
│       ├── listings/
│       │   ├── route.ts                # GET all / POST create
│       │   └── [listingId]/
│       │       └── route.ts            # GET one / DELETE
│       ├── reservations/
│       │   ├── route.ts                # POST create reservation
│       │   └── [reservationId]/
│       │       └── route.ts            # DELETE cancel
│       ├── favorites/
│       │   └── [listingId]/
│       │       └── route.ts            # POST / DELETE toggle favourite
│       └── register/
│           └── route.ts                # POST create user (email fallback)
│
├── components/
│   ├── navbar/
│   │   ├── Navbar.tsx
│   │   ├── Logo.tsx
│   │   ├── Search.tsx                  # Search bar with location + dates + guests
│   │   └── UserMenu.tsx
│   ├── modals/
│   │   ├── Modal.tsx                   # Base modal component
│   │   ├── LoginModal.tsx
│   │   ├── RegisterModal.tsx
│   │   ├── RentModal.tsx               # Multi-step listing creation
│   │   └── SearchModal.tsx             # Advanced filter modal
│   ├── listings/
│   │   ├── ListingCard.tsx
│   │   ├── ListingGrid.tsx
│   │   ├── ListingHead.tsx             # Hero image + title
│   │   ├── ListingInfo.tsx             # Amenities, description, map
│   │   ├── ListingReservation.tsx      # Calendar + price + reserve button
│   │   └── ListingCategory.tsx
│   ├── inputs/
│   │   ├── Input.tsx                   # React Hook Form input
│   │   ├── CategoryInput.tsx
│   │   ├── CountrySelect.tsx
│   │   ├── ImageUpload.tsx             # Cloudinary upload widget
│   │   ├── Counter.tsx
│   │   └── Calendar.tsx                # React Date Range wrapper
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Avatar.tsx
│   │   ├── CategoryBox.tsx
│   │   ├── Container.tsx
│   │   ├── EmptyState.tsx
│   │   └── Loader.tsx
│   └── Map.tsx                         # Leaflet map with dynamic import
│
├── hooks/
│   ├── useLoginModal.ts                # Zustand store for modal state
│   ├── useRegisterModal.ts
│   ├── useRentModal.ts
│   ├── useSearchModal.ts
│   ├── useFavorite.ts                  # Toggle + optimistic update
│   ├── useCountries.ts                 # Country data + formatting
│   └── useSearchParams.ts              # Read/write URL search params
│
├── lib/
│   ├── prismadb.ts                     # PrismaClient singleton
│   ├── auth.ts                         # NextAuth config + Google provider
│   └── cloudinary.ts                   # Cloudinary config + upload helpers
│
├── actions/                            # Next.js server actions
│   ├── getCurrentUser.ts
│   ├── getListings.ts                  # Filtered query — reads URL params
│   ├── getListingById.ts
│   ├── getReservations.ts
│   └── getFavoriteListings.ts
│
├── prisma/
│   └── schema.prisma
│
├── types/
│   └── index.ts
│
├── middleware.ts                        # Protected route config
├── next.config.js
└── .env
```

---

## Key decisions

**Why Prisma with MongoDB instead of Mongoose?**
Prisma gives you a typed query builder, schema-as-code in `schema.prisma`, and generated types that flow through the entire app. Mongoose models and TypeScript don't integrate as cleanly — you end up writing types twice. Prisma's MongoDB adapter handles ObjectId serialisation automatically.

**Why URL params for search state instead of Zustand or server state?**
Any search state stored in memory or a global store dies on refresh and can't be shared. URL params are permanent, shareable, and indexable. The trade-off is that URL manipulation is slightly more verbose — but the `useSearchParams` hook abstracts it to a single `setFilter(key, value)` call.

**Why Cloudinary over storing images in MongoDB or Next.js public?**
MongoDB has a 16MB document size limit — storing binary directly is the wrong approach. Serving images from `public/` works locally but doesn't scale and means deploying images with code. Cloudinary provides a CDN, automatic WebP conversion, responsive resizing via URL params (`w_800,f_auto`), and a free tier that covers most hobby projects.

**Why React Hook Form over controlled inputs?**
The listing creation form has 7 steps and a dozen fields. With controlled inputs, every keystroke re-renders the entire form tree. React Hook Form registers inputs with refs by default, so re-renders only happen on submit or explicit validation — the form is dramatically more performant at no additional complexity cost.

---

## Screenshots

| Home                | Listing detail                | Booking                            |
| ------------------- | ----------------------------- | ---------------------------------- |
| Category filter bar | Photo gallery, map, host info | Calendar, price breakdown, reserve |

---

## License

MIT
