import uvicorn
from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from transcriber import transcribe_audio, summarize_text, store_in_chroma, query_chroma

app = FastAPI()

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API routes
@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    name = os.path.basename(file.filename)
    audio_data = await file.read()
    save_path = f"Audio/uploaded_{name}"

    with open(save_path, "wb") as f:
        f.write(audio_data)

    transcript = transcribe_audio(save_path)
    summary = summarize_text(transcript)
    store_in_chroma(summary)

    return {
        "filename": name,
        "file_size": len(audio_data),
        "saved_to": save_path,
        "transcript": transcript,
        "summary": summary
    }

@app.post("/ask/")
async def ask_podcast(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"error": "No question was asked"}
    answer = query_chroma(question)
    return {"answer": answer}

# ✅ Serve frontend (AFTER routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# ✅ Launch server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
