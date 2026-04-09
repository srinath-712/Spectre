from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import sys
from typing import Callable

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from detection.orchestrator import run_detectors
from detection.registry import detector_names
from main import app


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def _make_synthetic_anomaly_image() -> np.ndarray:
    img = np.full((900, 700), 180, dtype=np.float32)
    patch = np.random.normal(90, 22, (90, 90))
    img[300:390, 120:210] = patch
    img[300:390, 350:440] = patch + np.random.normal(0, 1.2, (90, 90))
    img[380:520, 250:460] = np.random.normal(120, 55, (140, 210))
    img[:, :230] = 130
    img[:, 470:] = 210
    img[430:560, 300:470] = 172
    for row in range(0, 900, 25):
        img[row : row + 1, :] += 18
    return np.clip(img, 0, 255).astype(np.uint8)


def _png_bytes(image: np.ndarray) -> bytes:
    pil_img = Image.fromarray(image)
    buf = BytesIO()
    pil_img.save(buf, format='PNG')
    return buf.getvalue()


def _multipage_pdf_bytes() -> bytes:
    page1 = Image.new('RGB', (800, 1000), color=(222, 222, 222))
    page2 = Image.new('RGB', (800, 1000), color=(200, 208, 220))
    buf = BytesIO()
    page1.save(buf, format='PDF', save_all=True, append_images=[page2])
    return buf.getvalue()


def _low_quality_bytes() -> bytes:
    base = Image.new('L', (1200, 900), color=210)
    rotated = base.rotate(1.8, expand=True)
    tiny = rotated.resize((420, 320), Image.BILINEAR)
    blown = tiny.resize((840, 640), Image.BILINEAR)
    buf = BytesIO()
    blown.convert('RGB').save(buf, format='JPEG', quality=35)
    return buf.getvalue()


def check_detector_stack() -> CheckResult:
    run = run_detectors(_make_synthetic_anomaly_image(), domain='medical', selected_detectors=detector_names())
    types = {finding.type for finding in run.findings}
    expected = set(detector_names())
    passed = len(run.failures) == 0 and expected.issubset(types)
    return CheckResult(
        name='detector-stack',
        passed=passed,
        detail=f'findings={len(run.findings)} failures={len(run.failures)} covered={len(types)}/9',
    )


def check_api_image_flow() -> CheckResult:
    client = TestClient(app)
    payload = _png_bytes(_make_synthetic_anomaly_image())

    analyze = client.post('/api/analyze', data={'domain': 'medical'}, files={'file': ('img.png', payload, 'image/png')})
    if analyze.status_code != 200:
        return CheckResult('api-image-flow', False, f'analyze={analyze.status_code}')

    job_id = analyze.json()['job_id']
    result = client.get(f'/api/result/{job_id}')
    report = client.get(f'/api/report/{job_id}')
    adversarial = client.post('/api/adversarial', json={'job_id': job_id, 'attack_type': 'gaussian_noise'})

    ok = result.status_code == 200 and report.status_code == 200 and adversarial.status_code == 200
    detail = f'result={result.status_code} report={report.status_code} adversarial={adversarial.status_code}'
    return CheckResult('api-image-flow', ok, detail)


def check_multipage_pdf() -> CheckResult:
    client = TestClient(app)
    payload = _multipage_pdf_bytes()
    analyze = client.post('/api/analyze', data={'domain': 'legal'}, files={'file': ('multi.pdf', payload, 'application/pdf')})
    passed = analyze.status_code == 200
    return CheckResult('multipage-pdf', passed, f'analyze={analyze.status_code}')


def check_low_quality_scan() -> CheckResult:
    client = TestClient(app)
    payload = _low_quality_bytes()
    analyze = client.post('/api/analyze', data={'domain': 'financial'}, files={'file': ('lowq.jpg', payload, 'image/jpeg')})
    if analyze.status_code != 200:
        return CheckResult('low-quality-scan', False, f'analyze={analyze.status_code}')

    job_id = analyze.json()['job_id']
    result = client.get(f'/api/result/{job_id}')
    body = result.json() if result.status_code == 200 else {}
    passed = result.status_code == 200 and isinstance(body.get('findings', []), list)
    return CheckResult('low-quality-scan', passed, f'result={result.status_code} findings={len(body.get("findings", []))}')


def check_fingerprint_compare() -> CheckResult:
    client = TestClient(app)
    payload = _png_bytes(_make_synthetic_anomaly_image())

    fingerprint = client.post('/api/fingerprint', files={'file': ('a.png', payload, 'image/png')})
    if fingerprint.status_code != 200:
        return CheckResult('fingerprint-compare', False, f'fingerprint={fingerprint.status_code}')

    dna_id = fingerprint.json()['dna_id']
    compare = client.post(f'/api/compare/{dna_id}', files={'file': ('a.png', payload, 'image/png')})
    passed = compare.status_code == 200 and compare.json().get('delta') == []
    return CheckResult('fingerprint-compare', passed, f'compare={compare.status_code}')


def run_all_checks() -> list[CheckResult]:
    checks: list[Callable[[], CheckResult]] = [
        check_detector_stack,
        check_api_image_flow,
        check_multipage_pdf,
        check_low_quality_scan,
        check_fingerprint_compare,
    ]
    return [check() for check in checks]


def main() -> int:
    results = run_all_checks()

    print('Phase 5B QA Summary')
    print('--------------------')
    failed = 0
    for result in results:
        status = 'PASS' if result.passed else 'FAIL'
        print(f'[{status}] {result.name}: {result.detail}')
        if not result.passed:
            failed += 1

    if failed:
        print(f'\nOverall: FAIL ({failed} checks failed)')
        return 1

    print('\nOverall: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
