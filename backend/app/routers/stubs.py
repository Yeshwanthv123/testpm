from fastapi import APIRouter, HTTPException
router = APIRouter(tags=["stubs"])
@router.post("/tts")
def tts(): raise HTTPException(status_code=501, detail="Text-to-Speech not implemented.")
@router.post("/stt")
def stt(): raise HTTPException(status_code=501, detail="Speech-to-Text not implemented.")
