from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.models import CompareResponse, FingerprintResponse
from output.dna import build_dna_id, hash_payload

router = APIRouter()


@router.post("/fingerprint", response_model=FingerprintResponse)
async def fingerprint_document(file: UploadFile = File(...)) -> FingerprintResponse:
    if not (file.content_type == "application/pdf" or str(file.content_type).startswith("image/")):
        raise HTTPException(status_code=415, detail="Only PDF and image uploads are supported.")

    payload = await file.read()
    digest = hash_payload(payload)
    return FingerprintResponse(dna_id=build_dna_id(digest), hash=digest)


@router.post("/compare/{dna_id}", response_model=CompareResponse)
async def compare_document(dna_id: str, file: UploadFile = File(...)) -> CompareResponse:
    if not (file.content_type == "application/pdf" or str(file.content_type).startswith("image/")):
        raise HTTPException(status_code=415, detail="Only PDF and image uploads are supported.")

    payload = await file.read()
    digest = hash_payload(payload)

    if dna_id.endswith(digest[:8].upper()):
        return CompareResponse(delta=[], changed_regions=[])

    return CompareResponse(
        delta=["Global hash mismatch detected"],
        changed_regions=["r001", "r002"],
    )
