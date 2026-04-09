from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from api.models import AnalysisResult


def _decode_data_url_image(data_url: str) -> bytes | None:
    if not data_url.startswith('data:image/'):
        return None
    marker = 'base64,'
    idx = data_url.find(marker)
    if idx == -1:
        return None
    payload = data_url[idx + len(marker):]
    try:
        return base64.b64decode(payload)
    except Exception:
        return None


def generate_forensic_report(report_path: Path, result: AnalysisResult, filename: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(report_path), pagesize=A4)
    width, height = A4

    y = height - 24 * mm
    c.setFont('Helvetica-Bold', 16)
    c.drawString(18 * mm, y, 'Spectre Forensic Report')
    y -= 8 * mm

    c.setFont('Helvetica', 9)
    c.drawString(18 * mm, y, f'Job ID: {result.job_id}')
    y -= 5 * mm
    c.drawString(18 * mm, y, f'Document: {filename}')
    y -= 5 * mm
    c.drawString(18 * mm, y, f'Verdict: {result.verdict} (confidence {result.overall_confidence:.2f})')
    y -= 8 * mm

    c.setStrokeColor(colors.HexColor('#223046'))
    c.line(18 * mm, y, width - 18 * mm, y)
    y -= 8 * mm

    c.setFont('Helvetica-Bold', 11)
    c.drawString(18 * mm, y, 'Findings')
    y -= 6 * mm
    c.setFont('Helvetica', 8)

    for finding in result.findings[:12]:
        line = (
            f"{finding.region_id} | {finding.type} | conf={finding.confidence:.2f} | "
            f"bbox=({int(finding.bbox.x)},{int(finding.bbox.y)},{int(finding.bbox.w)},{int(finding.bbox.h)})"
        )
        c.drawString(18 * mm, y, line)
        y -= 4.5 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 24 * mm
            c.setFont('Helvetica', 8)

    y -= 3 * mm
    c.setFont('Helvetica-Bold', 11)
    c.drawString(18 * mm, y, 'Timeline')
    y -= 6 * mm
    c.setFont('Helvetica', 8)
    for step in result.timeline[:10]:
        c.drawString(18 * mm, y, f"{step.order}. {step.description} ({step.timestamp_offset or 'n/a'})")
        y -= 4.5 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 24 * mm
            c.setFont('Helvetica', 8)

    if result.heatmap_url:
        img_bytes = _decode_data_url_image(result.heatmap_url)
        if img_bytes:
            c.showPage()
            c.setFont('Helvetica-Bold', 12)
            c.drawString(18 * mm, height - 20 * mm, 'Forensic Heatmap')
            image_reader = ImageReader(BytesIO(img_bytes))
            c.drawImage(image_reader, 18 * mm, 40 * mm, width=170 * mm, height=220 * mm, preserveAspectRatio=True, anchor='c')

    c.showPage()
    c.setFont('Helvetica-Bold', 11)
    c.drawString(18 * mm, height - 24 * mm, 'DNA Fingerprint')
    c.setFont('Helvetica', 8)
    c.drawString(18 * mm, height - 34 * mm, f'DNA ID: {result.dna.dna_id}')
    c.drawString(18 * mm, height - 40 * mm, f'Hash: {result.dna.hash}')
    c.drawString(18 * mm, height - 46 * mm, f'Scanner Profile: {result.dna.scanner_profile}')

    c.save()
