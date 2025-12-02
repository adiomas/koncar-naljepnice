export interface Artikl {
  redni_broj: number;
  naziv: string;
  novi_broj_dijela: string;
  stari_broj_dijela?: string;
  kolicina: string;
  naziv_objekta: string;
  wbs: string;
}

export interface NarudzbaData {
  broj_narudzbe: string;
  artikli: Artikl[];
}

export interface LabelData {
  naziv: string;
  novi_broj_dijela: string;
  stari_broj_dijela: string;
  kolicina: string;
  narudzba: string;
  account_category: string;
  naziv_objekta: string;
  wbs: string;
  datum: string;
}

