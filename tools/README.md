# Werkzeuge

`gen_previews.py` baut Vorschau-Websites aus einer JSON-Liste:

    python3 tools/gen_previews.py tools/meine-leads.json

Jeder Eintrag: slug, name, theme (coiffeur | kosmetik | fuss | maler), email, optional phone und owner,
street, city, eyebrow, headline (darf <em> enthalten), lead, tagline_short.
Ergebnis: vorschau/<slug>/index.html. Format-Beispiel: beispiel-leads.json.
