from fastapi import UploadFile, HTTPException
import io
from PyPDF2 import PdfReader

def extract_text_from_file(file: UploadFile) -> str:
    """Извлекает текст из загруженного файла (PDF или TXT)."""
    

    if file.content_type == "application/pdf":
        try:
            file_content = file.file.read()
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                
            if not text.strip():
                 raise ValueError("PDF не содержит извлекаемого текста.")

            return text
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Не удалось извлечь текст из PDF. Возможно, файл защищен или не содержит текста. Ошибка: {e}")


    elif file.content_type == "text/plain":
        try:
            content = file.file.read().decode("utf-8")
            return content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка при чтении TXT: {e}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый тип файла: {file.content_type}. Поддерживаются .txt и .pdf.",
        )