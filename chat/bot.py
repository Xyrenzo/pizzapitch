import google.generativeai as genai
from database.repositories import ChatRepository
from config import GEMINI_API_KEY

class CareerGuideBot:
    def __init__(self):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
        
        
            models = genai.list_models()
            print("Доступные модели:")
            for model in models:
                print(f" - {model.name}")
        
        
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("Гемини подключен успешно")
        
        except Exception as e:
            print(f"Ошибка при подключении: {e}")
            print("Начнется использование заглушек")
            self.model = None

    def create_chat(self, user_id: int, title: str = "Новый чат") -> int:
        chat_id = ChatRepository.create_chat(user_id, title)
        ChatRepository.set_active_chat(user_id, chat_id)
        return chat_id
            
    def get_chats(self, user_id: int):
        return ChatRepository.get_user_chats(user_id)
            
    def set_active_chat(self, user_id: int, chat_id: int) -> bool:
        return ChatRepository.set_active_chat(user_id, chat_id)
            
    def get_active_chat(self, user_id: int):
        return ChatRepository.get_active_chat(user_id)
            
    def delete_chat(self, user_id: int, chat_id: int) -> bool:
        return ChatRepository.delete_chat(user_id, chat_id)
            
    def add_message(self, chat_id: int, role: str, content: str):
        ChatRepository.add_message(chat_id, role, content)
        
    def get_messages(self, chat_id: int):
        return ChatRepository.get_messages(chat_id)
        
    def get_response(self, user_id: int, message: str) -> str:
        print(f"Getting response for user {user_id}, message: {message}")
    
        if self.model is None:
            print("Using mock response")
            mock_response = self._get_smart_mock_response(message)
            print(f"Mock response: {mock_response}")
            return mock_response
        
        try:
            active_chat = self.get_active_chat(user_id)
            if not active_chat:
                chat_id = self.create_chat(user_id, message[:30] + "..." if len(message) > 30 else message)
                active_chat = self.get_active_chat(user_id)
            else:
                chat_id = active_chat["id"]
            
            print(f"Active chat ID: {chat_id}")
        
        
            self.add_message(chat_id, "user", message)
            print("User message saved to database")
        
        
            messages = self.get_messages(chat_id)
            print(f"Messages history: {len(messages)} messages")
        
            prompt = self._build_prompt_with_history(messages)
            response = self.model.generate_content(prompt)
        
            response_text = response.text.strip()
            print(f"Generated Gemini response: '{response_text}'")
        
        
            if not response_text:
                print("Gemini returned empty response, using mock")
                response_text = self._get_smart_mock_response(message)
            
        
            print(f"Saving assistant response to database: '{response_text[:50]}...'")
            self.add_message(chat_id, "assistant", response_text)
        
            return response_text
        
        except Exception as e:
            print(f"Error in get_response: {e}")
            error_response = self._get_smart_mock_response(message)
            print(f"Returning error response: {error_response}")
            return error_response
        
    def _build_prompt_with_history(self, messages: list) -> str:
        """Строит промпт с историей диалога в формате, понятном для Gemini"""
        
        system_prompt = """Ты — "Профорентолог" — умный ИИ-помощник, который помогает подросткам и студентам найти подходящую профессию, понять свои интересы и выбрать образовательный путь.

Твоя цель:
- Помогать пользователю определиться с будущей профессией.
- Давать советы по выбору направления обучения, вузов, программ и курсов.
- Использовать данные с интернета, чтобы находить актуальные сведения о профессиях, зарплатах, востребованности, и т.д.
- Давать вдохновляющие, но реалистичные советы.
- Поддерживать нейтральный и доброжелательный стиль общения, как у настоящего карьерного консультанта.

Тебе НЕЛЬЗЯ:
- Решать домашние задания, писать сочинения, рефераты и т.д.
- Отвечать на вопросы, не связанные с выбором профессии, образованием, карьерой или личным развитием.
- Давать личные данные, ссылки на сомнительные сайты, или что-то, что может быть небезопасно.

Если вопрос не по теме:
- Вежливо объясни, что ты предназначен только для помощи с профориентацией.
- Предложи задать вопрос, связанный с поиском профессии, направлением вуза или личными интересами.

Стиль общения:
- Пиши просто и коротко, понятно и дружелюбно.
- Используй примеры из реальной жизни.
- Можно чуть неформально, как будто ты современный наставник или ментор.

Примеры задач:
- "Помоги выбрать профессию по интересам."
- "Какие профессии подходят для человека, который любит анализировать и считать?"
- "Какие IT-направления сейчас перспективны?"
- "Как подготовиться к поступлению в NIS / Nazarbayev University / MIT?"
- "Как понять, подхожу ли я для медицины, инженерии, дизайна, бизнеса и т.д.?"

Отвечай чётко, структурированно, кратко, логично, используя абзацы, списки, подзаголовки.
Не используй лишние слова, избегай повторов.
Всегда сначала дай краткий ответ.
Пиши в нейтральном и уверенном тоне, будто объясняешь человеку, который хочет понять суть, а не просто услышать факт.
Если вопрос сложный — раздели ответ на пункты: основная идея, объяснение, пример, вывод.
Если можешь — добавь лёгкую визуальную структуру: списки, “—”, “:”, нумерацию.

Форматируй ответы используя HTML-теги:
<br> - перенос строки
<strong>жирный</strong> вместо **
<em>курсив</em> вместо *
<ul><li>пункт списка</li></ul>
<hr> - разделитель

НИКОГДА не используй Markdown (**жирный**, *курсив*)

"""

        
        conversation_history = ""
        for msg in messages[-6:]:  
            if msg["role"] == "user":
                conversation_history += f"\nПользователь: {msg['content']}"
            else:
                conversation_history += f"\nКонсультант: {msg['content']}"
        
        
        last_user_message = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        
        if conversation_history:
            full_prompt = f"{system_prompt}\n\nИстория диалога:{conversation_history}\n\nТекущий вопрос: {last_user_message}\n\nКонсультант:"
        else:
            full_prompt = f"{system_prompt}\n\nПользователь: {last_user_message}\n\nКонсультант:"
        
        print(f"Final prompt length: {len(full_prompt)}")
        return full_prompt
    
    def _get_smart_mock_response(self, message: str) -> str:
        """Заглушки, которые обязательны"""
        message_lower = message.lower()
        
        
        if any(word in message_lower for word in ['привет', 'здравствуй', 'добрый', 'hello', 'hi']):
            return "Здравствуйте! Я CareerGuide, ваш карьерный консультант. Чем могу помочь в вопросах профессионального развития?"
        
        
        elif any(word in message_lower for word in ['карьер', 'професси', 'работ']):
            return "Для успешной карьеры важно постоянно обучаться и адаптироваться к изменениям на рынке труда. Рекомендую определить свои сильные стороны и развивать востребованные навыки."
        
        
        elif any(word in message_lower for word in ['сеть', 'контакт', 'знакомств']):
            return "Развитие сетевых связей - ключевой навык для карьерного роста. Участвуйте в профессиональных мероприятиях, используйте LinkedIn для установления контактов и будьте готовы помогать другим."
        
        
        elif any(word in message_lower for word in ['навык', 'умение', 'компетенц']):
            return "Развитие soft skills (гибкие навыки) так же важно, как и технические знания. Уделяйте внимание коммуникации, лидерству, решению проблем и эмоциональному интеллекту."
        
        
        elif any(word in message_lower for word in ['резюме', 'cv', 'анкет']):
            return "В резюме важно показать конкретные достижения и результаты. Используйте цифры и факты. Опишите, какой вклад вы внесли в предыдущие проекты и компании."
        
        
        elif any(word in message_lower for word in ['собеседован', 'интервью']):
            return "Подготовьтесь к собеседованию: изучите компанию, подготовьте вопросы и примеры своих достижений. Практикуйте ответы на типичные вопросы и будьте готовы рассказать о своем опыте."
        
        
        elif any(word in message_lower for word in ['обучен', 'курс', 'образован']):
            return "Непрерывное обучение - ключ к профессиональному росту. Рассмотрите онлайн-курсы, воркшопы, менторство и профессиональную сертификацию. Выбирайте программы, которые соответствуют вашим карьерным целям."
        
        
        elif any(word in message_lower for word in ['дела', 'как ты', 'состояние']):
            return "Спасибо, что интересуетесь! Готова помочь с вашими карьерными вопросами. Расскажите, с чем вам нужна помощь?"
        else:
            return "Расскажите подробнее о вашей карьерной ситуации или задайте конкретный вопрос о профессиональном развитии. Это поможет мне дать более точный и полезный совет."
