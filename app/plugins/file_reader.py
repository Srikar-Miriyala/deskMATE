import os
from PyPDF2 import PdfReader

class FileReaderPlugin:
    """Plugin for reading PDF and TXT files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt']
    
    def read_file(self, file_path: str) -> dict:
        """Read text from PDF or TXT files"""
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in self.supported_formats:
            return {"success": False, "error": f"Unsupported file format: {file_extension}. Supported: PDF, TXT"}
        
        try:
            if file_extension == '.pdf':
                return self._read_pdf(file_path)
            elif file_extension == '.txt':
                return self._read_txt(file_path)
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}
    
    def _read_pdf(self, file_path: str) -> dict:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        return {
            "success": True,
            "content": text.strip(),
            "file_type": "PDF",
            "page_count": len(reader.pages)
        }
    
    def _read_txt(self, file_path: str) -> dict:
        """Read text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        
        return {
            "success": True,
            "content": content,
            "file_type": "TXT"
        }
    
    def summarize_text(self, text: str, style: str = "short") -> dict:
        """Create a summary of the text"""
        if not text or not text.strip():
            return {"success": False, "error": "No text provided for summarization"}
        
        words = text.split()
        if len(words) <= 100:
            summary = text
        else:
            if style == "short":
                summary = " ".join(words[:50]) + "..."
            else:
                summary = " ".join(words[:150]) + "..."
        
        return {
            "success": True,
            "summary": summary,
            "original_length": len(words),
            "summary_length": len(summary.split())
        }