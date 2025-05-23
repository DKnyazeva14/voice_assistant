import speech_recognition as sr
import pyttsx3
from config import Config
import os
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import time
import atexit

class VoiceIO:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.engine = None

        self._temp_files = []
        atexit.register(self._cleanup_temp_files)
    
    def _cleanup_temp_files(self):
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete temp file {file_path}: {e}")
        
        if Config.VOICE_ENABLED:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', Config.VOICE_RATE)
                self.engine.setProperty('volume', Config.VOICE_VOLUME)
            except Exception as e:
                print(f"Ошибка инициализации синтезатора речи: {e}")
                self.engine = None
    
    def listen(self) -> str:
        """Запись голоса с микрофона и преобразование в текст"""
        with sr.Microphone() as source:
            print("Слушаю...")
            audio = self.recognizer.listen(source)
        
        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Распознано: {text}")
            return text
        except sr.UnknownValueError:
            print("Речь не распознана")
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return ""
    
    def speak(self, text: str):
        """Озвучивание текста"""
        if not Config.VOICE_ENABLED or not self.engine:
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Ошибка синтеза речи: {e}")
    
    def play_notification_sound(self, sound_type: str = "start"):
        """Воспроизведение звукового уведомления"""
        sound_path = os.path.join(Config.BASE_DIR, "static", "sounds", f"{sound_type}.mp3")
        
        if os.path.exists(sound_path):
            try:
                sound = AudioSegment.from_mp3(sound_path)
                play(sound)
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")

class MockVoiceIO(VoiceIO):
    """Заглушка для тестирования без микрофона"""
    def listen(self) -> str:
        return input("Введите текст запроса: ")