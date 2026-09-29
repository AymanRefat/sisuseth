# Optional features

Each feature below can be turned on or off without touching code:

**CMS → Site settings → "Features – turn website sections on/off"** → tick or untick → **Save**.

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
| 9 | [Google reviews](#9-google-reviews) | `google_reviews` | **off** | API key + Place ID |
| 10 | [Household tax credit calculator](#10-household-tax-credit-calculator-kotitalousvähennys) | `tax_credit` | on | – |
| 11 | [Referral codes](#11-referral-codes) | `referrals` | on | – |

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
One slider per pair of photos. Dragging it reveals the finished furniture over the pile of boxes.

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

- **CMS:** the times and texts are text blocks (`compare.*`, for example `compare.diy.3.time`).
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

## 9. Google reviews
Shows the Google rating, for example *"4.9 ★ from 87 Google reviews"*, up to 5 of the latest reviews and a "See all reviews on Google" link, above the testimonials section.

**Setup (one time):**
1. The business needs a **Google Business Profile** with reviews.
2. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable **Places API (New)**. Create an **API key** and restrict it to that API. Google requires a billing account, but this usage stays far inside the free monthly allowance: results are cached for 6 hours, so it makes at most about 12 requests a day.
3. Put the key on the server as `GOOGLE_PLACES_API_KEY` in `.env`, then restart.
4. Find the Place ID with Google's [Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id) and paste it into *CMS → Site settings → Google reviews*.
5. Tick `feature_google_reviews`.

If the key, the Place ID or Google itself is unavailable, the section simply doesn't appear. Reviews come in the visitor's language where Google has a translation.

- **Recommendation:** once this works, turn off or delete the placeholder *Testimonials* copied from the prototype. They look invented, and showing invented reviews as real ones is illegal under EU consumer law.
- **Texts:** `google.*`
- **Code:** `frontend/src/features/GoogleReviews.jsx`, `backend/content/services.py → fetch_google_reviews`

## 10. Household tax credit calculator (kotitalousvähennys)
Placed under the price calculator. It shows the job price, the tax credit and the "real cost". It starts from the calculator's current estimate, and the visitor can type any price.

- **Formula:** `credit = price × labour share × rate`, capped at the yearly maximum. Example: €85 × 100 % × 35 % = €29.75 credit, so the real cost is €55.25.
- **Important, for the owner:**
  - The rules change. **Check [vero.fi](https://www.vero.fi/en/individuals/deductions/Tax-credit-for-household-expenses/) every January** and update *CMS → Site settings → Household tax credit*: rate %, labour share %, yearly deductible (own share) and yearly maximum. The defaults are 35 %, 100 %, €150 and €1600.
  - The **€150 own share applies per person per year across all household work**. A single €85 job does *not* give money back on its own unless the customer has other household work that year. The note under the calculator says this. Don't remove it, or the calculator becomes misleading.
  - To qualify, the company must be registered in the **prepayment register (ennakkoperintärekisteri)**, and the invoice must show the labour part separately. Confirm with the accountant that furniture assembly qualifies before turning this on.
  - If materials or travel are billed, lower the *labour share* so the estimate stays honest.
- **Texts:** `tax.*`
- **Code:** `frontend/src/features/TaxCredit.jsx`

## 11. Referral codes
1. On the website, a customer enters their name and phone number under **"Invite a friend"** and gets a personal code (for example `MIKA482`) plus a share link `https://sisuseth.com/?ref=MIKA482`, which they can copy or share on WhatsApp. The same phone number always gets the same code.
2. When a friend opens the link, the code is checked, remembered in their browser, and a banner shows *"Code MIKA482 applied – €10 off your booking!"*.
3. The code is then added **automatically** to every WhatsApp/Telegram booking message and is pre-filled in the booking form. Customers can also type a code into the form by hand.
4. The Telegram alert for a new booking includes the code.

- **CMS:**
  - *Referrals*: all codes with the number of bookings made with each one, and the option to deactivate a code.
  - *Booking requests*: has a `referral code` column and search.
  - *Site settings → Referrals → discount*: the "€10" shown to the friend.
  - The referrer's reward is shown on the pricing packages ("€10 referral bonus"; *Pricing packages → referral bonus*).
- **The owner applies the discount and pays the reward by hand.** The website doesn't handle money. It only records who referred whom.
- **Spam protection:** each visitor can submit at most 20 forms per hour (bookings and codes).
- **Texts:** `ref.*`, `booking.referral`, `wa.referral`
- **Code:** `frontend/src/features/referral.jsx`, `backend/content/views.py → create_referral / check_referral`

---

## For developers: adding a new feature flag
1. Add `("my_feature", "Label shown in CMS", default)` to `FEATURES` in `backend/content/models.py`.
2. Run `uv run python manage.py makemigrations content && uv run python manage.py migrate`. The checkbox appears in the CMS and `settings.features.my_feature` appears in `/api/content/`.
3. In React: `{s.features.my_feature && <MyFeature />}`. Put the component in `frontend/src/features/`.
4. Add its texts to all three files in `frontend/src/locales/`, then run `uv run python manage.py seed` so they appear in the CMS.
5. Document it in this file.
