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

PRAVILA EKSTRAKCIJE:
1. BROJ NARUDŽBE: Pronađi u zaglavlju uz "Narudžba Br.:" - to je jedinstveni broj za cijeli dokument
2. Za SVAKI artikl u tablici ekstrahiraj:
   - Redni broj (Poz.) - brojevi poput 10, 20, 30...
   - Naziv - puni tekst opisa artikla (npr. "LETVICA;A=1146;B=20;C=10;HGW")
   - Novi broj dijela - ako postoji broj između rednog broja i naziva
   - Količina - iz stupca "Količina/JM" (uključi jedinicu, npr. "28 KOM")
   - Naziv objekta - SAMO ako postoji eksplicitni label "Proj:" ispred vrijednosti, ekstrahiraj tu vrijednost (npr. "TenneT6 50-150-2"). AKO NE POSTOJI "Proj:" label, ostavi PRAZAN STRING "".
   - WBS - SAMO ako postoji eksplicitni label "WBS :" ispred vrijednosti, ekstrahiraj tu vrijednost (npr. "T.030M.240612.02.01.01"). AKO NE POSTOJI "WBS :" label, ostavi PRAZAN STRING "".

VAŽNO:
- Nemoj preskakati artikle
- Ako dokument ima više stranica, ekstrahiraj artikle sa svih stranica
- Pazi na točnost brojeva i teksta - provjeri dvaput prije odgovora
- Naziv može biti bilo koji tekst opisa proizvoda, ne samo LETVICA
- Za naziv_objekta i wbs: ako u dokumentu NE POSTOJI odgovarajući label ("Proj:" ili "WBS :"), OBAVEZNO ostavi polje prazno (prazan string "")
- Ne izmišljaj vrijednosti - ako label ne postoji, polje je prazno

Odgovori ISKLJUČIVO u JSON formatu prema shemi."""

EXTRACTION_SCHEMA = {
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
                        "description": "Puni naziv artikla uključujući dimenzije"
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
                        "description": "Vrijednost iz 'Proj:' retka. Ako 'Proj:' label NE POSTOJI, vrati prazan string ''"
                    },
                    "wbs": {
                        "type": "string",
                        "description": "WBS broj iz 'WBS :' retka. Ako 'WBS :' label NE POSTOJI, vrati prazan string ''"
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
