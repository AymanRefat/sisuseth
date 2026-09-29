# Optional features

Each feature below can be turned on or off without touching code:

**CMS → Site settings → "Features – turn website sections on/off"** → tick or untick → **Save**.

> Google reviews and referral codes were removed for now. They were built and tested in commit `5442d05`, so they can be restored from git history if wanted.

The change is live on the next page load. Turning a feature off only hides it. Its content (products, photos, codes) stays in the database, so turning it back on restores everything.

| # | Feature | Flag (`feature_…`) | Default | Needs content? |
|---|---|---|---|---|
| 1 | [Product price search](#1-product-price-search) | `product_search` | on | Products (18 seeded) |
| 2 | [Sticky mobile booking bar](#2-sticky-mobile-booking-bar) | `mobile_bar` | on | – |
| 3 | [Before/after slider](#3-beforeafter-slider) | `before_after` | on | Before/after photos (**none seeded**) |
| 4 | [Video strip](#4-video-strip) | `videos` | on | Videos (**none seeded**) |
| 5 | [Weekend-hours counter](#5-weekend-hours-counter) | `hours_counter` | on | – |
| 6 | [Animated weekend timeline](#6-animated-weekend-timeline) | `timeline_animation` | on | – |
| 7 | ["How long would it take you?" quiz](#7-how-long-would-it-take-you-quiz) | `quiz` | on | Products |
| 8 | [Hero box animation](#8-hero-box-animation) | `hero_animation` | on | – |
| 9 | [Household tax credit calculator](#9-household-tax-credit-calculator-kotitalousvähennys) | `tax_credit` | on | – |

If a feature is **on but has no content**, for example no before/after photos yet, the section is hidden automatically. It never shows up empty.

All text used by these features is under **CMS → Text blocks**, in Finnish, Swedish and English. Search for the key prefix shown in each section below (for example `quiz.`).

---

## 1. Product price search
A search box at the top of the pricing section. The customer types "PAX", "MALM" or "KALLAX" and sees the price and our assembly time. Each result has a WhatsApp/Telegram button with a pre-written message such as *"I'd like to book assembly for IKEA PAX wardrobe 100 cm (€85)…"*. If nothing matches, the customer is asked to send a photo of the box instead.

- **CMS:** *Products*. Each product has a name, brand, price (€), assembly time (minutes) and an active switch. Prices and times can be edited directly in the list view.
- **Starting data:** 18 common IKEA/JYSK/ISKU products, seeded as example estimates in the small (€55), medium (€85) and large (€120) price bands. **The owner should check these against their real prices.**
- **Texts:** `search.*`, `wa.product`
- **Code:** `frontend/src/features/ProductSearch.jsx`

## 2. Sticky mobile booking bar
On screens narrower than 820 px, a bar stays fixed at the bottom with **WhatsApp**, **Telegram** (only if a Telegram username is set) and **📞 Call** buttons. It is hidden on desktop.

- **CMS:** uses *Site settings → Contact*.
- **Texts:** `bar.call`, `wa.default`
- **Code:** `frontend/src/features/MobileBar.jsx`

## 3. Before/after slider
One slider per pair of photos, shown in a carousel (2 per page on desktop, 1 on phones). Dragging a slider reveals the finished furniture over the pile of boxes.

- **CMS:** *Before/after photos*. Upload a **before** photo, an **after** photo and an optional caption in EN/FI/SV, then set the order. Take both photos **from the same spot**, otherwise the effect doesn't work. Images are resized to 1600 px on upload.
- **Starting data:** none, because we don't have real before photos. The section stays hidden until the first pair is uploaded.
- **Texts:** `ba.*`
- **Code:** `frontend/src/features/BeforeAfter.jsx`

## 4. Video strip
A horizontal, swipeable row of short vertical clips (9:16) that play silently on a loop, like TikTok or Reels.

- **CMS:** *Videos*. Upload an MP4 file, an optional poster image shown while loading, and an optional caption.
- **Tips:** keep clips **short (10–30 s) and small (under 10 MB)**. They are served from our own small server, so big files slow the page down and use bandwidth. Export them from TikTok/Instagram without the watermark, or compress them with HandBrake.
- **Starting data:** none. The section is hidden until a video is uploaded.
- **Texts:** `videos.*`
- **Code:** `frontend/src/features/VideoStrip.jsx`

## 5. Weekend-hours counter
A big number that counts up when the visitor scrolls to it, for example **"1 240 hours of weekend given back to families in Helsinki, Espoo, Vantaa"**. It sits under the three steps.

- **How the number is calculated:** `hours_saved_base + (booking requests with status "Done") × hours_per_job`. It grows automatically as the owner marks bookings *Done* in *Booking requests*.
- **CMS:** *Site settings → Hours-saved counter*. `hours_saved_base` (default 1000) covers jobs done before this website existed. `hours_per_job` defaults to 3.
- **Texts:** `hours.label`
- **Code:** `frontend/src/features/HoursCounter.jsx`

## 6. Animated weekend timeline
The "DIY vs SISUSETH" comparison plays out when scrolled into view. Each row appears one after another, the DIY rows from midday on turn red and shake, and the SISUSETH card glows green. With the flag off, the timeline is shown without animation.

- **CMS:** *Weekend timeline rows*. Add, remove or reorder rows for each side (time + text in EN/FI/SV).
- Visitors whose system asks for reduced motion get no animation.
- **Code:** `Compare` in `frontend/src/App.jsx` and the "animated timeline" CSS in `frontend/src/index.css`

## 7. "How long would it take you?" quiz
The visitor picks a product and how handy they are, and gets a result like *"On your own: ~3 h 20 min …and about 3 arguments 😅 / With SISUSETH: ~50 min, €55"* with a booking button.

- **How it's calculated:** DIY time = the product's assembly time × a skill multiplier. Arguments = DIY hours, rounded, minimum 1.
- **CMS:** products come from *Products*. The multipliers are in *Site settings → Quiz* (beginner 4×, average 2.5×, handy 1.5×).
- **Texts:** `quiz.*`
- **Code:** `frontend/src/features/Quiz.jsx`

## 8. Hero box animation
A small card on the hero image where a flat-pack box opens, a shelf builds itself and a ✅ appears. It loops every 6 seconds. It uses only SVG and CSS, adds no images or libraries (under 1 KB), and is disabled for visitors who ask for reduced motion.

- **Texts:** `hero.animLabel`, a description for screen readers.
- **Code:** `frontend/src/features/HeroAnimation.jsx` and the "hero animation" CSS in `index.css`

## 9. Household tax credit calculator (kotitalousvähennys)
Placed under the price calculator. It shows the job price, the tax credit and the "real cost". It starts from the calculator's current estimate, and the visitor can type any price.

- **Formula:** `credit = price × labour share × rate`, capped at the yearly maximum. Example: €85 × 100 % × 35 % = €29.75 credit, so the real cost is €55.25.
- **Important, for the owner:**
  - The rules change. **Check [vero.fi](https://www.vero.fi/en/individuals/deductions/Tax-credit-for-household-expenses/) every January** and update *CMS → Site settings → Household tax credit*: rate %, labour share %, yearly deductible (own share) and yearly maximum. The defaults are 35 %, 100 %, €150 and €1600.
  - The **€150 own share applies per person per year across all household work**. A single €85 job does *not* give money back on its own unless the customer has other household work that year. The note under the calculator says this. Don't remove it, or the calculator becomes misleading.
  - To qualify, the company must be registered in the **prepayment register (ennakkoperintärekisteri)**, and the invoice must show the labour part separately. Confirm with the accountant that furniture assembly qualifies before turning this on.
  - If materials or travel are billed, lower the *labour share* so the estimate stays honest.
- **Texts:** `tax.*`
- **Code:** `frontend/src/features/TaxCredit.jsx`

---

## For developers: adding a new feature flag
1. Add `("my_feature", "Label shown in CMS", default)` to `FEATURES` in `backend/content/models.py`.
2. Run `uv run python manage.py makemigrations content && uv run python manage.py migrate`. The checkbox appears in the CMS and `settings.features.my_feature` appears in `/api/content/`.
3. In React: `{s.features.my_feature && <MyFeature />}`. Put the component in `frontend/src/features/`.
4. Add its texts to all three files in `frontend/src/locales/`, then run `uv run python manage.py seed` so they appear in the CMS.
5. Document it in this file.
