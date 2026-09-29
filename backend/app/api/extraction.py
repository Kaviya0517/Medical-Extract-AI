import io
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.nlp_service import extract_medical_summary

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None

router = APIRouter(prefix="/extraction", tags=["Extraction"])


@router.post("/", response_model=ExtractionResponse)
def extract(payload: ExtractionRequest):
    summary = extract_medical_summary(payload.report_text)
    return ExtractionResponse(**summary)


@router.post("/file", response_model=ExtractionResponse)
async def extract_from_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    contents = await file.read()

    text = ""
    if filename.endswith(".pdf"):
        if PdfReader is None:
            raise HTTPException(status_code=400, detail="PDF parsing library unavailable")
        try:
            reader = PdfReader(io.BytesIO(contents))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF file: {str(e)}")
    else:
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            text = contents.decode("latin-1", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in uploaded file")

    summary = extract_medical_summary(text)
    return ExtractionResponse(**summary)