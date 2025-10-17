import google.generativeai as genai
from database.repositories import ChatRepository
from config import GEMINI_API_KEY

class CareerGuideBot:
    def __init__(self):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            print("Гемини подключен успешно")
            
        except Exception as e:
            print(f"Ошибка при подключении: {e}")
            print("НАчнется использование заглушек")
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
        if self.model is None:
            return self._get_smart_mock_response(message)
            
        try:
            active_chat = self.get_active_chat(user_id)
            if not active_chat:
                chat_id = self.create_chat(user_id, message[:30] + "..." if len(message) > 30 else message)
                active_chat = self.get_active_chat(user_id)
            else:
                chat_id = active_chat["id"]
                
            self.add_message(chat_id, "user", message)
            
            # Получаем историю сообщений
            messages = self.get_messages(chat_id)
            prompt = self._build_prompt_with_history(messages)
            response = self.model.generate_content(prompt)
            
            response_text = response.text.strip()
            
            # Если ответ пустой, используем ту заглушку, которая снизуу
            if not response_text:
                response_text = self._get_smart_mock_response(message)
                
            self.add_message(chat_id, "assistant", response_text)
            return response_text
            
        except Exception as e:
            print(f"Error in get_response: {e}")
            return self._get_smart_mock_response(message)
    
    def _build_prompt_with_history(self, messages: list) -> str:
        """это промт"""
        system_prompt = """Ты CareerGuide - профессиональный карьерный консультант. Твоя задача - давать полезные советы по карьере, профессиональному развитию и выбору профессии.

Отвечай кратко, дружелюбно и по делу. Будь конкретным в своих рекомендациях. Фокусируйся на практических советах.

Твои ответы должны быть:
- Краткими и информативными
- Практическими и полезными
- Дружелюбными и поддерживающими
- Сфокусированными на карьерном развитии

Ты специализируешься на:
- Профориентации и выборе профессии
- Развитии карьеры и профессиональных навыков
- Составлении резюме и подготовке к собеседованиям
- Сетевом взаимодействии и личном бренде
- Поиске работы и карьерном планировании

История диалога:"""

        # Добавляем последние 10 сообщений из историит
        conversation_history = ""
        for msg in messages[-10:]:
            if msg["role"] == "user":
                conversation_history += f"\nЧеловек: {msg['content']}"
            else:
                conversation_history += f"\nКонсультант: {msg['content']}"
        
        # Последнее сообщение пользователя
        last_user_message = messages[-1]["content"] if messages else ""
        
        full_prompt = f"{system_prompt}{conversation_history}\n\nТекущий вопрос: {last_user_message}\n\nТвой ответ:"
        
        return full_prompt
    
    def _get_smart_mock_response(self, message: str) -> str:
        """ЗАглушки, которые обязательны"""
        message_lower = message.lower()
        
        # Приветствие
        if any(word in message_lower for word in ['привет', 'здравствуй', 'добрый', 'hello', 'hi']):
            return "Здравствуйте! Я CareerGuide, ваш карьерный консультант. Чем могу помочь в вопросах профессионального развития?"
        
        # Вопросы о карьере
        elif any(word in message_lower for word in ['карьер', 'професси', 'работ']):
            return "Для успешной карьеры важно постоянно обучаться и адаптироваться к изменениям на рынке труда. Рекомендую определить свои сильные стороны и развивать востребованные навыки."
        
        # Сетевые связи
        elif any(word in message_lower for word in ['сеть', 'контакт', 'знакомств']):
            return "Развитие сетевых связей - ключевой навык для карьерного роста. Участвуйте в профессиональных мероприятиях, используйте LinkedIn для установления контактов и будьте готовы помогать другим."
        
        # Навыки
        elif any(word in message_lower for word in ['навык', 'умение', 'компетенц']):
            return "Развитие soft skills (гибкие навыки) так же важно, как и технические знания. Уделяйте внимание коммуникации, лидерству, решению проблем и эмоциональному интеллекту."
        
        # Резюме
        elif any(word in message_lower for word in ['резюме', 'cv', 'анкет']):
            return "В резюме важно показать конкретные достижения и результаты. Используйте цифры и факты. Опишите, какой вклад вы внесли в предыдущие проекты и компании."
        
        # Собеседование
        elif any(word in message_lower for word in ['собеседован', 'интервью']):
            return "Подготовьтесь к собеседованию: изучите компанию, подготовьте вопросы и примеры своих достижений. Практикуйте ответы на типичные вопросы и будьте готовы рассказать о своем опыте."
        
        # Обучение
        elif any(word in message_lower for word in ['обучен', 'курс', 'образован']):
            return "Непрерывное обучение - ключ к профессиональному росту. Рассмотрите онлайн-курсы, воркшопы, менторство и профессиональную сертификацию. Выбирайте программы, которые соответствуют вашим карьерным целям."
        
        # Дела/состояние
        elif any(word in message_lower for word in ['дела', 'как ты', 'состояние']):
            return "Спасибо, что интересуетесь! Готова помочь с вашими карьерными вопросами. Расскажите, с чем вам нужна помощь?"
        else:
            return "Расскажите подробнее о вашей карьерной ситуации или задайте конкретный вопрос о профессиональном развитии. Это поможет мне дать более точный и полезный совет."
