import nltk
import re
import string
from pathlib import Path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from config import Config

# Скачиваем необходимые данные NLTK (выполняется один раз при первом запуске)
#try:
#    nltk.data.find('tokenizers/punkt')
#    nltk.data.find('corpora/stopwords')
#except LookupError:
##    nltk.download('punkt')
 #   nltk.download('stopwords')

class NLPProcessor:
    def __init__(self):
        self.stemmer = SnowballStemmer("russian")
        self.stop_words = set(stopwords.words("russian") + list(Config.STOP_WORDS))
        
        self.category_patterns = {
            "FIS": ["финанс", "поддержк", "субсид", "грант", "бюджет"],
            "LAW": ["закон", "норматив", "постановлени", "правов", "регулирован"],
            "STA": ["статистик", "данн", "отчет", "показател", "ввп", "экономик"]
        }
        
        self.type_patterns = {
            "03": ["закон", "постановлени", "приказ", "норматив", "правов"],
            "12": ["статистик", "отчет", "данн", "показател", "анализ"],
            "07": ["методич", "рекомендац", "инструкц", "руководств", "правил"]
        }

        self.synonyms = {
            "финанс": ["деньги", "бюджет", "финансирование"],
            "субсид": ["помощь", "выплата", "компенсация"]
        }
        
        def expand_with_synonyms(self, token):
            return [token] + self.synonyms.get(token, [])

    def preprocess_text(self, text):
        """Улучшенная предобработка текста"""
        text = text.lower().translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(text, language="russian")
        return [self.stemmer.stem(token) for token in tokens if token not in self.stop_words]

    def classify_query(self, query_text):
        """Улучшенная классификация с обработкой краевых случаев"""
        if not query_text or len(query_text) < 2:
            return {"tokens": [], "category": None, "doc_type": None, "query_code": None}
        tokens = self.preprocess_text(query_text)
        
         # Улучшенное определение категории с пороговым значением
        category_scores = {}
        for token in tokens:
            for category, patterns in self.category_patterns.items():
                if any(pattern in token for pattern in patterns):
                    category_scores[category] = category_scores.get(category, 0) + 1
        best_category = max(category_scores, key=category_scores.get) if category_scores and max(category_scores.values()) >= 2 else None
        
        # Автоматическое определение типа документа для категории
        doc_type = None
        if best_category == "FIS":
            doc_type = "03"  # По умолчанию для финансовых запросов - нормативные акты
        elif best_category == "LAW":
            doc_type = "03"  # Нормативные акты
        elif best_category == "STA":
            doc_type = "12"  # Статистические отчеты
            # Дополнительная проверка по ключевым словам
        type_scores = {}
        for token in tokens:
            for doc_type_code, patterns in self.type_patterns.items():
                if any(pattern in token for pattern in patterns):
                    type_scores[doc_type_code] = type_scores.get(doc_type_code, 0) + 1
        best_type = max(type_scores, key=type_scores.get) if type_scores else doc_type
        return {
            "tokens": tokens,
            "category": best_category,
            "doc_type": best_type,
            "query_code": f"{best_category}-{best_type}" if best_category and best_type else None
            }