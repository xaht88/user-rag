from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
import asyncio

# ChromaDB
import chromadb
from chromadb.config import Settings

# Парсинг документов
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Эмбеддинги
from sentence_transformers import SentenceTransformer

# LLM
import requests


class RAGEngine:
    """Движок RAG для локального использования"""
    
    def __init__(self, chroma_dir: str = "chroma_db"):
        """Инициализация движка"""
        self.chroma_dir = chroma_dir
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Загрузка модели эмбеддингов
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Текст-сплиттер
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def parse_pdf(self, filepath: str) -> str:
        """Парсинг PDF файла"""
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise ValueError(f"Ошибка чтения PDF: {str(e)}")
        return text
    
    def parse_docx(self, filepath: str) -> str:
        """Парсинг DOCX файла"""
        try:
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Ошибка чтения DOCX: {str(e)}")
    
    def parse_txt(self, filepath: str) -> str:
        """Парсинг TXT файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Ошибка чтения TXT: {str(e)}")
    
    def parse_file(self, filepath: str, filename: str) -> str:
        """Определение типа файла и парсинг"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return self.parse_pdf(filepath)
        elif ext == '.docx':
            return self.parse_docx(filepath)
        elif ext in ['.txt', '.md']:
            return self.parse_txt(filepath)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
    
    def create_chunks(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """Разбиение текста на чанки и создание эмбеддингов"""
        chunks = self.text_splitter.split_text(text)
        embeddings = self.embedder.encode(chunks)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{doc_id}_{i}",
                "document": chunk,
                "embedding": embeddings[i].tolist(),
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        
        return documents
    
    def add_document(self, doc_id: str, filepath: str, filename: str) -> Dict[str, Any]:
        """Добавление документа в базу"""
        # Парсинг файла
        text = self.parse_file(filepath, filename)
        
        # Разбиение на чанки
        chunks = self.create_chunks(text, doc_id)
        
        # Добавление в ChromaDB
        if chunks:
            self.collection.add(
                documents=[c["document"] for c in chunks],
                embeddings=[c["embedding"] for c in chunks],
                ids=[c["id"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks]
            )
        
        return {
            "doc_id": doc_id,
            "chunks_count": len(chunks),
            "text_length": len(text)
        }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Поиск релевантных чанков по запросу"""
        query_embedding = self.embedder.encode([query])[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        return list(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ))
    
    def delete_document(self, doc_id: str):
        """Удаление документа из базы"""
        # Удаляем все чанки документа
        ids_to_delete = [f"{doc_id}_{i}" for i in range(1000)]  # Максимум 1000 чанков
        self.collection.delete(ids=ids_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику базы"""
        return {
            "total_documents": self.collection.count()
        }


class OllamaClient:
    """Клиент для работы с Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama2"  # Можно менять
    
    def generate(self, prompt: str, context: str = "") -> str:
        """Генерация ответа LLM"""
        # Формирование промпта с контекстом
        if context:
            full_prompt = f"""
            Контекст: {context}
            
            Ответьте на вопрос, используя только предоставленный контекст.
            Если информации недостаточно, скажите об этом.
            
            Вопрос: {prompt}
            """
        else:
            full_prompt = prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Ollama сервер недоступен. Убедитесь, что Ollama запущен.")
        except Exception as e:
            raise ValueError(f"Ошибка генерации LLM: {str(e)}")
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
import asyncio

# ChromaDB
import chromadb
from chromadb.config import Settings

# Парсинг документов
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Эмбеддинги
from sentence_transformers import SentenceTransformer

# LLM
import requests


class RAGEngine:
    """Движок RAG для локального использования"""
    
    def __init__(self, chroma_dir: str = "chroma_db"):
        """Инициализация движка"""
        self.chroma_dir = chroma_dir
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Загрузка модели эмбеддингов
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Текст-сплиттер
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def parse_pdf(self, filepath: str) -> str:
        """Парсинг PDF файла"""
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise ValueError(f"Ошибка чтения PDF: {str(e)}")
        return text
    
    def parse_docx(self, filepath: str) -> str:
        """Парсинг DOCX файла"""
        try:
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Ошибка чтения DOCX: {str(e)}")
    
    def parse_txt(self, filepath: str) -> str:
        """Парсинг TXT файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Ошибка чтения TXT: {str(e)}")
    
    def parse_file(self, filepath: str, filename: str) -> str:
        """Определение типа файла и парсинг"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return self.parse_pdf(filepath)
        elif ext == '.docx':
            return self.parse_docx(filepath)
        elif ext in ['.txt', '.md']:
            return self.parse_txt(filepath)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
    
    def create_chunks(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """Разбиение текста на чанки и создание эмбеддингов"""
        chunks = self.text_splitter.split_text(text)
        embeddings = self.embedder.encode(chunks)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{doc_id}_{i}",
                "document": chunk,
                "embedding": embeddings[i].tolist(),
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        
        return documents
    
    def add_document(self, doc_id: str, filepath: str, filename: str) -> Dict[str, Any]:
        """Добавление документа в базу"""
        # Парсинг файла
        text = self.parse_file(filepath, filename)
        
        # Разбиение на чанки
        chunks = self.create_chunks(text, doc_id)
        
        # Добавление в ChromaDB
        if chunks:
            self.collection.add(
                documents=[c["document"] for c in chunks],
                embeddings=[c["embedding"] for c in chunks],
                ids=[c["id"] for c in chunks],
                metadatas=[c["metadata"] for c in chunks]
            )
        
        return {
            "doc_id": doc_id,
            "chunks_count": len(chunks),
            "text_length": len(text)
        }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Поиск релевантных чанков по запросу"""
        query_embedding = self.embedder.encode([query])[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        return list(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ))
    
    def delete_document(self, doc_id: str):
        """Удаление документа из базы"""
        # Удаляем все чанки документа
        ids_to_delete = [f"{doc_id}_{i}" for i in range(1000)]  # Максимум 1000 чанков
        self.collection.delete(ids=ids_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику базы"""
        return {
            "total_documents": self.collection.count()
        }


class OllamaClient:
    """Клиент для работы с Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama2"  # Можно менять
    
    def generate(self, prompt: str, context: str = "") -> str:
        """Генерация ответа LLM"""
        # Формирование промпта с контекстом
        if context:
            full_prompt = f"""
            Контекст: {context}
            
            Ответьте на вопрос, используя только предоставленный контекст.
            Если информации недостаточно, скажите об этом.
            
            Вопрос: {prompt}
            """
        else:
            full_prompt = prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Ollama сервер недоступен. Убедитесь, что Ollama запущен.")
        except Exception as e:
            raise ValueError(f"Ошибка генерации LLM: {str(e)}")
