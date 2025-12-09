import base64
import json
from typing import List, Optional

from openai import OpenAI

from .config import OPENAI_API_KEY
from .models import Artikl, NarudzbaData

# Initialize client lazily
_client: Optional[OpenAI] = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in .env file.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client

EXTRACTION_PROMPT = """Ti si ekspert za ekstrakciju strukturiranih podataka iz poslovnih dokumenata.

ZADATAK:
Analiziraj priloženu sliku narudžbenice od Končar Energetski Transformatori i ekstrahiraj sve artikle s njihovim podacima.

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


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def extract_data_from_images(images: List[bytes]) -> NarudzbaData:
    """
    Extract order data from PDF page images using OpenAI Vision API.
    
    Args:
        images: List of image bytes (one per PDF page)
    
    Returns:
        NarudzbaData with extracted information
    """
    client = get_client()
    
    # Build content with all images
    content = [{"type": "text", "text": EXTRACTION_PROMPT}]
    
    for img_bytes in images:
        base64_image = encode_image_to_base64(img_bytes)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}",
                "detail": "high"
            }
        })
    
    response = client.chat.completions.create(
        model="gpt-4o",
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
        max_tokens=4096
    )
    
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
