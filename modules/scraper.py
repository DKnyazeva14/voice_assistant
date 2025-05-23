import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from pathlib import Path
from config import Config
import time
import re
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config

class SiteScraper:
    def __init__(self, base_url="https://economy.gov.ru/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_site(self, max_pages=50):
        """Основной метод для парсинга сайта"""
        queue = [self.base_url]
        
        while queue and len(self.data) < max_pages:
            url = queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            print(f"Обработка: {url}")
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                self.visited_urls.add(url)
                
                # Извлекаем данные со страницы
                self.extract_page_data(url, soup)
                
                # Находим новые ссылки для обработки
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    if self.is_valid_url(absolute_url):
                        queue.append(absolute_url)
                
                time.sleep(1)  # Задержка между запросами
                
            except Exception as e:
                print(f"Ошибка при обработке {url}: {str(e)}")
                continue

    def is_valid_url(self, url):
        """Проверяет, нужно ли обрабатывать URL"""
        return (url.startswith(self.base_url) and
                not any(ext in url for ext in ['.pdf', '.doc', '.xls']) and
                url not in self.visited_urls and
                re.search(r'economy\.gov\.ru/.+/', url))  # Только страницы с контентом

    def extract_page_data(self, url, soup):
        """Извлекает данные с одной страницы"""
        title = soup.title.string if soup.title else "Без названия"
        
        # Основной контент страницы (адаптируйте под структуру сайта)
        content_div = soup.find('div', class_=re.compile('content|main|text', re.I))
        if not content_div:
            return
            
        content = ' '.join(p.get_text() for p in content_div.find_all(['p', 'div']))
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) < 200:  # Пропускаем страницы с малым количеством текста
            return
            
        # Определяем категорию и тип документа (примерная логика)
        doc_category, doc_type = self.classify_document(url, title)
        
        self.data.append({
            "title": title,
            "content": content,
            "url": url,
            "type_code": doc_type,
            "category_code": doc_category,
            "access_code": "A"  # По умолчанию открытый доступ
        })

    def classify_document(self, url, title):
        """Определяет категорию и тип документа"""
        # Пример простого классификатора по ключевым словам
        category_map = [
            (r'финанс|поддержк|субсид|бюджет', "FIS"),
            (r'закон|норматив|правов|регулирован', "LAW"), 
            (r'статистик|данн|отчет|показател|ввп', "STA")
        ]
        
        type_map = [
            (r'закон|постановлени|приказ|норматив|правов', "03"),
            (r'статистик|отчет|данн|показател|анализ', "12"),
            (r'методич|рекомендац|инструкц|руководств|правил', "07")
        ]
        
        # Определяем категорию
        category = "UNK"
        for pattern, code in category_map:
            if re.search(pattern, title, re.I):
                category = code
                break
                
        # Определяем тип
        doc_type = "00"
        for pattern, code in type_map:
            if re.search(pattern, title, re.I):
                doc_type = code
                break
                
        return category, doc_type

    def save_to_json(self, filename="scraped_data.json"):
        """Сохраняет данные в JSON файл"""
        output_path = Config.DATA_DIR / "scraped_data" / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            
        print(f"Данные сохранены в {output_path}")

def run_scraper():
    scraper = SiteScraper()
    scraper.scrape_site(max_pages=20)  # Ограничим для теста
    scraper.save_to_json()
    
if __name__ == "__main__":
    run_scraper()