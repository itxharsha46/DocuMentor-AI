from fastapi import FastAPI, UploadFile, File, HTTPException, Response, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import base64
import os
import uuid
from fpdf import FPDF

# Import your custom modules
from .parsers import pdf_parser, docx_parser, txt_parser
from .core.chunker import chunk_text
from .core.embedder import embedder_instance
from .vector_store.chroma import vector_store_instance
from .core.llm import llm_instance
from .core.scheduler import scheduler, session_manager

app = FastAPI(
    title="DocuMentor AI API",
    description="API with summarization, export, and agentic features.",
    version="4.1.0-stable",
)

# --- CORS POLICY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ChatMessage(BaseModel):
    sender: str
    text: str

class QueryRequest(BaseModel):
    session_id: str
    question: str
    chat_history: List[ChatMessage] = []

class ExportRequest(BaseModel):
    chat_history: List[ChatMessage] = []

# --- HELPERS ---
def clean_text_for_pdf(text):
    """Standardize characters that break FPDF (Latin-1 limitations)."""
    if not text: return ""
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'", 
        '—': '-', '–': '-', '…': '...', '\u2022': '-'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- EVENTS ---
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(session_manager.cleanup_expired_sessions, 'interval', minutes=10)
    scheduler.start()
    print("Scheduler started and cleanup job scheduled.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("Scheduler shut down.")

# --- ROUTES ---

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "DocuMentor AI API is running"}

@app.post("/process", tags=["Document Processing"])
async def process_document(file: UploadFile = File(...)):
    try:
        session_id = vector_store_instance.create_collection()
        session_manager.register_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")
    
    content_type = file.content_type
    filename = file.filename
    extracted_text = ""
    
    if content_type == 'application/pdf': 
        extracted_text = pdf_parser.parse_pdf(file)
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or filename.endswith('.docx'): 
        extracted_text = docx_parser.parse_docx(file)
    elif content_type == 'text/plain' or filename.endswith('.txt'): 
        extracted_text = txt_parser.parse_txt(file)
    else: 
        vector_store_instance.delete_collection(session_id)
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    if "Error:" in extracted_text or not extracted_text.strip():
        vector_store_instance.delete_collection(session_id)
        raise HTTPException(status_code=400, detail="Invalid or empty document.")

    text_chunks = chunk_text(extracted_text)
    for i in range(0, len(text_chunks), 100):
        batch = text_chunks[i:i + 100]
        try:
            embeddings = await embedder_instance.embed_documents(batch)
            metadatas = [{"source": filename} for _ in batch]
            vector_store_instance.add_documents(session_id, batch, embeddings, metadatas)
        except Exception as e:
            vector_store_instance.delete_collection(session_id)
            raise HTTPException(status_code=500, detail=f"Batch processing error: {e}")

    return {"message": "Processed successfully", "session_id": session_id}

@app.post("/query", tags=["Question Answering"])
async def query_document(request: QueryRequest):
    try:
        query_embedding = await embedder_instance.embed_documents([request.question])
        context_chunks = vector_store_instance.query(request.session_id, query_embedding[0])
    except Exception as e:
        raise HTTPException(status_code=404, detail="Query error or session expired.")

    sources_b64 = base64.b64encode(json.dumps(context_chunks).encode('utf-8')).decode('utf-8')
    
    try:
        answer_generator = llm_instance.generate_answer_stream(
            question=request.question,
            context_chunks=context_chunks,
            chat_history=[msg.dict() for msg in request.chat_history]
        )
        return StreamingResponse(answer_generator, media_type="text/plain", headers={"X-Source-Chunks": sources_b64})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {e}")

@app.post("/export/pdf", tags=["Exporting"])
async def export_conversation_to_pdf(request: ExportRequest, background_tasks: BackgroundTasks):
    chat_history = [msg.dict() for msg in request.chat_history]
    
    if not chat_history:
        summary = "No conversation history to summarize."
    else:
        try:
            if hasattr(llm_instance, 'summarize_conversation'):
                summary = await llm_instance.summarize_conversation(chat_history)
                if "Error:" in summary:
                    summary = "Could not generate summary due to an AI error."
            else:
                summary = "Summary function missing in LLM module."
        except Exception as e:
            print(f"Summary Generation Failed: {e}")
            summary = "Summary generation failed."

    # --- FPDF GENERATION ---
    reports_dir = "generated_reports"
    os.makedirs(reports_dir, exist_ok=True)
    pdf_filename = f"Summary_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="DocuMentor AI - Conversation Summary", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        cleaned_summary = clean_text_for_pdf(summary)
        pdf.multi_cell(0, 10, txt=cleaned_summary)

        pdf.output(pdf_path)
        
        # Schedule deletion after sending
        background_tasks.add_task(os.remove, pdf_path)
        
        return FileResponse(
            path=pdf_path, filename="DocuMentor_Summary.pdf", media_type='application/pdf'
        )
    except Exception as e:
        print(f"PDF GENERATION FAILED: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")