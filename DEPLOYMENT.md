# Deployment Guide

## Arhitektura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Vercel      │────▶│     Railway     │────▶│   OpenAI API    │
│   (Frontend)    │     │   (Backend)     │     │                 │
│   React + Vite  │     │   FastAPI       │     │   gpt-4o        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 1. Backend na Railway

### Korak 1: Kreiraj Railway račun
1. Idi na https://railway.app
2. Prijavi se s GitHub računom

### Korak 2: Kreiraj novi projekt
1. Klikni **"New Project"**
2. Odaberi **"Deploy from GitHub repo"**
3. Odaberi svoj repository (`koncar-naljepnice`)
4. Railway će detektirati Python projekt

### Korak 3: Konfiguriraj deployment
Railway će automatski koristiti `nixpacks.toml` konfiguraciju.

**VAŽNO:** Postavi root directory na `backend`:
1. Idi u **Settings** → **General**
2. Pod **Root Directory** upiši: `backend`

### Korak 4: Postavi Environment Variables
U Railway dashboard-u, idi na **Variables** tab i dodaj:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | `sk-...` (tvoj OpenAI API ključ) |
| `FRONTEND_URL` | `https://tvoj-projekt.vercel.app` (dodaj nakon što deployaš frontend) |

### Korak 5: Deploy
1. Railway će automatski buildati i deployati
2. Dobit ćeš URL poput: `https://koncar-naljepnice-production.up.railway.app`
3. **Sačuvaj ovaj URL** - trebat će ti za frontend

### Testiranje
Otvori `https://tvoj-railway-url.railway.app/health` - trebao bi vratiti:
```json
{"status": "healthy"}
```

---

## 2. Frontend na Vercel

### Korak 1: Kreiraj Vercel račun
1. Idi na https://vercel.com
2. Prijavi se s GitHub računom

### Korak 2: Import projekt
1. Klikni **"Add New..."** → **"Project"**
2. Importaj svoj GitHub repository
3. Vercel će detektirati Vite projekt

### Korak 3: Konfiguriraj deployment
1. **Root Directory:** `frontend`
2. **Framework Preset:** Vite (auto-detected)
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`

### Korak 4: Postavi Environment Variables
Dodaj environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://tvoj-railway-url.railway.app` |

**VAŽNO:** Koristi Railway URL iz prethodnog koraka!

### Korak 5: Deploy
1. Klikni **"Deploy"**
2. Pričekaj build (1-2 minute)
3. Dobit ćeš URL poput: `https://koncar-naljepnice.vercel.app`

---

## 3. Završna konfiguracija

### Ažuriraj Railway CORS
1. Vrati se na Railway dashboard
2. Dodaj/ažuriraj environment variable:
   - `FRONTEND_URL` = `https://koncar-naljepnice.vercel.app`
3. Railway će automatski redeployati

---

## Troubleshooting

### "CORS error" u browseru
- Provjeri je li `FRONTEND_URL` pravilno postavljen na Railway
- URL mora biti **bez trailing slash** (bez `/` na kraju)

### "Failed to extract" error
- Provjeri je li `OPENAI_API_KEY` pravilno postavljen
- Provjeri imaš li credits na OpenAI računu

### PDF konverzija ne radi
- Railway koristi `nixpacks.toml` za instalaciju Poppler-a
- Ako ne radi, provjeri Railway build logs

---

## Cijene

### Railway
- **Hobby plan:** $5/mjesec (500 sati compute)
- **Pay-as-you-go:** ~$0.000463/min CPU

### Vercel
- **Hobby plan:** Besplatno (100GB bandwidth)
- **Pro:** $20/mjesec za timove

### OpenAI
- **gpt-4o:** ~$2.50/1M input tokens, $10/1M output tokens
- Prosječna narudžba: ~$0.05-0.10 po ekstrakciji

---

## Lokalni razvoj nakon deploymenta

Za lokalni razvoj, nastavi koristiti:

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend (u drugom terminalu)
cd frontend
npm run dev
```

Frontend će automatski koristiti `http://localhost:8000` ako `VITE_API_URL` nije postavljen.

