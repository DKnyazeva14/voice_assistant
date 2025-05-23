# Временный скрипт check_db.py
from modules.database import DatabaseManager
db = DatabaseManager()
docs = db.search_documents([], None, None)
print(f"Найдено документов: {len(docs)}")
for doc in docs[:3]:
    print(doc['title'])