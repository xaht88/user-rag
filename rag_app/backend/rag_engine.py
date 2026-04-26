# rag_app/backend/rag_engine.py
import os
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

# ChromaDB
import chromadb

# Парсинг документов
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Эмбеддинги
from sentence_transformers import SentenceTransformer

# LLM
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGEngine:
    """Движок RAG для локального использования с поддержкой кэширования и метрик"""
    
    def __init__(self, chroma_dir: str = "chroma_db", embedding_model_name: str = 'all-MiniLM-L6-v2'):
        """Инициализация движка"""
        self.chroma_dir = chroma_dir
        self.embedding_model_name = embedding_model_name
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Загрузка модели эмбеддингов
        try:
            logger.info(f"Loading embedding model: {embedding_model_name}")
            self.embedder = SentenceTransformer(embedding_model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        # Текст-сплиттер
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Кэш для поисковых запросов (key: query, value: result)
        self._search_cache: Dict[str, Any] = {}
        self._cache_max_size = 100

    def parse_pdf(self, filepath: str) -> str:
        """Парсинг PDF файла"""
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {filepath}: {e}")
            raise ValueError(f"Ошибка чтения PDF: {str(e)}")
        return text
    
    def parse_docx(self, filepath: str) -> str:
        """Парсинг DOCX файла"""
        try:
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {filepath}: {e}")
            raise ValueError(f"Ошибка чтения DOCX: {str(e)}")
    
    def parse_txt(self, filepath: str) -> str:
        """Парсинг TXT файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT {filepath}: {e}")
            raise ValueError(f"Ошибка чтения TXT: {str(e)}")
    
    def parse_file(self, filepath: str, filename: str) -> str:
        """Определение типа файла и парсинг"""
        ext = os.path.splitext(filename)[1].lower()
        
        parsers = {
            '.pdf': self.parse_pdf,
            '.docx': self.parse_docx,
            '.txt': self.parse_txt,
            '.md': self.parse_txt
        }
        
        parser = parsers.get(ext)
        if not parser:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
            
        return parser(filepath)
    
    def create_chunks(self, text: str, doc_id: str, filename: str) -> List[Dict[str, Any]]:
        """Разбиение текста на чанки и создание эмбеддингов"""
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return []
            
        embeddings = self.embedder.encode(chunks)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{doc_id}_{i}",
                "document": chunk,
                "embedding": embeddings[i].tolist(),
                "metadata": {
                    "doc_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "upload_time": datetime.now().isoformat()
                }
            })
        
        return documents
    
    def add_document(self, doc_id: str, filepath: str, filename: str) -> Dict[str, Any]:
        """Добавление документа в базу"""
        try:
            # Парсинг файла
            text = self.parse_file(filepath, filename)
            
            # Разбиение на чанки
            chunks = self.create_chunks(text, doc_id, filename)
            
            # Добавление в ChromaDB
            if chunks:
                self.collection.add(
                    documents=[c["document"] for c in chunks],
                    embeddings=[c["embedding"] for c in chunks],
                    ids=[c["id"] for c in chunks],
                    metadatas=[c["metadata"] for c in chunks]
                )
                logger.info(f"Document {doc_id} ({filename}) added: {len(chunks)} chunks.")
            else:
                logger.warning(f"No chunks created for document {doc_id}.")

            return {
                "doc_id": doc_id,
                "chunks_count": len(chunks),
                "text_length": len(text),
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Поиск релевантных чанков по запросу с кэшированием и метриками"""
        start_time = time.time()
        
        # Проверка кэша
        if query in self._search_cache:
            logger.debug("Cache hit for query")
            return self._search_cache[query]

        try:
            query_embedding = self.embedder.encode([query])[0].tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Форматирование результатов
            formatted_results = []
            if results['documents'][0]:
                for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "score": float(dist) # Cosine distance to float
                    })

            result_data = {
                "results": formatted_results,
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
            
            # Обновление кэша
            if len(self._search_cache) >= self._cache_max_size:
                # Простая очистка при переполнении (FIFO)
                self._search_cache.pop(next(iter(self._search_cache)))
            self._search_cache[query] = result_data
            
            return result_data

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"results": [], "latency_ms": round((time.time() - start_time) * 1000, 2), "error": str(e)}
    
    def delete_document(self, doc_id: str):
        """Удаление документа из базы по doc_id"""
        try:
            # Используем where filter для удаления всех чанков конкретного документа
            self.collection.delete(where={"doc_id": doc_id})
            logger.info(f"Document {doc_id} deleted.")
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику базы"""
        try:
            count = self.collection.count()
            return {"total_documents": count}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_documents": 0, "error": str(e)}


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