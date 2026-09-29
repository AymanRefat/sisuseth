"""Load the initial content from the customer's prototype. Safe to re-run: only fills empty tables."""
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from content.models import FAQ, Product, CalculatorOption, GalleryImage, PricingPackage, SiteSettings, Testimonial, TextBlock

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


def tri(prefix, values):
    return {f"{prefix}_{lang}": v for lang, v in zip(("en", "fi", "sv"), values)}


class Command(BaseCommand):
    help = "Seed the database with the prototype content (only fills empty tables)."

    def handle(self, *args, **options):
        cfg, created = SiteSettings.objects.get_or_create(pk=1, defaults={
            "instagram_url": "https://www.instagram.com/sisu_seth",
            "tiktok_url": "https://www.tiktok.com/@sisu.set",
            "facebook_url": "https://www.facebook.com/share/1B33mnzcYo/",
        })
        if created:
            for field, filename in (("logo", "logo.jpeg"), ("hero_image", "hero.jpg")):
                with open(SEED_IMAGES / filename, "rb") as f:
                    getattr(cfg, field).save(filename, File(f), save=False)
            cfg.save()

        if not PricingPackage.objects.exists():
            for i, (names, descs, price, hours, bonus, popular) in enumerate(PACKAGES):
                PricingPackage.objects.create(order=i, price_eur=price, estimated_hours=hours, referral_bonus_eur=bonus,
                                              is_popular=popular, **tri("name", names), **tri("description", descs))
        if not Product.objects.exists():
            Product.objects.bulk_create(Product(brand=b, name=n, price_eur=p, minutes=m) for b, n, p, m in PRODUCTS)
        if not CalculatorOption.objects.exists():
            for i, (labels, price, hourly) in enumerate(CALCULATOR):
                CalculatorOption.objects.create(order=i, price_eur=price, is_hourly=hourly, **tri("label", labels))
        if not FAQ.objects.exists():
            for i, (qs, ans) in enumerate(FAQS):
                FAQ.objects.create(order=i, **tri("question", qs), **tri("answer", ans))
        if not Testimonial.objects.exists():
            for i, (author, city, quote) in enumerate(TESTIMONIALS):
                Testimonial.objects.create(order=i, author=author, city=city, quote_en=quote)
        if not GalleryImage.objects.exists():
            for i, path in enumerate(sorted((SEED_IMAGES / "gallery").glob("*.jpg"))):
                with open(path, "rb") as f:
                    photo = GalleryImage(order=i)
                    photo.image.save(path.name, File(f), save=False)
                    photo.save()

        # Every UI text becomes editable in the CMS, pre-filled with the bundled translations.
        locales = {lang: json.loads((LOCALES_DIR / f"{lang}.json").read_text()) for lang in ("en", "fi", "sv")}
        created = 0
        for key in locales["en"]:
            _, was_created = TextBlock.objects.get_or_create(
                key=key, defaults={f"value_{lang}": locales[lang].get(key, "") for lang in locales}
                | {"note": key.split(".")[0].capitalize() + " section"},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"Seeded content ({created} new text blocks)."))
