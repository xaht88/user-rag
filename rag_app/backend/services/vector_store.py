from typing import List, Dict, Optional
from chromadb import PersistentClient
from chromadb.config import Settings
import uuid

class VectorStore:
    """Сервис для работы с векторной базой данных ChromaDB"""
    
    def __init__(self, persist_directory: str = "chroma_db"):
        self.client = PersistentClient(path=persist_directory)
        self.collection = None
    
    def get_collection(self, name: str) -> object:
        """Получить или создать коллекцию"""
        if self.collection is None or self.collection.name != name:
            self.collection = self.client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        return self.collection
    
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict]) -> List[str]:
        """Добавить документы в коллекцию"""
        collection = self.get_collection(collection_name)
        ids = [str(uuid.uuid4()) for _ in documents]
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return ids
    
    def search(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        """Поиск по запросу"""
        collection = self.get_collection(collection_name)
        results = collection.query(query_texts=[query], n_results=n_results)
        return list(zip(results["documents"][0], results["metadatas"][0]))
    
    def delete_collection(self, collection_name: str):
        """Удалить коллекцию"""
        self.client.delete_collection(name=collection_name)