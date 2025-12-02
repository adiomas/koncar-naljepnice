import type { LabelData } from "../types";

interface LabelPreviewProps {
  label: LabelData;
  index: number;
}

/**
 * Calculate dynamic font size based on text length.
 * Used for single-line fields that should shrink to fit.
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
 * Get inline style for single-line fields with dynamic font sizing.
 * Text won't wrap - font shrinks to fit instead.
 */
function getSingleLineStyle(
  text: string,
  maxChars: number,
  baseFontPx: number,
  minFontPx: number = 5
): React.CSSProperties {
  const fontSize = calculateFontSize(text, maxChars, baseFontPx, minFontPx);
  return {
    fontSize: `${fontSize}px`,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    lineHeight: '1.2',
  };
}

export function LabelPreview({ label, index }: LabelPreviewProps) {
  // Dynamic styles for single-line fields (all except Naziv)
  // Max chars are based on available width in preview component
  const noviBrojStyle = getSingleLineStyle(label.novi_broj_dijela, 14, 9, 5);
  const stariBrojStyle = getSingleLineStyle(label.stari_broj_dijela, 8, 8, 5);
  const kolicinaStyle = getSingleLineStyle(label.kolicina, 32, 9, 6);
  const narudzbaStyle = getSingleLineStyle(label.narudzba, 14, 9, 5);
  const accountStyle = getSingleLineStyle(label.account_category, 8, 7, 5);
  const nazivObjektaStyle = getSingleLineStyle(label.naziv_objekta, 32, 9, 5);
  const wbsStyle = getSingleLineStyle(label.wbs, 34, 8, 5);
  const datumStyle = getSingleLineStyle(label.datum, 14, 9, 6);

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
        {/* Naziv - CAN wrap to multiple lines */}
        <div className="flex border border-black/40">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Naziv</div>
          <div className="flex-1 p-1 text-[9px] font-medium leading-tight" style={{ wordBreak: 'break-word' }}>{label.naziv}</div>
        </div>

        {/* Novi/Stari broj dijela - single line */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30 leading-tight">
            Novi broj<br/>dijela
          </div>
          <div className="flex-1 p-1 font-medium" style={noviBrojStyle}>{label.novi_broj_dijela}</div>
          <div className="w-12 shrink-0 p-1 text-[7px] border-l border-r border-black/40 bg-amber-500/30 leading-tight">
            Stari broj<br/>dijela
          </div>
          <div className="w-10 p-1" style={stariBrojStyle}>{label.stari_broj_dijela}</div>
        </div>

        {/* Količina - single line */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Količina</div>
          <div className="flex-1 p-1 font-medium" style={kolicinaStyle}>{label.kolicina}</div>
        </div>

        {/* Narudžba / Account - single line */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">Narudžba</div>
          <div className="flex-1 p-1 font-medium" style={narudzbaStyle}>{label.narudzba}</div>
          <div className="w-12 shrink-0 p-1 text-[6px] border-l border-r border-black/40 bg-amber-500/30 leading-tight">
            Account<br/>assign.<br/>Category
          </div>
          <div className="w-10 p-1" style={accountStyle}>{label.account_category}</div>
        </div>

        {/* Naziv objekta - single line */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30 leading-tight">
            Naziv<br/>objekta
          </div>
          <div className="flex-1 p-1" style={nazivObjektaStyle}>{label.naziv_objekta}</div>
        </div>

        {/* WBS - single line */}
        <div className="flex border border-black/40 border-t-0">
          <div className="w-14 shrink-0 p-1 text-[8px] border-r border-black/40 bg-amber-500/30">WBS</div>
          <div className="flex-1 p-1 font-mono" style={wbsStyle}>{label.wbs}</div>
        </div>

        {/* Datum - single line */}
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

