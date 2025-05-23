from modules.nlp_processor import NLPProcessor
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_nlp():
    """Тестирование NLP-классификатора"""
    processor = NLPProcessor()
    
    test_queries = [
        "Как получить субсидию для малого бизнеса?",
        "Нормативные акты по налогам",
        "Статистика ВВП за 2023 год",
        "",  # Пустой запрос
        "фин",  # Неполное слово
        "Какие есть программы поддержки?"
    ]
    
    print("\n=== Тестирование NLP-обработки ===")
    for query in test_queries:
        result = processor.classify_query(query)
        print(f"\nЗапрос: '{query}'")
        print("Результат:")
        print(f"- Токены: {result['tokens']}")
        print(f"- Категория: {result['category']}")
        print(f"- Тип документа: {result['doc_type']}")
        print(f"- Код запроса: {result['query_code']}")

if __name__ == "__main__":
    test_nlp()