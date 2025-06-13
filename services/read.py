from fastapi import HTTPException
import logging as logger
from PyPDF2 import PdfReader
import pandas as pd
import os

def read_pdf(file_path: str) -> str:

    try:
        if not os.path.exists(file_path):
            logger.error(f"PDF file does not exist: {file_path}")
            raise HTTPException(status_code=400, detail="PDF file does not exist.")
        
        if os.path.getsize(file_path) == 0:
            logger.error("PDF file is empty.")
            raise HTTPException(status_code=400, detail="PDF file is empty.")

        logger.info(f"Reading PDF file: {file_path}")
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
        
        if not text.strip():
            logger.warning(f"No text extracted from PDF: {file_path}")
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF. It may be image-based or empty.")
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading PDF file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error reading PDF file: {str(e)}")
    

def read_csv(file_path: str) -> list[str]:
    try:
        # Validate file existence and size
        if not os.path.exists(file_path):
            logger.error(f"CSV file does not exist: {file_path}")
            raise HTTPException(status_code=400, detail="CSV file does not exist.")
        
        if os.path.getsize(file_path) == 0:
            logger.error("CSV file is empty.")
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        logger.info(f"Reading CSV file: {file_path}")

        df = pd.read_csv(file_path, encoding='utf-8')
        if df.empty:
            logger.error("CSV file parsed but contains no data.")
            raise HTTPException(status_code=400, detail="CSV file contains no data.")
        
        return df.columns.tolist()
    
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")