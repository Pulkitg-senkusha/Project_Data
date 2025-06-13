from fastapi import APIRouter, HTTPException, UploadFile, File
from logger import logger
from pydantic import BaseModel
from services.read import read_pdf, read_csv
from services.chat import get_llama_response
import os
import shutil

router = APIRouter()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File '{filename}' uploaded successfully. Size: {os.path.getsize(file_path)} bytes")

        if filename.endswith('.csv'):
            headers = read_csv(file_path)
            return {"data": headers}
        
        elif filename.endswith('.pdf'):
            return {"text": read_pdf(file_path)}
        
        else:
            logger.warning(f"Unsupported file type: {filename}")
            raise HTTPException(status_code=400, detail="Unsupported file type. Only CSV and PDF files are allowed.")
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
class QueryInput(BaseModel):
    history: list[dict[str, str]] 
      

@router.post("/chat")
async def chat_with_llama(input_data: QueryInput):
    try:
        history = [{"role": msg["role"], "content": msg["content"]} for msg in input_data.history]

        reply = get_llama_response(history)

        return {"response": reply}
    except Exception as e:
        logger.error(f"Error in /chat route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")