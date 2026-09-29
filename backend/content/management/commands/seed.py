"""Load the starting content from the customer's prototype.

Safe to run on every deploy:
- Each section is filled ONCE and then remembered in SiteSettings.seeded_sections, so content the owner
  deletes or replaces in the CMS is never brought back.
- New UI text keys (added in frontend/src/locales/*.json) are added as text blocks; existing ones are
  never overwritten. Keys that were removed from the code are deleted.
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import (
    FAQ, CalculatorOption, GalleryImage, PainPoint, PricingPackage, Product, SiteSettings, Step, Testimonial, TextBlock,
    TimelineEntry,
)

LOCALES_DIR = Path(settings.BASE_DIR).parent / "frontend" / "src" / "locales"
SEED_IMAGES = Path(__file__).resolve().parents[2] / "seed_images"

PACKAGES = [
    # (en, fi, sv names), (en, fi, sv descriptions), price, hours, referral, popular
    (("Basic", "Perus", "Bas"), ("Small furniture items", "Pienet huonekalut", "Små möbler"), 55, 1, 0, False),
    (("Standard", "Standard", "Standard"), ("Medium furniture items", "Keskikokoiset huonekalut", "Medelstora möbler"), 85, 2, 10, True),
    (("Premium", "Premium", "Premium"), ("Large furniture sets", "Suuret kalustekokonaisuudet", "Stora möbelset"), 120, 3, 15, False),
]

CALCULATOR = [
    (("Small items (chairs, shelves)", "Pienet (tuolit, hyllyt)", "Små (stolar, hyllor)"), 55, False),
    (("Medium items (wardrobes, desks)", "Keskikokoiset (kaapit, pöydät)", "Medelstora (garderober, skrivbord)"), 85, False),
    (("Large items (kitchens, bedroom sets)", "Suuret (keittiöt, makuuhuonekalusteet)", "Stora (kök, sovrumsset)"), 120, False),
    (("Large wardrobes (PAX etc.)", "Suuret vaatekaapit (PAX ym.)", "Stora garderober (PAX m.fl.)"), 40, True),
]

FAQS = [
    (("Is it safe to let strangers into my home?", "Onko turvallista päästää vieraita kotiin?", "Är det säkert att släppa in främlingar i hemmet?"),
     ("Absolutely. Our team members are background-checked and insured, we verify ID before service, and we carry full insurance.",
      "Ehdottomasti. Tiimimme jäsenten taustat on tarkistettu ja he ovat vakuutettuja. Esittelemme henkilöllisyyden ennen työtä, ja meillä on kattava vakuutus.",
      "Absolut. Vårt team är bakgrundskontrollerat och försäkrat, vi visar legitimation före arbetet och har fullständig försäkring.")),
    (("Do you bring your own tools?", "Tuotteko omat työkalut?", "Tar ni med egna verktyg?"),
     ("Yes! We bring everything from screwdrivers to power drills. You don't need to provide anything.",
      "Kyllä! Tuomme kaiken ruuvimeisseleistä porakoneisiin. Sinun ei tarvitse hankkia mitään.",
      "Ja! Vi tar med allt från skruvmejslar till borrmaskiner. Du behöver inte ordna något.")),
    (("How quickly can you come?", "Kuinka nopeasti pääsette paikalle?", "Hur snabbt kan ni komma?"),
     ("We offer same-day and next-day service in Helsinki, Espoo and Vantaa. Most bookings are scheduled within 24–48 hours. Weekend slots fill up quickly!",
      "Tarjoamme palvelua samana tai seuraavana päivänä Helsingissä, Espoossa ja Vantaalla. Useimmat varaukset hoidetaan 24–48 tunnissa. Viikonloppuajat täyttyvät nopeasti!",
      "Vi erbjuder service samma dag eller nästa dag i Helsingfors, Esbo och Vanda. De flesta bokningar ordnas inom 24–48 timmar. Helgtider går åt snabbt!")),
    (("What if something goes wrong?", "Entä jos jokin menee pieleen?", "Vad händer om något går fel?"),
     ("We guarantee our work. If there's any issue with the assembly we'll come back and fix it free of charge. We're also fully insured.",
      "Takaamme työmme. Jos kokoamisessa on ongelmia, tulemme korjaamaan sen veloituksetta. Olemme myös täysin vakuutettuja.",
      "Vi garanterar vårt arbete. Om något är fel med monteringen kommer vi tillbaka och åtgärdar det kostnadsfritt. Vi är även fullt försäkrade.")),
    (("Do you work with all furniture brands?", "Kokoatteko kaikkien merkkien huonekaluja?", "Monterar ni alla möbelmärken?"),
     ("Yes! We work with all major brands including IKEA, JYSK, Kodin1 and many others.",
      "Kyllä! Kokoamme kaikkia suuria merkkejä, kuten IKEA, JYSK, Kodin1 ja monia muita.",
      "Ja! Vi monterar alla stora märken, bland annat IKEA, JYSK, Kodin1 och många fler.")),
    (("How do I pay?", "Miten maksan?", "Hur betalar jag?"),
     ("We accept cash, card and MobilePay. Payment is due after the job is done and you're happy – no upfront payment.",
      "Hyväksymme käteisen, kortin ja MobilePayn. Maksu suoritetaan vasta, kun työ on valmis ja olet tyytyväinen – ei ennakkomaksua.",
      "Vi tar emot kontanter, kort och MobilePay. Du betalar först när jobbet är klart och du är nöjd – ingen förskottsbetalning.")),
]

# Copied from the prototype. Replace with real, verified customer reviews before launch.
TESTIMONIALS = [
    ("Emma Virtanen", "Helsinki", "Had 3 JYSK wardrobes sitting in boxes for months. SISUSETH assembled them all in one morning. Amazing service!"),
    ("Mikael Johansson", "Espoo", "Professional, punctual, and perfect results. My dining room set looks like it came from a showroom."),
    ("Anna Korhonen", "Vantaa", "They assembled my entire home office setup in 2 hours. I can't believe I waited so long to call them."),
    ("Petri Mäkinen", "Helsinki", "They handled my daughter's bedroom set perfectly. Clean, professional and incredibly efficient."),
    ("Laura Nieminen", "Espoo", "My complex PAX closet system was done in half the time I expected. No stress, just results."),
    ("Timo Aalto", "Espoo", "My elderly parents needed help with their new furniture. SISUSETH was patient, respectful and did beautiful work."),
]



# Example estimates in the price categories above (small 55 / medium 85 / large 120).
PRODUCTS = [
    ("IKEA", "BILLY bookcase", 55, 45), ("IKEA", "KALLAX shelf 2×4", 55, 45), ("IKEA", "LACK coffee table", 55, 20),
    ("IKEA", "MALM chest of 3 drawers", 55, 60), ("IKEA", "MALM chest of 6 drawers", 85, 90),
    ("IKEA", "HEMNES chest of 8 drawers", 85, 120), ("IKEA", "BRIMNES wardrobe", 85, 90),
    ("IKEA", "ALEX desk", 55, 50), ("IKEA", "BEKANT desk", 55, 45), ("IKEA", "MALM bed frame", 85, 75),
    ("IKEA", "HEMNES day-bed", 85, 120), ("IKEA", "PAX wardrobe 100 cm", 85, 120),
    ("IKEA", "PAX wardrobe 150 cm with sliding doors", 120, 180), ("IKEA", "KIVIK sofa", 55, 40),
    ("JYSK", "Wardrobe 2 doors", 85, 90), ("JYSK", "Box spring bed", 55, 45), ("JYSK", "Dining table + 4 chairs", 85, 90),
    ("ISKU", "Office desk", 55, 50),
]


PAINS = [  # (icon, (en, fi, sv) title, (en, fi, sv) text)
    ("🔧", ["Missing tools", "Työkalut puuttuvat", "Verktyg saknas"], ["No right screwdrivers, allen keys or power tools", "Ei oikeita ruuvimeisseleitä, kuusiokoloavaimia tai sähkötyökaluja", "Inga rätta skruvmejslar, insexnycklar eller elverktyg"]),
    ("⏰", ["No time", "Ei aikaa", "Ingen tid"], ["Weekends are precious – spend them with family", "Viikonloput ovat arvokkaita – vietä ne perheen kanssa", "Helgerna är värdefulla – tillbringa dem med familjen"]),
    ("📄", ["Confusing instructions", "Sekavat ohjeet", "Förvirrande instruktioner"], ["Those diagrams make no sense", "Kuvista ei saa mitään selvää", "Ritningarna är omöjliga att förstå"]),
    ("💔", ["Fear of damage", "Pelko vahingoista", "Rädsla för skador"], ["Worried about breaking expensive furniture", "Huoli kalliiden huonekalujen rikkoutumisesta", "Orolig att förstöra dyra möbler"]),
    ("📦", ["Limited space", "Vähän tilaa", "Litet utrymme"], ["Small apartment, nowhere to spread out parts", "Pieni asunto, ei tilaa levittää osia", "Liten lägenhet, ingenstans att lägga ut delarna"]),
    ("😤", ["Relationship stress", "Riitoja kotona", "Bråk hemma"], ["Arguments with your partner over assembly", "Kokoaminen aiheuttaa kinaa kumppanin kanssa", "Gräl med partnern om monteringen"]),
]

STEPS = [  # ((en, fi, sv) title, (en, fi, sv) text)
    (["Book via WhatsApp", "Varaa WhatsAppilla", "Boka via WhatsApp"], ["Send a quick message with your furniture details. We reply within 30 minutes.", "Lähetä lyhyt viesti huonekaluista. Vastaamme 30 minuutin sisällä.", "Skicka ett kort meddelande om dina möbler. Vi svarar inom 30 minuter."]),
    (["We arrive with tools", "Tulemme työkalujen kanssa", "Vi kommer med verktyg"], ["Our team brings all equipment. You don't lift a finger.", "Tiimimme tuo kaikki välineet. Sinun ei tarvitse nostaa sormeakaan.", "Vårt team tar med all utrustning. Du behöver inte lyfta ett finger."]),
    (["Enjoy perfect furniture", "Nauti valmiista huonekaluista", "Njut av perfekta möbler"], ["Relax while we work. Perfect assembly guaranteed or your money back.", "Rentoudu kun me teemme työt. Täydellinen lopputulos tai rahat takaisin.", "Koppla av medan vi jobbar. Perfekt montering eller pengarna tillbaka."]),
]

TIMELINE = [  # (side, time, (en, fi, sv) text)
    ("diy", "9:00", ["Start reading confusing instructions", "Sekavien ohjeiden lukeminen alkaa", "Börjar läsa förvirrande instruktioner"]),
    ("diy", "10:30", ["Drive to the hardware store for missing tools", "Ajo rautakauppaan puuttuvien työkalujen takia", "Åker till järnhandeln efter verktyg"]),
    ("diy", "12:00", ["Argument with partner about step 47", "Riita kumppanin kanssa vaiheesta 47", "Gräl med partnern om steg 47"]),
    ("diy", "15:00", ["Realise you built it backwards", "Huomaat kasanneesi sen väärin päin", "Inser att den är byggd bakvänt"]),
    ("diy", "18:00", ["Weekend gone, furniture still wonky", "Viikonloppu meni, huonekalu edelleen vino", "Helgen är slut, möbeln fortfarande sned"]),
    ("us", "9:00", ["Coffee and breakfast with family", "Kahvi ja aamiainen perheen kanssa", "Kaffe och frukost med familjen"]),
    ("us", "10:00", ["SISUSETH team arrives and works", "SISUSETHin tiimi saapuu ja tekee työt", "SISUSETH-teamet kommer och jobbar"]),
    ("us", "12:00", ["Lunch at your favourite restaurant", "Lounas lempiravintolassa", "Lunch på din favoritrestaurang"]),
    ("us", "14:00", ["Perfect furniture ready to enjoy", "Täydelliset huonekalut valmiina", "Perfekta möbler klara att använda"]),
    ("us", "15:00", ["Rest of the weekend for what matters", "Loppu viikonloppu tärkeille asioille", "Resten av helgen för det som betyder något"]),
]


def tri(prefix, values):
    return {f"{prefix}_{lang}": v for lang, v in zip(("en", "fi", "sv"), values)}


def load_image(field, path):
    with open(path, "rb") as f:
        field.save(path.name, File(f), save=False)


def seed_packages():
    for i, (names, descs, price, hours, bonus, popular) in enumerate(PACKAGES):
        PricingPackage.objects.create(order=i, price_eur=price, estimated_hours=hours, referral_bonus_eur=bonus,
                                      is_popular=popular, **tri("name", names), **tri("description", descs))


def seed_calculator():
    for i, (labels, price, hourly) in enumerate(CALCULATOR):
        CalculatorOption.objects.create(order=i, price_eur=price, is_hourly=hourly, **tri("label", labels))


def seed_faq():
    for i, (qs, ans) in enumerate(FAQS):
        FAQ.objects.create(order=i, **tri("question", qs), **tri("answer", ans))


def seed_testimonials():
    for i, (author, city, quote) in enumerate(TESTIMONIALS):
        Testimonial.objects.create(order=i, author=author, city=city, quote_en=quote)


def seed_gallery():
    for i, path in enumerate(sorted((SEED_IMAGES / "gallery").glob("*.jpg"))):
        photo = GalleryImage(order=i)
        load_image(photo.image, path)
        photo.save()


def seed_products():
    Product.objects.bulk_create(Product(brand=b, name=n, price_eur=p, minutes=m) for b, n, p, m in PRODUCTS)


def seed_pains():
    for i, (icon, titles, texts) in enumerate(PAINS):
        PainPoint.objects.create(order=i, icon=icon, **tri("title", titles), **tri("text", texts))


def seed_steps():
    for i, (titles, texts) in enumerate(STEPS):
        Step.objects.create(order=i, **tri("title", titles), **tri("text", texts))


def seed_timeline():
    for i, (side, time, texts) in enumerate(TIMELINE):
        TimelineEntry.objects.create(order=i, side=side, time=time, **tri("text", texts))


def seed_site_images():
    cfg = SiteSettings.load()
    for field, filename in (("logo", "logo.jpeg"), ("hero_image", "hero.jpg")):
        if not getattr(cfg, field):  # never replace an image the owner uploaded
            load_image(getattr(cfg, field), SEED_IMAGES / filename)
    cfg.save()


# section name → (loader, model whose existing rows mean "already has content")
SECTIONS = {
    "site_images": (seed_site_images, None),
    "packages": (seed_packages, PricingPackage),
    "calculator": (seed_calculator, CalculatorOption),
    "faq": (seed_faq, FAQ),
    "testimonials": (seed_testimonials, Testimonial),
    "gallery": (seed_gallery, GalleryImage),
    "products": (seed_products, Product),
    "pains": (seed_pains, PainPoint),
    "steps": (seed_steps, Step),
    "timeline": (seed_timeline, TimelineEntry),
}


class Command(BaseCommand):
    help = "Load starting content once per section and sync UI text keys (safe on every deploy)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", nargs="+", metavar="SECTION", choices=list(SECTIONS),
                            help="Delete a section's current content and load the starting content again.")

    @transaction.atomic
    def handle(self, *args, reset=None, **options):
        cfg, _ = SiteSettings.objects.get_or_create(pk=1, defaults={
            "instagram_url": "https://www.instagram.com/sisu_seth",
            "tiktok_url": "https://www.tiktok.com/@sisu.set",
            "facebook_url": "https://www.facebook.com/share/1B33mnzcYo/",
        })
        done = set(cfg.seeded_sections)
        for name in reset or []:
            if (model := SECTIONS[name][1]) is not None:
                model.objects.all().delete()
            done.discard(name)

        loaded = []
        for name, (loader, model) in SECTIONS.items():
            if name in done:
                continue
            if model is None or not model.objects.exists():  # never mix starting content into real content
                loader()
                loaded.append(name)
            done.add(name)
        SiteSettings.objects.filter(pk=1).update(seeded_sections=sorted(done))

        added, removed = self.sync_text_blocks()
        if options.get("verbosity", 1) > 0:
            self.stdout.write(self.style.SUCCESS(
                f"Seed – loaded: {', '.join(loaded) or 'nothing new'}. Text blocks: {added} added, {removed} removed."))

    def sync_text_blocks(self):
        locales = {lang: json.loads((LOCALES_DIR / f"{lang}.json").read_text()) for lang in ("en", "fi", "sv")}
        added = 0
        for key in locales["en"]:
            _, created = TextBlock.objects.get_or_create(
                key=key, defaults={f"value_{lang}": locales[lang].get(key, "") for lang in locales}
                | {"note": key.split(".")[0].capitalize() + " section"},
            )
            added += created
        removed, _ = TextBlock.objects.exclude(key__in=locales["en"]).delete()
        return added, removed
