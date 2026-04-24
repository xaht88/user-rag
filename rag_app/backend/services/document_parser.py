from typing import List, Dict
from pypdf import PdfReader
from docx import Document
import os

class DocumentParser:
    """Парсер документов"""
    
    @staticmethod
    def parse_pdf(filepath: str) -> List[str]:
        """Парсинг PDF"""
        reader = PdfReader(filepath)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return pages
    
    @staticmethod
    def parse_docx(filepath: str) -> List[str]:
        """Парсинг DOCX"""
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return paragraphs
    
    @staticmethod
    def parse_txt(filepath: str) -> List[str]:
        """Парсинг TXT"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return [content]
    
    @staticmethod
    def parse_md(filepath: str) -> List[str]:
        """Парсинг MD"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return [content]
    
    @classmethod
    def parse(cls, filepath: str) -> List[str]:
        """Общий метод парсинга"""
        ext = os.path.splitext(filepath)[1].lower()
        parsers = {
            '.pdf': cls.parse_pdf,
            '.docx': cls.parse_docx,
            '.txt': cls.parse_txt,
            '.md': cls.parse_md
        }
        parser = parsers.get(ext)
        if not parser:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
        return parser(filepath)