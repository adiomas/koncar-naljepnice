from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel


class OutputFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"  # Returns ZIP with PNG files at 300 DPI


class Artikl(BaseModel):
    redni_broj: int
    naziv: str
    novi_broj_dijela: str = ""
    stari_broj_dijela: str = ""
    kolicina: str
    naziv_objekta: str
    wbs: str


class NarudzbaData(BaseModel):
    broj_narudzbe: str
    artikli: List[Artikl]


class LabelData(BaseModel):
    naziv: str
    novi_broj_dijela: str = ""
    stari_broj_dijela: str = ""
    kolicina: str
    narudzba: str
    account_category: str = ""
    naziv_objekta: str
    wbs: str
    datum: str = ""


class GenerateLabelsRequest(BaseModel):
    labels: List[LabelData]
    format: OutputFormat = OutputFormat.PDF  # Default to PDF for backwards compatibility

