import type { LabelData } from "../types";

interface LabelPreviewProps {
  label: LabelData;
  index: number;
}

/**
 * Calculate dynamic font size based on text length
 * @param text - The text content
 * @param maxChars - Maximum characters that fit at base font size
 * @param baseFontPx - Base font size in pixels
 * @param minFontPx - Minimum font size in pixels
 */
function calculateFontSize(
  text: string,
  maxChars: number,
  baseFontPx: number,
  minFontPx: number = 5
): number {
  if (!text || text.length <= maxChars) {
    return baseFontPx;
  }
  const ratio = maxChars / text.length;
  const newSize = baseFontPx * ratio;
  return Math.max(newSize, minFontPx);
}

/**
 * Get inline style for dynamic font sizing
 */
function getDynamicStyle(
  text: string,
  maxChars: number,
  baseFontPx: number
): React.CSSProperties {
  const fontSize = calculateFontSize(text, maxChars, baseFontPx);
  return {
    fontSize: `${fontSize}px`,
    whiteSpace: 'nowrap' as const,
    overflow: 'hidden' as const,
  };
}

export function LabelPreview({ label, index }: LabelPreviewProps) {
  // Calculate dynamic styles for each field
  // Max chars are approximate based on available width in preview
  const nazivStyle = getDynamicStyle(label.naziv, 28, 9);
  const noviBrojStyle = getDynamicStyle(label.novi_broj_dijela, 12, 9);
  const stariBrojStyle = getDynamicStyle(label.stari_broj_dijela, 8, 8);
  const kolicinaStyle = getDynamicStyle(label.kolicina, 28, 9);
  const narudzbaStyle = getDynamicStyle(label.narudzba, 12, 9);
  const accountStyle = getDynamicStyle(label.account_category, 6, 7);
  const nazivObjektaStyle = getDynamicStyle(label.naziv_objekta, 28, 9);
  const wbsStyle = getDynamicStyle(label.wbs, 30, 8);
  const datumStyle = getDynamicStyle(label.datum, 12, 9);

  return (
    <div className="bg-amber-400 rounded-lg p-3 shadow-lg w-full max-w-[280px] text-xs font-sans">
      {/* Header */}
      <div className="flex justify-between items-start pb-2 border-b border-black/30 mb-2">
        <div>
          <div className="font-bold text-sm">Končar</div>
          <div className="text-[10px] font-semibold">Energetski transformatori d.o.o.</div>
        </div>
        <div className="text-right">
          <div className="font-bold text-[10px]">QA IDENT KARTA</div>
          <div className="text-[9px]">- Dobavni dijelovi -</div>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-0.5">
        {/* Naziv */}
        <div className="flex border border-black/40">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Naziv</div>
          <div className="flex-1 p-1 font-medium" style={nazivStyle}>{label.naziv}</div>
        </div>

        {/* Novi/Stari broj dijela */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30 leading-tight">
            Novi broj<br/>dijela
          </div>
          <div className="flex-1 p-1" style={noviBrojStyle}>{label.novi_broj_dijela}</div>
          <div className="w-12 shrink-0 p-1 text-[7px] border-l border-r border-black/40 bg-amber-500/30 leading-tight">
            Stari broj<br/>dijela
          </div>
          <div className="w-10 p-1" style={stariBrojStyle}>{label.stari_broj_dijela}</div>
        </div>

        {/* Količina */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Količina</div>
          <div className="flex-1 p-1 font-medium" style={kolicinaStyle}>{label.kolicina}</div>
        </div>

        {/* Narudžba / Account */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Narudžba</div>
          <div className="flex-1 p-1 font-medium" style={narudzbaStyle}>{label.narudzba}</div>
          <div className="w-12 shrink-0 p-1 text-[6px] border-l border-r border-black/40 bg-amber-500/30 leading-tight">
            Account<br/>assign.<br/>Category
          </div>
          <div className="w-10 p-1" style={accountStyle}>{label.account_category}</div>
        </div>

        {/* Naziv objekta */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30 leading-tight">
            Naziv<br/>objekta
          </div>
          <div className="flex-1 p-1" style={nazivObjektaStyle}>{label.naziv_objekta}</div>
        </div>

        {/* WBS */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">WBS</div>
          <div className="flex-1 p-1 font-mono" style={wbsStyle}>{label.wbs}</div>
        </div>

        {/* Datum */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Datum</div>
          <div className="flex-1 p-1" style={datumStyle}>{label.datum}</div>
          <div className="w-22 border-l border-black/40"></div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center pt-2 text-[9px] font-semibold">KPT-OI-077</div>
      
      {/* Index badge */}
      <div className="absolute -top-2 -right-2 w-6 h-6 bg-zinc-800 text-white rounded-full flex items-center justify-center text-[10px] font-bold">
        {index + 1}
      </div>
    </div>
  );
}

