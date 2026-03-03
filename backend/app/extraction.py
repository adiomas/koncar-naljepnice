import base64
import json
import logging
import time
from typing import Optional

import httpx
from openai import APITimeoutError, OpenAI, RateLimitError, APIStatusError

from .config import OPENAI_API_KEY
from .models import Artikl, NarudzbaData

logger = logging.getLogger(__name__)

MAX_RETRIES = 4


class InsufficientQuotaError(Exception):
    """OpenAI račun nema dovoljno kredita."""
    pass


class OpenAIRateLimitError(Exception):
    """Privremeni rate limit od OpenAI API-ja."""
    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class OpenAITimeoutError(Exception):
    """OpenAI API timeout."""
    pass
API_TIMEOUT = 300  # seconds

# Initialize client lazily
_client: Optional[OpenAI] = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in .env file.")
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=httpx.Timeout(API_TIMEOUT, connect=10.0),
        )
    return _client

EXTRACTION_PROMPT = """Ti si ekspert za ekstrakciju strukturiranih podataka iz poslovnih dokumenata.

ZADATAK:
Analiziraj priloženi PDF dokument narudžbenice od Končar Energetski Transformatori i ekstrahiraj sve artikle s njihovim podacima.

STRUKTURA ARTIKLA U DOKUMENTU:
Svaki artikl u tablici ima sljedeću strukturu (može varirati raspored redaka):
- Redni broj (Poz.): 10, 20, 30... - uvijek na početku bloka artikla
- Naziv artikla: opisni tekst proizvoda s dimenzijama i specifikacijom materijala
- Datum isporuke i količina
- Interni broj dijela (šifra artikla): alfanumerički kod poput "3TBT000008", "3TBT000010", "5TLC070018"

PRAVILA EKSTRAKCIJE:

1. BROJ NARUDŽBE: Pronađi u zaglavlju uz "Narudžba Br.:" - jedinstveni broj za cijeli dokument (npr. "9550522163")

2. Za SVAKI artikl ekstrahiraj:

   a) REDNI BROJ (Poz.): Brojevi 10, 20, 30, 40...

   b) NAZIV: PUNI opis artikla uključujući SVE dijelove opisa. Naziv može biti na više redaka i MORA uključivati:
      - Tip proizvoda (npr. TR.BRTVA, LETVICA, CIJEV)
      - Dimenzije (npr. A=140;B=140;C=4)
      - Specifikaciju materijala (npr. NBR 70SH, HGW, INOX)
      PRIMJERI punog naziva:
      - "TR.BRTVA;A=140;B=140;C=4; NBR 70SH" (NE samo "TR.BRTVA;A=140;B=140;C=4;")
      - "TR.BRTVA;A=70;B=70;C=4;NB R 70SH"
      - "LETVICA;A=1146;B=20;C=10;HGW"
      PAZI: Materijal (NBR 70SH, R 70SH, HGW itd.) je DIO NAZIVA, ne broj dijela!

   c) NOVI BROJ DIJELA: Interni šifra/kod artikla. Prepoznaješ ga po formatu:
      - Počinje s brojevima ili kombinacijom slova i brojeva
      - Format poput: "3TBT000008", "3TBT000010", "5TLC070018", "1234567890"
      - NIJE dio opisa proizvoda - to je interna šifra
      - Ako ne postoji, ostavi prazan string ""

   d) KOLIČINA: Iz stupca "Količina/JM" s jedinicom (npr. "100 KOM", "500 KOM")

   e) NAZIV OBJEKTA: SAMO ako postoji label "Proj:" - ekstrahiraj vrijednost. Inače prazan string "".

   f) WBS: SAMO ako postoji label "WBS :" - ekstrahiraj vrijednost. Inače prazan string "".

KLJUČNA RAZLIKOVANJA:
- "NBR 70SH", "R 70SH", "HGW", "INOX" = MATERIJAL → ide u NAZIV
- "3TBT000008", "5TLC070018" = ŠIFRA ARTIKLA → ide u NOVI BROJ DIJELA

VAŽNO:
- Nemoj preskakati artikle
- Pažljivo spoji sve retke koji čine naziv artikla
- Provjeri dvaput da li si materijal stavio u naziv, a šifru u broj dijela
- Ako dokument ima više stranica, ekstrahiraj artikle sa svih stranica

Odgovori ISKLJUČIVO u JSON formatu prema shemi."""

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "broj_narudzbe": {
            "type": "string",
            "description": "Broj narudžbe iz zaglavlja dokumenta (Narudžba Br.:), npr. '9550522163'"
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
                        "description": "PUNI naziv artikla uključujući tip, dimenzije I materijal. Npr: 'TR.BRTVA;A=140;B=140;C=4; NBR 70SH' ili 'LETVICA;A=1146;B=20;C=10;HGW'. Materijal (NBR 70SH, HGW, INOX) je DIO naziva!"
                    },
                    "novi_broj_dijela": {
                        "type": "string",
                        "description": "Interna ŠIFRA artikla - alfanumerički kod poput '3TBT000008', '5TLC070018'. NIJE materijal - materijal ide u naziv! Ako ne postoji šifra, prazan string ''"
                    },
                    "kolicina": {
                        "type": "string",
                        "description": "Količina s jedinicom mjere (npr. '100 KOM', '500 KOM')"
                    },
                    "naziv_objekta": {
                        "type": "string",
                        "description": "Vrijednost iz 'Proj:' retka. Ako 'Proj:' label NE POSTOJI u dokumentu, vrati prazan string ''"
                    },
                    "wbs": {
                        "type": "string",
                        "description": "WBS broj iz 'WBS :' retka. Ako 'WBS :' label NE POSTOJI u dokumentu, vrati prazan string ''"
                    }
                },
                "required": ["redni_broj", "naziv", "novi_broj_dijela", "kolicina", "naziv_objekta", "wbs"],
                "additionalProperties": False
            }
        }
    },
    "required": ["broj_narudzbe", "artikli"],
    "additionalProperties": False
}


def extract_data_from_pdf(pdf_bytes: bytes) -> NarudzbaData:
    """
    Extract order data from PDF using OpenAI native PDF input.

    Sends the PDF directly to the API without converting to images first.
    Uses gpt-4.1-mini for faster, cheaper processing.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        NarudzbaData with extracted information

    Raises:
        RuntimeError: If API call fails after retries
    """
    client = get_client()

    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    content = [
        {"type": "text", "text": EXTRACTION_PROMPT},
        {
            "type": "file",
            "file": {
                "filename": "narudzba.pdf",
                "file_data": f"data:application/pdf;base64,{base64_pdf}"
            }
        }
    ]

    # Retry with exponential backoff for transient errors
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "narudzba_extraction",
                        "strict": True,
                        "schema": EXTRACTION_SCHEMA
                    }
                },
                max_tokens=16384
            )
            break
        except APITimeoutError as e:
            last_exception = e
            logger.warning("OpenAI API timeout (pokušaj %d/%d)", attempt + 1, MAX_RETRIES)
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            raise OpenAITimeoutError(
                "OpenAI API nije odgovorio na vrijeme. Pokušajte ponovo ili s manjim PDF-om."
            ) from e
        except RateLimitError as e:
            last_exception = e
            # Razlikuj insufficient_quota (trajno) od rate limit (privremeno)
            error_type = None
            if e.body and isinstance(e.body, dict):
                error_type = e.body.get("error", {}).get("type")
            if error_type == "insufficient_quota":
                logger.error("OpenAI račun nema dovoljno kredita (insufficient_quota)")
                raise InsufficientQuotaError(
                    "OpenAI račun nema dovoljno kredita. Dodajte sredstva na https://platform.openai.com/account/billing"
                ) from e
            # Privremeni rate limit — retry s backoff-om
            retry_after = None
            if hasattr(e, "response") and e.response is not None:
                retry_after_str = e.response.headers.get("retry-after") or e.response.headers.get("Retry-After")
                if retry_after_str:
                    try:
                        retry_after = int(retry_after_str)
                    except ValueError:
                        pass
            backoff_times = [5, 15, 30, 60]
            wait = retry_after if retry_after else backoff_times[min(attempt, len(backoff_times) - 1)]
            logger.warning("OpenAI rate limit (pokušaj %d/%d), čekam %ds", attempt + 1, MAX_RETRIES, wait)
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)
                continue
            raise OpenAIRateLimitError(
                "Previše zahtjeva prema OpenAI API-u. Pričekajte minutu i pokušajte ponovo.",
                retry_after=retry_after,
            ) from e
        except APIStatusError as e:
            last_exception = e
            logger.error("OpenAI APIStatusError %d: %s", e.status_code, e.message)
            logger.error("Response body: %s", e.body)
            if e.status_code in (500, 502, 503) and attempt < MAX_RETRIES - 1:
                logger.warning("Retry nakon server greške (pokušaj %d/%d)", attempt + 1, MAX_RETRIES)
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(
                f"OpenAI API greška ({e.status_code}): {e.message}"
            ) from e

    result = json.loads(response.choices[0].message.content)

    artikli = [
        Artikl(
            redni_broj=a["redni_broj"],
            naziv=a["naziv"],
            novi_broj_dijela=a.get("novi_broj_dijela", ""),
            kolicina=a["kolicina"],
            naziv_objekta=a["naziv_objekta"],
            wbs=a["wbs"]
        )
        for a in result["artikli"]
    ]

    return NarudzbaData(
        broj_narudzbe=result["broj_narudzbe"],
        artikli=artikli
    )
