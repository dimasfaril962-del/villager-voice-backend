import io
import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI(title="Villager Voice Converter API")

@app.get("/")
def health():
    return {"status": "ok", "message": "Villager Voice API is running"}

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    # Prototype only: basic audio saturation, not AI voice conversion.
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(413, "Maximum upload size is 15 MB")
    try:
        audio, sr = sf.read(io.BytesIO(raw), dtype="float32", always_2d=True)
    except Exception:
        raise HTTPException(400, "Please upload a supported audio file, preferably WAV")
    if audio.shape[0] == 0:
        raise HTTPException(400, "Audio file is empty")
    if len(audio) / sr > 45:
        raise HTTPException(413, "Maximum audio duration is 45 seconds")
    output = np.tanh(np.clip(audio, -1, 1) * 1.45) / np.tanh(1.45)
    result = io.BytesIO()
    sf.write(result, output, sr, format="WAV", subtype="PCM_16")
    result.seek(0)
    return StreamingResponse(result, media_type="audio/wav",
        headers={"Content-Disposition": 'attachment; filename="villager-voice-prototype.wav"'})
