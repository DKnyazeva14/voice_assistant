from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.db_init import Document, DocumentCategory, DocumentType, AccessLevel, UserQuery
from config import Config
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.DB_URL)
        self.Session = sessionmaker(bind=self.engine)
    
    def search_documents(self, query_tokens, category_code=None, doc_type_code=None):
        session = self.Session()
        try:
            query = session.query(Document).filter(Document.access_id == 1)
            if category_code:
                query = query.join(DocumentCategory).filter(DocumentCategory.code == category_code)
            if doc_type_code:
                query = query.join(DocumentType).filter(DocumentType.code == doc_type_code)
            # Улучшенный поиск по токенам
            conditions = []
            for token in query_tokens:
                conditions.append(Document.content.ilike(f"%{token}%"))
                conditions.append(Document.title.ilike(f"%{token}%"))
                if conditions:
                    query = query.filter(or_(*conditions))
            # Ранжирование результатов
            documents = query.all()
            scored_docs = []
            for doc in documents:
                score = 0
                content = doc.content.lower()
                title = doc.title.lower()
                for token in query_tokens:
                    score += content.count(token) * 3  # Больший вес содержанию
                    score += title.count(token) * 5    # Максимальный вес заголовку
                    if score > 0:
                        scored_docs.append({
                            "id": doc.id,
                            "title": doc.title,
                            "content": doc.content,
                            "url": doc.url,
                            "score": score
                            })
                        
            return sorted(scored_docs, key=lambda x: x["score"], reverse=True)[:5]  # Топ-5 результатов
        finally:
            session.close()
    
    def log_query(self, query_text: str, category_code: str, response_text: str, document_id: int = None):
        session = self.Session()
        
        try:
            new_query = UserQuery(
                query_text=query_text,
                category_code=category_code,
                response_text=response_text,
                document_id=document_id
            )
            session.add(new_query)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        session = self.Session()
        
        try:
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                return {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "url": doc.url,
                    "category": doc.category.code,
                    "type": doc.doc_type.code,
                    "access": doc.access_level.code
                }
            return None
        finally:
            session.close()