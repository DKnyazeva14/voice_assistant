
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from modules.voice_io import VoiceIO
from modules.nlp_processor import NLPProcessor
from modules.database import DatabaseManager
from modules.security import SecurityChecker
from config import Config
from pydub import AudioSegment
import os
import logging
import tempfile
import speech_recognition as sr
from pathlib import Path


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Инициализация компонентов
nlp = NLPProcessor()
db = DatabaseManager()
voice_io = VoiceIO()

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    # Воспроизведение приветственного звука
    voice_io.play_notification_sound("start")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница с интерфейсом помощника"""
    return templates.TemplateResponse("index.html", {"request": request})

async def process_text_query(query_text: str):
    """Обработка текстового запроса"""
    # Проверка безопасности
    is_valid, validation_result = SecurityChecker.validate_query(query_text)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_result)
    
    query_text = validation_result
    
    # NLP-обработка
    nlp_result = nlp.classify_query(query_text)
    logger.info(f"NLP результат: {nlp_result}")
    
    # Поиск в базе данных
    search_results = db.search_documents(
        nlp_result["tokens"],
        nlp_result["category"],
        nlp_result["doc_type"]
    )
    
    # Формирование ответа
    if not search_results:
        response = {
            "text": "К сожалению, я не нашел информации по вашему запросу.",
            "document": None,
            "query_code": nlp_result.get("query_code")
        }
    else:
        best_match = search_results[0]
        response = {
            "text": f"По вашему запросу найдено: {best_match['title']}\n\n{best_match['content'][:500]}...",
            "document": {
                "id": best_match["id"],
                "title": best_match["title"],
                "url": best_match["url"]
            },
            "query_code": nlp_result.get("query_code")
        }
    
    # Логирование запроса
    db.log_query(
        query_text=query_text,
        category_code=nlp_result.get("category", "UNK"),
        response_text=response["text"],
        document_id=response["document"]["id"] if response["document"] else None
    )
    
    return response


@app.post("/process_voice")
async def process_voice(audio_data: UploadFile = File(...)):
    try:
        # Конвертация и обработка аудио
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio = AudioSegment.from_file(audio_data.file)
            audio.set_channels(1).set_frame_rate(16000).export(tmp.name, format="wav")
            
            with sr.AudioFile(tmp.name) as source:
                audio_data = voice_io.recognizer.record(source)
                try:
                    query_text = voice_io.recognizer.recognize_google(audio_data, language="ru-RU")
                    logger.info(f"Распознанный текст: {query_text}")
                    
                    # Улучшенная обработка NLP
                    nlp_result = nlp.classify_query(query_text)
                    logger.info(f"NLP результат: {nlp_result}")
                    
                    if not nlp_result['tokens']:
                        raise HTTPException(400, detail="Не удалось определить тему запроса")
                    
                    # Поиск с учетом морфологии
                    search_results = db.search_documents(
                        nlp_result["tokens"],
                        nlp_result["category"],
                        nlp_result["doc_type"]
                    )
                    
                    if not search_results:
                        return JSONResponse({
                            "text": "По вашему запросу ничего не найдено. Уточните вопрос.",
                            "document": None
                        })
                    
                    best_match = search_results[0]
                    return JSONResponse({
                        "text": f"Найдено: {best_match['title']}\n{best_match['content'][:300]}...",
                        "document": {
                            "id": best_match["id"],
                            "title": best_match["title"],
                            "url": best_match["url"]
                        }
                    })
                    
                except sr.UnknownValueError:
                    raise HTTPException(400, detail="Не удалось распознать речь")
                except sr.RequestError as e:
                    raise HTTPException(500, detail=f"Ошибка сервиса распознавания: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Внутренняя ошибка сервера")
    
@app.get("/toggle_voice", response_class=JSONResponse)
async def toggle_voice(enable: bool = True):
    """Переключение голосовой озвучки"""
    Config.VOICE_ENABLED = enable
    return {"status": "success", "voice_enabled": enable}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)