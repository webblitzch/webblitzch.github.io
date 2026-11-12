"""Erzeugt Vorschau-Websites für Webblitz-Leads aus einer gemeinsamen Vorlage."""
import html, json, pathlib, re, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
NAIL = (REPO / "vorschau/nailcosmetica-r7t2/index.html").read_text(encoding="utf-8")
# Wiederverwendbare Bausteine aus der fertigen nailcosmetica-Seite (Menü, Animationen, Galerie-Zoom)
EXTRA_CSS = NAIL[NAIL.index("/* Handy-Menü */"):NAIL.index("</style>")]
EXTRA_JS = NAIL[NAIL.index("<script>\n/* Anruf-Buttons"):NAIL.rindex("</body>")]

THEMES = {
    "coiffeur": dict(bg="#f7f6f4", surface="#ecebe7", ink="#1c1c1e", muted="#64646a", line="#dcdad4",
                     brand="#1f3a5f", soft="#d7e0ea", fonts="family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Manrope:wght@400;500;600",
                     display='"Fraunces",Georgia,serif', body='"Manrope",system-ui,sans-serif', radius="14px", arch=False),
    "kosmetik": dict(bg="#fbf8f6", surface="#f1e7e2", ink="#2a2023", muted="#6e6064", line="#e7d9d2",
                     brand="#9a4a5e", soft="#efd3da", fonts="family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600",
                     display='"Cormorant Garamond",Georgia,serif', body='"Jost",system-ui,sans-serif', radius="18px", arch=True),
    "fuss": dict(bg="#f6f8f5", surface="#e6eee6", ink="#1d2620", muted="#5f6b63", line="#d6e0d6",
                 brand="#3f6b52", soft="#d4e6da", fonts="family=Lora:ital,wght@0,500;0,600;1,500&family=Nunito+Sans:wght@400;600;700",
                 display='"Lora",Georgia,serif', body='"Nunito Sans",system-ui,sans-serif', radius="18px", arch=True),
    "maler": dict(bg="#f8f7f3", surface="#efece4", ink="#1e1e1c", muted="#5e5d58", line="#dedbd1",
                  brand="#c2410c", soft="#fbe2d4", fonts="family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600",
                  display='"Archivo",system-ui,sans-serif', body='"Inter",system-ui,sans-serif', radius="10px", arch=False),
}

SERVICES = {
    "coiffeur": [("Schneiden und Styling", "Für Damen und Herren. Wir nehmen uns Zeit für eine Beratung, damit der Schnitt zu Ihnen passt."),
                 ("Farbe und Strähnen", "Von natürlichen Nuancen bis zu kräftigen Tönen, abgestimmt auf Ihren Typ."),
                 ("Pflege", "Behandlungen und Produkte, die Ihr Haar gesund und glänzend halten.")],
    "kosmetik": [("Gesichtsbehandlung", "Reinigung, Pflege und Entspannung, abgestimmt auf Ihren Hauttyp."),
                 ("Hand- und Nagelpflege", "Gepflegte Hände und Nägel, von dezent bis auffällig."),
                 ("Beratung", "Gemeinsam finden wir die Pflege, die zu Ihnen und Ihrem Alltag passt.")],
    "fuss": [("Fusspflege", "Sorgfältige Pflege von Haut und Nägeln für gesunde, gepflegte Füsse."),
             ("Massage", "Wohltuende Behandlungen zum Entspannen und Durchatmen."),
             ("Beratung", "Tipps für die Pflege zu Hause, damit sich Ihre Füsse lange wohlfühlen.")],
    "maler": [("Innenräume", "Wände und Decken frisch gestrichen, sauber abgedeckt und termingerecht."),
              ("Fassaden", "Schutz und neuer Glanz für Ihr Haus, mit hochwertigen Farben."),
              ("Renovationen", "Von kleinen Ausbesserungen bis zur kompletten Auffrischung.")],
}

ABOUT = {
    "coiffeur": ("Willkommen im Salon", "Hier steht später ein kurzer Text über Sie, Ihr Team und das, was Ihren Salon besonders macht."),
    "kosmetik": ("Willkommen", "Hier steht später ein kurzer Text über Sie, Ihre Erfahrung und was Ihnen bei Ihrer Arbeit wichtig ist."),
    "fuss": ("Willkommen", "Hier steht später ein kurzer Text über Sie, Ihre Ausbildung und Ihre Art zu arbeiten."),
    "maler": ("Über uns", "Hier steht später ein kurzer Text über Ihren Betrieb, Ihre Erfahrung und Ihre Arbeitsweise."),
}

def tel_href(phone):
    d = re.sub(r"\D", "", phone)
    return "+41" + d[1:] if d.startswith("0") else "+" + d

def esc(s):
    return html.escape(s, quote=True)

def build(b):
    t = THEMES[b["theme"]]
    name, slug = b["name"], b["slug"]
    phone = b.get("phone")
    nav_label = "Leistungen" if b["theme"] == "maler" else "Angebot"
    about_title, about_text = ABOUT[b["theme"]]
    if b.get("owner"):
        about_title = b["owner"]
    cta = (f'<a class="btn" href="tel:{tel_href(phone)}">Termin vereinbaren</a>' if phone
           else f'<a class="btn" href="mailto:{esc(b["email"])}">Anfrage senden</a>')
    if b["theme"] == "maler":
        cta = cta.replace("Termin vereinbaren", "Offerte anfragen").replace("Anfrage senden", "Offerte anfragen")
    call = f'<a class="call" href="tel:{tel_href(phone)}">{esc(phone)}</a>' if phone else ""
    contact_lines = (f'<a href="tel:{tel_href(phone)}">{esc(phone)}</a><br>' if phone else "") + \
        f'<a href="mailto:{esc(b["email"])}">{esc(b["email"])}</a>'
    services = "".join(
        f'<div class="service"><span class="num">{"i ii iii".split()[i]}.</span><h3>{esc(h)}</h3><p>{esc(p)}</p></div>'
        for i, (h, p) in enumerate(SERVICES[b["theme"]]))
    addr_q = re.sub(r"\s+", "+", f'{b["street"]} {b["city"]}')
    hero_shape = "200px 200px 24px 24px" if t["arch"] else t["radius"]
    photo_shape = "200px 200px 18px 18px" if t["arch"] else t["radius"]
    return f'''<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(name)} – {esc(b["tagline_short"])}</title>
<meta name="description" content="{esc(name)}: {esc(b["tagline_short"])}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{t["fonts"]}&display=swap">
<style>
/* Webblitz-Vorschlag: {esc(b["theme"])} */
:root{{
  --bg:{t["bg"]}; --surface:{t["surface"]}; --ink:{t["ink"]}; --muted:{t["muted"]}; --line:{t["line"]};
  --brand:{t["brand"]}; --brand-soft:{t["soft"]}; --brand-ink:#ffffff;
  --display:{t["display"]}; --body:{t["body"]};
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.65 var(--body)}}
img{{max-width:100%;display:block}}
a{{color:inherit}}
.wrap{{max-width:1080px;margin:0 auto;padding-left:max(18px,env(safe-area-inset-left));padding-right:max(18px,env(safe-area-inset-right))}}
h1,h2,h3{{font-family:var(--display);line-height:1.08;margin:0;text-wrap:balance;font-weight:600}}
h2{{font-size:clamp(1.9rem,4.5vw,2.7rem)}}
h3{{font-size:1.3rem}}
p{{margin:0}}
.btn{{display:inline-block;background:var(--brand);color:var(--brand-ink);font-weight:600;padding:.9rem 1.5rem;border-radius:999px;text-decoration:none;letter-spacing:.01em}}
.btn.ghost{{background:transparent;color:var(--brand);border:1.5px solid var(--brand)}}
.btn:focus-visible,a:focus-visible{{outline:3px solid var(--brand);outline-offset:3px}}
header{{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
header .wrap{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:14px}}
.logo{{font:600 1.35rem/1.1 var(--display);text-decoration:none;min-width:0}}
nav{{display:flex;gap:24px;font-weight:500;font-size:.95rem}}
nav a{{text-decoration:none;color:var(--muted)}}
nav a:hover{{color:var(--ink)}}
.call{{font-weight:600;text-decoration:none;white-space:nowrap;color:var(--brand)}}
.hero .wrap{{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;padding-block:80px}}
.hero .wrap > *{{min-width:0}}
.eyebrow{{font-weight:600;letter-spacing:.16em;text-transform:uppercase;font-size:.75rem;color:var(--brand)}}
.hero h1{{font-size:clamp(2.4rem,6.5vw,4.1rem);margin-top:14px}}
.hero h1 em{{color:var(--brand)}}
.hero p.lead{{margin-top:20px;font-size:1.12rem;color:var(--muted);max-width:38ch}}
.hero .cta{{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}}
.hero-card{{background:var(--surface);border-radius:{hero_shape};padding:{"56px 28px 32px" if t["arch"] else "28px"};display:flex;flex-direction:column;gap:12px;text-align:{"center" if t["arch"] else "left"}}}
.hero-card .label{{font-size:.75rem;letter-spacing:.16em;text-transform:uppercase;color:var(--brand);font-weight:600}}
.hero-card p{{color:var(--muted)}}
.hero-card b{{display:block;font:600 1.5rem/1.2 var(--display);color:var(--ink)}}
section{{padding-block:76px}}
.head{{display:flex;flex-direction:column;gap:10px;margin-bottom:36px;max-width:48ch}}
.head p{{color:var(--muted)}}
.services{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.service{{background:#fff;border:1px solid var(--line);border-radius:{t["radius"]};padding:28px;display:flex;flex-direction:column;gap:10px}}
.service p{{color:var(--muted);font-size:.97rem}}
.service .num{{font:italic 500 1.05rem/1 var(--display);color:var(--brand)}}
.about{{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}}
.about > *{{min-width:0}}
.about p{{color:var(--muted);margin-top:16px}}
.photo{{aspect-ratio:4/5;border-radius:{photo_shape};background:linear-gradient(160deg,var(--brand-soft),var(--surface));display:grid;place-items:center;color:var(--muted);font-size:.9rem;text-align:center;padding:24px}}
.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.gallery .photo{{aspect-ratio:1;border-radius:16px}}
.contact{{background:var(--surface)}}
.contact-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}}
.contact-grid > div{{display:flex;flex-direction:column;gap:6px;min-width:0;overflow-wrap:anywhere}}
.contact-grid .label{{font-size:.75rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--brand)}}
.map-link{{margin-top:6px;font-weight:600;color:var(--brand)}}
footer{{padding-block:28px;font-size:.85rem;color:var(--muted);border-top:1px solid var(--line)}}
footer .wrap{{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px}}
.preview-bar{{background:#1f2326;color:#eef0f2;font-size:.85rem;text-align:center;padding:8px 16px}}
.preview-bar a{{color:#ffd76a}}
@media (max-width:860px){{
  nav{{display:none}}
  .hero .wrap,.about{{grid-template-columns:1fr}}
  .services,.contact-grid{{grid-template-columns:1fr}}
  .gallery{{grid-template-columns:repeat(2,1fr)}}
  .hero .wrap{{padding-block:52px}}
  section{{padding-block:56px}}
}}
{EXTRA_CSS}</style>
</head>
<body>
<div class="preview-bar">Unverbindlicher Vorschlag von <a href="https://webblitzch.github.io">Webblitz</a> – nur zur Ansicht</div>

<header>
  <div class="wrap">
    <a class="logo" href="#">{esc(name)}</a>
    <nav><a href="#angebot">{nav_label}</a><a href="#ueber-uns">Über uns</a><a href="#kontakt">Kontakt</a></nav>
    {call}
  </div>
</header>

<div class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow">{esc(b["eyebrow"])}</span>
      <h1>{b["headline"]}</h1>
      <p class="lead">{esc(b["lead"])}</p>
      <div class="cta">
        {cta}
        <a class="btn ghost" href="#angebot">{nav_label} ansehen</a>
      </div>
    </div>
    <div class="hero-card">
      <span class="label">Termine</span>
      <b>nach Vereinbarung</b>
      <p>Per {"Telefon oder " if phone else ""}E-Mail.<br>Öffnungszeiten folgen hier.</p>
    </div>
  </div>
</div>

<section id="angebot">
  <div class="wrap">
    <div class="head">
      <h2>{"Unsere Leistungen" if b["theme"] == "maler" else "Angebot"}</h2>
      <p>Hier stehen später Ihre {"Arbeiten" if b["theme"] == "maler" else "Behandlungen"} und Preise. Diese Beispiele passen wir gerne an Ihr Angebot an.</p>
    </div>
    <div class="services">{services}</div>
  </div>
</section>

<section id="ueber-uns" style="padding-top:0">
  <div class="wrap about">
    <div class="photo">Hier kommt ein Foto von Ihnen oder Ihrem {"Betrieb" if b["theme"] == "maler" else "Studio"}</div>
    <div>
      <h2>{esc(about_title)}</h2>
      <p>{esc(about_text)}</p>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="head"><h2>Einblicke</h2><p>Platz für Fotos Ihrer schönsten Arbeiten.</p></div>
    <div class="gallery">
      <div class="photo">Foto 1</div><div class="photo">Foto 2</div><div class="photo">Foto 3</div>
    </div>
  </div>
</section>

<section class="contact" id="kontakt">
  <div class="wrap">
    <div class="head"><h2>Kontakt</h2></div>
    <div class="contact-grid">
      <div>
        <span class="label">Adresse</span>
        <p>{esc(name)}<br>{esc(b["street"])}<br>{esc(b["city"])}</p>
        <a class="map-link" href="https://maps.google.com/?q={esc(addr_q)}" target="_blank" rel="noopener">Route planen</a>
      </div>
      <div>
        <span class="label">{"Telefon und E-Mail" if phone else "E-Mail"}</span>
        <p>{contact_lines}</p>
      </div>
      <div>
        <span class="label">Termine</span>
        <p>Nach Vereinbarung</p>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <span>© 2026 {esc(name)} · {esc(b["street"])}, {esc(b["city"])}</span>
    <span>Impressum und Datenschutz</span>
  </div>
</footer>
{EXTRA_JS}</body>
</html>
'''

if __name__ == "__main__":
    leads = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    for b in leads:
        out = REPO / "vorschau" / b["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(b), encoding="utf-8")
        print("ok", b["slug"])
