# Končar Naljepnice

Generator QA identifikacijskih kartica za Končar Energetski Transformatori d.o.o.

![Screenshot](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🎯 Funkcionalnosti

- 📤 Upload PDF narudžbenice (drag & drop)
- 🤖 Automatska ekstrakcija podataka pomoću OpenAI Vision API
- ✏️ Pregled i uređivanje ekstrahiranih podataka
- 🏷️ Generiranje PDF-a s naljepnicama (100×100mm)

## 🛠️ Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- OpenAI API (gpt-4o vision)
- pdf2image + Poppler
- WeasyPrint

**Frontend:**
- React 18 + TypeScript
- Vite
- TailwindCSS v4

## 🚀 Quick Start (Lokalni razvoj)

### Preduvjeti

- Python 3.11+
- Node.js 18+
- Poppler (`brew install poppler` na macOS)
- OpenAI API ključ

### Backend

```bash
cd backend

# Kreiraj virtualno okruženje
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instaliraj dependencies
pip install -r requirements.txt

# Postavi API ključ
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Pokreni server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Aplikacija: http://localhost:5173

## ☁️ Deployment

Za deployment na **Vercel** (frontend) i **Railway** (backend), pogledaj:

👉 **[DEPLOYMENT.md](./DEPLOYMENT.md)**

## 📋 API Endpoints

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| POST | `/extract` | Ekstrahira podatke iz PDF-a |
| POST | `/generate-pdf` | Generira PDF s naljepnicama |

## 📁 Struktura projekta

```
koncar-naljepnice/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── extraction.py     # OpenAI Vision
│   │   ├── pdf_processor.py  # PDF → slike
│   │   ├── label_generator.py # Generiranje naljepnica
│   │   └── models.py         # Pydantic modeli
│   ├── requirements.txt
│   ├── nixpacks.toml         # Railway config
│   └── Procfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   └── components/
│   └── package.json
└── DEPLOYMENT.md
```

## 📄 Licenca

Privatni projekt za Končar Energetski Transformatori d.o.o.
