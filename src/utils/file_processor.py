import os
import re
from typing import Dict, Union, List, Optional, Any
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import docx
import logging
import filetype  # <-- Replaced 'magic' with 'filetype'
from io import BytesIO
import traceback

class FileProcessor:
    """
    Enhanced file processor using the 'filetype' library for robust detection
    without external dependencies on Windows.
    """
    
    def __init__(self):
        # Mapping from detected extension to the appropriate processing method
        self.file_type_map = {
            "pdf": self._process_pdf,
            "docx": self._process_docx,
            "png": self._process_image,
            "jpg": self._process_image,
            "jpeg": self._process_image,
            "txt": self._process_text,
            "pptx": self._process_pptx
        }

    def process_uploaded_file(self, file) -> Dict[str, Any]:
        """
        Process an uploaded file with comprehensive error handling.
        Args:
            file: A Streamlit UploadedFile, bytes, or file-like object.
        Returns:
            A dictionary containing the processed file data.
        """
        try:
            file_data = file.getvalue() if hasattr(file, 'getvalue') else file
            file_name = getattr(file, 'name', 'uploaded_file')
            
            # Detect file type using the new, more reliable method
            file_type = self._detect_file_type(BytesIO(file_data), file_name)
            processor = self.file_type_map.get(file_type, self._process_unknown)
            processed_data = processor(BytesIO(file_data))
            
            return {
                "name": file_name,
                "type": file_type,
                "size": f"{len(file_data) / 1024:.1f} KB",
                "status": "success",
                **processed_data
            }
            
        except Exception as e:
            logging.error(f"File processing failed: {str(e)}\n{traceback.format_exc()}")
            return {
                "name": getattr(file, 'name', 'unknown_file'),
                "status": "error",
                "error": str(e)
            }

    def _detect_file_type(self, file_obj: BytesIO, file_name: str = "") -> str:
        """Robust file type detection using 'filetype' with fallback to extension."""
        try:
            file_obj.seek(0)
            # Guess the file type from the first 261 bytes of the file
            kind = filetype.guess(file_obj)
            file_obj.seek(0)
            
            if kind is not None:
                logging.info(f"Detected file type '{kind.extension}' using filetype library.")
                return kind.extension
        except Exception as e:
            logging.warning(f"Filetype detection failed: {e}. Falling back to extension.")

        # Fallback to file extension if detection fails or is ambiguous
        if file_name:
            ext = os.path.splitext(file_name)[1][1:].lower()
            if ext in self.file_type_map:
                logging.info(f"Using file extension '{ext}' as fallback.")
                return ext
        
        return "unknown"

    def _process_pdf(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Process PDF with text extraction."""
        reader = PdfReader(file_obj)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return {
            "text": text,
            "preview": self._generate_preview(text),
        }

    def _process_docx(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Process DOCX documents."""
        doc = docx.Document(file_obj)
        text = "\n".join([para.text for para in doc.paragraphs])
        return {
            "text": text,
            "preview": self._generate_preview(text),
        }

    def _process_image(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Process images with OCR."""
        img = Image.open(file_obj)
        text = pytesseract.image_to_string(img)
        return {
            "text": text,
            "preview": self._generate_preview(text),
        }

    def _process_text(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Process plain text files."""
        text = file_obj.read().decode('utf-8', errors='replace')
        return {
            "text": text,
            "preview": self._generate_preview(text),
        }

    def _process_pptx(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Placeholder for PPTX processing."""
        return {
            "text": "[PPTX content extraction is not fully supported yet.]",
            "preview": "PowerPoint file detected. Full text extraction requires additional libraries.",
        }

    def _process_unknown(self, file_obj: BytesIO) -> Dict[str, Any]:
        """Handler for unknown file types."""
        return {
            "text": "",
            "preview": "Unsupported file type.",
        }

    def _generate_preview(self, text: str, max_len: int = 250) -> str:
        """Generate a clean preview of the text."""
        if not text:
            return "No text content could be extracted."
        clean_text = re.sub(r'\s+', ' ', text.strip())
        if len(clean_text) <= max_len:
            return clean_text
        return clean_text[:max_len] + "..."
