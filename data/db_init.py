from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import Config
import os
import json

Base = declarative_base()

class DocumentCategory(Base):
    __tablename__ = 'document_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

class DocumentType(Base):
    __tablename__ = 'document_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

class AccessLevel(Base):
    __tablename__ = 'access_levels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(1), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(255), nullable=False)
    type_id = Column(Integer, ForeignKey('document_types.id'))
    category_id = Column(Integer, ForeignKey('document_categories.id'))
    access_id = Column(Integer, ForeignKey('access_levels.id'))
    
    doc_type = relationship("DocumentType")
    category = relationship("DocumentCategory")
    access_level = relationship("AccessLevel")

class UserQuery(Base):
    __tablename__ = 'user_queries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    category_code = Column(String(10))
    response_text = Column(Text)
    document_id = Column(Integer, ForeignKey('documents.id'))
    
    document = relationship("Document")

def init_db():
    engine = create_engine(Config.DB_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Заполнение справочников 
    categories = [
        {"code": "FIS", "name": "Финансовая поддержка", "description": "Запросы о финансовой поддержке"},
        {"code": "LAW", "name": "Законодательство", "description": "Запросы о нормативных актах"},
        {"code": "STA", "name": "Статистика", "description": "Запросы статистической информации"},
    ]
    
    types = [
        {"code": "03", "name": "Нормативные акты", "description": "Нормативно-правовые документы"},
        {"code": "12", "name": "Статистические отчеты", "description": "Официальная статистика"},
        {"code": "07", "name": "Методические рекомендации", "description": "Рекомендации и руководства"},
    ]
    
    access_levels = [
        {"code": "A", "name": "Открытые данные", "description": "Общедоступная информация"},
        {"code": "D", "name": "Конфиденциальные", "description": "Доступ ограничен"},
    ]
    
    for cat in categories:
        session.add(DocumentCategory(**cat))
    
    for typ in types:
        session.add(DocumentType(**typ))
    
    for acc in access_levels:
        session.add(AccessLevel(**acc))
    
    # Загрузка спарсенных данных
    scraped_path = Config.DATA_DIR / "scraped_data" / "scraped_data.json"
    if scraped_path.exists():
        with open(scraped_path, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            
        for doc in scraped_data:
            doc_type = session.query(DocumentType).filter_by(code=doc['type_code']).first()
            category = session.query(DocumentCategory).filter_by(code=doc['category_code']).first()
            access = session.query(AccessLevel).filter_by(code=doc['access_code']).first()
            
            new_doc = Document(
                title=doc['title'],
                content=doc['content'],
                url=doc['url'],
                type_id=doc_type.id if doc_type else None,
                category_id=category.id if category else None,
                access_id=access.id if access else None
            )
            session.add(new_doc)
    
    session.commit()
    session.close()
    print(f"База данных успешно инициализирована с {len(scraped_data) if scraped_path.exists() else 0} документами")

if __name__ == "__main__":
    init_db()