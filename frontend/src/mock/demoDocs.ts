export type DemoDocId = 'medical_patch' | 'financial_statement' | 'legal_contract';

const CANVAS_WIDTH = 1200;
const CANVAS_HEIGHT = 1500;

type DemoDocSpec = {
  filename: string;
  title: string;
  subtitle: string;
  marks: Array<{ x: number; y: number; w: number; h: number; label: string }>;
};

const demoDocSpecs: Record<DemoDocId, DemoDocSpec> = {
  medical_patch: {
    filename: 'medical_record_demo.png',
    title: 'MEDICAL LAB REPORT',
    subtitle: 'Patient ID: MR-29913',
    marks: [
      { x: 250, y: 360, w: 320, h: 56, label: 'Edited dosage row' },
      { x: 640, y: 685, w: 220, h: 62, label: 'Copy-paste signature' },
    ],
  },
  financial_statement: {
    filename: 'financial_statement_demo.png',
    title: 'QUARTERLY FINANCIAL SUMMARY',
    subtitle: 'Entity: Aster Holdings Ltd.',
    marks: [
      { x: 210, y: 520, w: 390, h: 66, label: 'Revenue overwrite' },
      { x: 700, y: 930, w: 260, h: 64, label: 'AI-edited footnote' },
    ],
  },
  legal_contract: {
    filename: 'legal_contract_demo.png',
    title: 'SERVICE AGREEMENT',
    subtitle: 'Case Ref: LGL-4412',
    marks: [
      { x: 210, y: 430, w: 390, h: 58, label: 'Clause replacement' },
      { x: 220, y: 830, w: 420, h: 60, label: 'Timestamp mismatch' },
    ],
  },
};

const drawBaseDocument = (ctx: CanvasRenderingContext2D, spec: DemoDocSpec): void => {
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

  ctx.strokeStyle = '#cbd5e1';
  ctx.lineWidth = 2;
  ctx.strokeRect(80, 80, CANVAS_WIDTH - 160, CANVAS_HEIGHT - 160);

  ctx.fillStyle = '#0f172a';
  ctx.font = '700 46px Arial';
  ctx.fillText(spec.title, 120, 170);

  ctx.fillStyle = '#334155';
  ctx.font = '500 26px Arial';
  ctx.fillText(spec.subtitle, 120, 220);

  ctx.strokeStyle = '#e2e8f0';
  for (let i = 0; i < 25; i += 1) {
    const y = 290 + i * 44;
    ctx.beginPath();
    ctx.moveTo(120, y);
    ctx.lineTo(CANVAS_WIDTH - 120, y);
    ctx.stroke();
  }

  ctx.fillStyle = '#1e293b';
  ctx.font = '400 20px Arial';
  for (let i = 0; i < 18; i += 1) {
    const y = 320 + i * 52;
    ctx.fillText(`Document line item ${String(i + 1).padStart(2, '0')} .................................`, 130, y);
  }
};

const drawTamperMarks = (ctx: CanvasRenderingContext2D, spec: DemoDocSpec): void => {
  spec.marks.forEach((mark) => {
    ctx.fillStyle = 'rgba(239, 68, 68, 0.14)';
    ctx.fillRect(mark.x, mark.y, mark.w, mark.h);

    ctx.strokeStyle = 'rgba(220, 38, 38, 0.9)';
    ctx.lineWidth = 2;
    ctx.strokeRect(mark.x, mark.y, mark.w, mark.h);

    ctx.fillStyle = '#7f1d1d';
    ctx.font = '600 14px Arial';
    ctx.fillText(mark.label, mark.x + 8, mark.y - 10);
  });
};

const toBlob = (canvas: HTMLCanvasElement): Promise<Blob> =>
  new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Failed to build demo document blob.'));
        return;
      }
      resolve(blob);
    }, 'image/png');
  });

export const createDemoDocumentFile = async (docId: DemoDocId): Promise<File> => {
  const spec = demoDocSpecs[docId];
  const canvas = document.createElement('canvas');
  canvas.width = CANVAS_WIDTH;
  canvas.height = CANVAS_HEIGHT;

  const ctx = canvas.getContext('2d');
  if (!ctx) {
    throw new Error('Canvas 2D context unavailable.');
  }

  drawBaseDocument(ctx, spec);
  drawTamperMarks(ctx, spec);

  const blob = await toBlob(canvas);
  return new File([blob], spec.filename, { type: 'image/png' });
};
