# Prompt za AI Sustav Generiranja Naljepnica

## 📋 KONTEKST PROJEKTA

Razvijam sustav za automatsko generiranje QA identifikacijskih naljepnica za tvrtku **Končar Energetski Transformatori d.o.o.** Sustav treba ekstrahirati podatke iz PDF narudžbenica i generirati printabilne naljepnice u formatu **100mm × 100mm**.

---

## 🎯 CILJ

Kreirati end-to-end rješenje koje:
1. Prima PDF narudžbenicu kao ulaz
2. Konvertira PDF stranice u slike za AI obradu
3. Ekstrahira strukturirane podatke pomoću OpenAI Vision API-ja
4. Generira naljepnice identičnog izgleda kao referentna slika
5. Omogućuje jednostavan ispis naljepnica

---

## 📄 STRUKTURA ULAZNOG DOKUMENTA

### Opis dokumenta
- **Tip:** PDF narudžbenica od Končar Energetski Transformatori
- **Format:** Višestranični dokument s tablicom artikala
- **Jezik:** Hrvatski


### Ključni elementi za ekstrakciju

| Polje na naljepnici | Lokacija u PDF-u | Primjer vrijednosti |
|---------------------|------------------|---------------------|
| **Naziv** | Opis artikla - naziv proizvoda s dimenzijama | `LETVICA;A=1146;B=20;C=10;HGW` |
| **Novi broj dijela** | Lijevo od naziva, iza rednog broja (10, 20, 30...) | Obično prazan ili broj ako postoji |
| **Stari broj dijela** | Ako postoji, u blizini novog broja | - |
| **Količina** | Stupac "Količina/JM" | `28 KOM`, `72 KOM`, `48 KOM` |
| **Narudžba** | Zaglavlje dokumenta - "Narudžba Br.:" | `9550521558` |
| **Account assign. Category** | - | Ostaviti prazno |
| **Naziv objekta** | Redak s oznakom "Proj:" za svaki artikl | `TenneT6 50-150-2` |
| **WBS** | Redak s oznakom "WBS :" za svaki artikl | `T.030M.240612.02.01.01` |
| **Datum** | - | Ostaviti prazno za ručni unos |

### Struktura tablice artikala
```
Poz. Robe | [Novi broj dijela] | Naziv artikla (LETVICA;A=...;B=...;C=...;materijal)
          | Datum isporuke     | Količina/JM | Cijena/JM | Ukup.cijena EUR
          | Proj: [Naziv objekta]
          | WBS : [WBS broj]
          | Neto vrijednost
```

---

## 🏷️ SPECIFIKACIJA NALJEPNICE

### Fizičke dimenzije
- **Širina:** 100mm
- **Visina:** 100mm
- **Pozadina:** Žuta (#FFD700 ili slična)

### Vizualni layout (od vrha prema dnu)

```
┌────────────────────────────────────────────────────────────┐
│  Končar                              QA IDENT KARTA        │
│  Energetski transformatori d.o.o.    - Dobavni dijelovi -  │
├────────────────────────────────────────────────────────────┤
│  Naziv     │ [vrijednost]                                  │
├────────────┼───────────────────────┬───────────────────────┤
│  Novi broj │                       │ Stari broj            │
│  dijela    │ [vrijednost]          │ dijela    [vrijednost]│
├────────────┼───────────────────────┴───────────────────────┤
│  Količina  │ [vrijednost]                                  │
├────────────┼───────────────────────┬───────────────────────┤
│  Narudžba  │ [vrijednost]          │ Account   │           │
│            │                       │ assign.   │           │
│            │                       │ Category  │           │
├────────────┼───────────────────────┴───────────────────────┤
│  Naziv     │                                               │
│  objekta   │ [vrijednost]                                  │
├────────────┼───────────────────────────────────────────────┤
│  WBS       │ [vrijednost]                                  │
├────────────┼───────────────────────┬───────────────────────┤
│  Datum     │                       │                       │
├────────────┴───────────────────────┴───────────────────────┤
│                        KPT-OI-077                          │
└────────────────────────────────────────────────────────────┘
```

### Tipografija
- **Zaglavlje (Končar):** Bold, veći font
- **QA IDENT KARTA:** Bold, uppercase
- **Labele polja:** Regular weight, lijevo poravnato
- **Vrijednosti:** Regular ili bold, ovisno o polju
- **KPT-OI-077:** Centered, footer

---

## 🔧 TEHNIČKA IMPLEMENTACIJA

### Preporučeni pristup: OpenAI Vision + Structured Outputs

#### 1. PDF → Slike konverzija
```
Koristi: pdf2image, PyMuPDF, ili sličnu biblioteku
Rezolucija: 300 DPI (za jasnoću teksta)
Format: PNG ili JPEG
```

#### 2. AI Ekstrakcija (OpenAI Vision API)

**Model:** `gpt-4o` ili `gpt-4o-mini` (vision-capable)

**JSON Schema za Structured Output:**
```json
{
  "type": "object",
  "properties": {
    "broj_narudzbe": {
      "type": "string",
      "description": "Broj narudžbe iz zaglavlja dokumenta (Narudžba Br.:)"
    },
    "artikli": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "redni_broj": {
            "type": "integer",
            "description": "Pozicija artikla (10, 20, 30...)"
          },
          "naziv": {
            "type": "string",
            "description": "Puni naziv artikla uključujući dimenzije (npr. LETVICA;A=1146;B=20;C=10;HGW)"
          },
          "novi_broj_dijela": {
            "type": "string",
            "description": "Novi broj dijela ako postoji, inače prazan string"
          },
          "kolicina": {
            "type": "string",
            "description": "Količina s jedinicom mjere (npr. 28 KOM)"
          },
          "naziv_objekta": {
            "type": "string",
            "description": "Vrijednost iz 'Proj:' retka"
          },
          "wbs": {
            "type": "string",
            "description": "WBS broj iz 'WBS :' retka"
          }
        },
        "required": ["redni_broj", "naziv", "kolicina", "naziv_objekta", "wbs"],
        "additionalProperties": false
      }
    }
  },
  "required": ["broj_narudzbe", "artikli"],
  "additionalProperties": false
}
```

**System Prompt za ekstrakciju:**
```
Ti si ekspert za ekstrakciju strukturiranih podataka iz poslovnih dokumenata.

ZADATAK:
Analiziraj priloženu sliku narudžbenice od Končar Energetski Transformatori i ekstrahiraj sve artikle s njihovim podacima.

PRAVILA EKSTRAKCIJE:
1. BROJ NARUDŽBE: Pronađi u zaglavlju uz "Narudžba Br.:" - to je jedinstveni broj za cijeli dokument
2. Za SVAKI artikl u tablici ekstrahiraj:
   - Redni broj (Poz.) - brojevi poput 10, 20, 30...
   - Naziv - puni tekst opisa artikla (npr. "LETVICA;A=1146;B=20;C=10;HGW")
   - Novi broj dijela - ako postoji broj između rednog broja i naziva
   - Količina - iz stupca "Količina/JM" (uključi jedinicu, npr. "28 KOM")
   - Naziv objekta - vrijednost nakon "Proj:" (npr. "TenneT6 50-150-2")
   - WBS - vrijednost nakon "WBS :" (npr. "T.030M.240612.02.01.01")

VAŽNO:
- Svaki artikl ima svoj redak s "Proj:" i "WBS :" vrijednostima
- Nemoj preskakati artikle
- Ako dokument ima više stranica, ekstrahiraj artikle sa svih stranica
- Pazi na točnost brojeva i teksta - provijeri dvaput prije odgovora
```

#### 3. Generiranje naljepnica

**Opcije za generiranje:**
- **HTML/CSS → PDF:** Koristi puppeteer, weasyprint, ili wkhtmltopdf
- **Python ReportLab:** Direktno PDF generiranje
- **Docx template:** python-docx za Word format (kompatibilno s postojećim workflow-om)

---

## 🛠️ ARHITEKTURA RJEŠENJA

### Opcija A: Mini Web Aplikacija (PREPORUČENO)

**Prednosti:**
- Korisničko sučelje za upload i pregled
- Vizualni pregled prije ispisa
- Mogućnost korekcije ekstrahiranih podataka
- Skalabilno i proširivo

**Tech stack:**
```
Frontend: React/Vue/Svelte + TailwindCSS
Backend: Python (FastAPI) ili Node.js (Express)
PDF procesiranje: pdf2image + PyMuPDF
AI: OpenAI API (gpt-4o s vision)
Generiranje naljepnica: WeasyPrint ili Puppeteer
```

**Workflow:**
```
1. Korisnik uploada PDF
2. Backend konvertira stranice u slike
3. Slike se šalju OpenAI Vision API-ju
4. Strukturirani podaci se vraćaju i prikazuju
5. Korisnik može pregledati/urediti podatke
6. Generiranje PDF-a s naljepnicama
7. Download/ispis
```

### Opcija B: n8n Workflow

**Prednosti:**
- Brža implementacija
- Visual workflow builder
- Manje koda za održavati

**Nedostaci:**
- Manje fleksibilno za UI/UX
- Teže debugiranje
- Ovisnost o n8n platformi

**n8n Nodes:**
```
1. Webhook (prima PDF)
2. HTTP Request (PDF → Image API)
3. OpenAI Node (Vision + Structured Output)
4. Code Node (transformacija podataka)
5. HTTP Request (generiranje PDF-a) ili Template Node
6. Respond to Webhook (vraća PDF)
```

---

## 📊 OČEKIVANI OUTPUT

Za svaki artikl iz narudžbe, sustav generira jednu naljepnicu:

**Primjer za artikl #10:**
```
Naziv:          LETVICA;A=1146;B=20;C=10;HGW
Novi broj dijela: [prazno]
Stari broj dijela: [prazno]
Količina:       28 KOM
Narudžba:       9550521558
Account assign. Category: [prazno]
Naziv objekta:  TenneT6 50-150-2
WBS:            T.030M.240612.02.01.01
Datum:          [prazno - za ručni unos]
```

---

## ✅ KRITERIJI USPJEŠNOSTI

1. **Točnost ekstrakcije:** >98% točno ekstrahiranih polja
2. **Vizualna identičnost:** Naljepnice moraju izgledati identično referentnoj slici
3. **Printabilnost:** PDF format spreman za ispis na 100×100mm naljepnice
4. **Brzina:** Obrada dokumenta od 2-3 stranice < 30 sekundi
5. **Jednostavnost:** Minimalan broj koraka za korisnika

---

## 🚀 SLJEDEĆI KORACI

1. Potvrdi razumijevanje zahtjeva
2. Predloži optimalnu arhitekturu (web app ili n8n)
3. Definiraj tech stack
4. Kreiraj MVP s osnovnom funkcionalnošću
5. Testiraj s priloženim primjerima
6. Iteriraj i optimiziraj

---

## 📎 PRILOŽENI MATERIJALI

1. **Primjer narudžbenice (PDF/slike)** - 2 stranice s artiklima
2. **Referentna naljepnica** - žuta QA IDENT KARTA (100×100mm)

---

*Napomena: Ovaj prompt je strukturiran prema OpenAI best practices za Vision API i Structured Outputs, osiguravajući optimalnu ekstrakciju podataka i konzistentnost outputa.*

