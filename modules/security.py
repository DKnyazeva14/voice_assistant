from config import Config
import re

class SecurityChecker:
    @staticmethod
    def sanitize_input(input_text: str) -> str:
        """Очистка входных данных от потенциально опасных символов"""
        if not input_text:
            return ""
        
        # Удаление неразрешенных символов
        sanitized = ''.join(c for c in input_text if c in Config.ALLOWED_CHARS)
        
        # Проверка длины
        if len(sanitized) > Config.MAX_QUERY_LENGTH:
            sanitized = sanitized[:Config.MAX_QUERY_LENGTH]
        
        return sanitized.strip()
    
    @staticmethod
    def check_query_for_injection(query: str) -> bool:
        """Проверка на возможные SQL-инъекции"""
        injection_patterns = [
            r";\s*(--|#|/*)",
            r"\b(select|insert|update|delete|drop|alter|create|exec)\b",
            r"\b(union|having|group by)\b",
            r"\b(and|or)\s+[\d\w]+\s*=\s*[\d\w]+\b",
            r"'.*--",
            r"'.*;",
            r"'.*/\*"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_query(query: str) -> tuple:
        """Проверка запроса на безопасность"""
        sanitized = SecurityChecker.sanitize_input(query)
        is_injection = SecurityChecker.check_query_for_injection(sanitized)
        
        if is_injection:
            return (False, "Обнаружена попытка SQL-инъекции")
        
        if not sanitized or len(sanitized) < 3:
            return (False, "Запрос слишком короткий")
        
        return (True, sanitized)