import type { LabelData } from "../types";

interface LabelEditorProps {
  label: LabelData;
  index: number;
  onChange: (index: number, field: keyof LabelData, value: string) => void;
}

export function LabelEditor({ label, index, onChange }: LabelEditorProps) {
  const fields: { key: keyof LabelData; label: string }[] = [
    { key: 'naziv', label: 'Naziv' },
    { key: 'novi_broj_dijela', label: 'Novi broj dijela' },
    { key: 'stari_broj_dijela', label: 'Stari broj dijela' },
    { key: 'kolicina', label: 'Količina' },
    { key: 'narudzba', label: 'Narudžba' },
    { key: 'account_category', label: 'Account assign. Category' },
    { key: 'naziv_objekta', label: 'Naziv objekta' },
    { key: 'wbs', label: 'WBS' },
    { key: 'datum', label: 'Datum' },
  ];

  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-4 space-y-3">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-6 h-6 bg-amber-400 text-zinc-900 rounded-full flex items-center justify-center text-xs font-bold">
          {index + 1}
        </span>
        <span className="font-medium text-zinc-700 truncate">{label.naziv || 'Nova naljepnica'}</span>
      </div>
      
      <div className="grid gap-3">
        {fields.map(({ key, label: fieldLabel }) => (
          <div key={key} className="grid gap-1">
            <label className="text-xs font-medium text-zinc-500">{fieldLabel}</label>
            <input
              type="text"
              value={label[key]}
              onChange={(e) => onChange(index, key, e.target.value)}
              className="w-full px-3 py-2 text-sm border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400 transition-all"
              placeholder={`Unesite ${fieldLabel.toLowerCase()}`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}






