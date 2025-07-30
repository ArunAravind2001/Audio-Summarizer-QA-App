import whisper
from transformers import T5Tokenizer, T5ForConditionalGeneration
import chromadb
from chromadb.config import Settings
import ollama

# 🔧 Define the system prompt template
SYSTEM_PROMPT = """You are a helpful assistant that answers user questions based strictly on the summary of a podcast.

Here is the summary of the podcast:

---
{summary}
---

Your task is to:
- Answer questions using only the information in the summary above.
- If the answer cannot be found in the summary, reply with: "Sorry, I couldn't find that information in the summary."
- Keep responses clear and concise.
"""

# 🔧 Setup ChromaDB
chroma_client = chromadb.PersistentClient(path="C:/Users/Arun/poddcast summarizer/vd")
collection = chroma_client.get_or_create_collection(name="podcast_knowledge")

# 🔧 Load Whisper + T5
whisper_model = whisper.load_model("base")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")

# 🎙️ Transcribe audio
def transcribe_audio(audio_path: str) -> str:
    result = whisper_model.transcribe(audio_path)
    return result["text"]

# 📝 Summarize the transcript
def summarize_text(text):
    inputs = t5_tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = t5_model.generate(inputs, max_length=80, min_length=10, length_penalty=2.0, num_beams=4)
    summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# 🧠 Store summary in ChromaDB
def store_in_chroma(summary: str, doc_id: str = "podcast-001"):
    chroma_client.delete_collection("podcast_knowledge")  # clear old data
    collection = chroma_client.get_or_create_collection(name="podcast_knowledge")
    collection.add(
        documents=[summary],
        ids=[doc_id],
        metadatas=[{"source": "transcribed_podcast"}]
    )
    return "Stored in ChromaDB"

# ❓ Ask a question about the podcast summary using Mistral via Ollama
def query_chroma(question: str):
    # ⛏️ Get the stored summary
    collection = chroma_client.get_or_create_collection(name="podcast_knowledge")
    results = collection.get(ids=["podcast-001"])
    summary = results["documents"][0] if results and results["documents"] else ""

    # 🧠 Format messages
    system_msg = SYSTEM_PROMPT.format(summary=summary)
    response = ollama.chat(
        model="mistral:7b",
        options={"num_gpu": 0},  # ✅ Force CPU usage
        messages=[
        {"role": "system", "content": system_msg.strip()},
        {"role": "user", "content": question.strip()}
    ]
        )
    return response['message']['content']
