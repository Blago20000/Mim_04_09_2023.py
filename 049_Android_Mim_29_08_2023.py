import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from PIL import Image
import io
import random
from bs4 import BeautifulSoup
from chatterbot import ChatBot
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from pymystem3 import Mystem
import string
import wikipediaapi

# Загрузка объекта Wikipedia.
wiki_wiki = wikipediaapi.Wikipedia(language="ru", extract_format=wikipediaapi.ExtractFormat.WIKI, user_agent="my-wikipedia-bot/1.0")

# Создание экземпляра чат-бота.
chatbot = ChatBot('МиМ-психолог')

# Создание экземпляра анализатора морфологии.
mystem = Mystem()

# Определение исходных размеров окна и размеров картинки с учетом увеличения высоты окна чата.
initial_window_width = 450  # Изменено на 450 пикселей по требованию пользователя.
initial_window_height = 1000  # Изменено на 1000 пикселей по требованию пользователя.

window_width = int(initial_window_width * 1)  # Установлено на 100% по требованию пользователя.
window_height = int(initial_window_height * 1)  # Установлено на 100% по требованию пользователя.

# Список URL ссылок на изображения.
image_urls = [
    "https://raw.githubusercontent.com/Blago20000/Mim_15_08_2023/main/001_Mime.png",
    "https://raw.githubusercontent.com/Blago20000/Mim_15_08_2023/main/002_Mime.png",
    "https://raw.githubusercontent.com/Blago20000/Mim_15_08_2023/main/003_Mime.png"
    # Добавьте остальные ссылки на изображения по аналогии.
]

# Функция для получения случайной картинки по URL ссылке и ее отображения на экране.
def get_random_image():
    image_url = random.choice(image_urls)
    return AsyncImage(source=image_url)

# Функция для получения краткой информации из Wikipedia.
def get_wikipedia_summary(keyword):
    page = wiki_wiki.page(keyword)
    
    if page.exists():
        summary = page.summary.split(".")[0] + "."  # Ограничиваем ответ одним предложением.
        return summary
    else:
        return None

# Переменная для хранения wiki_response.
wiki_response = None

class ChatBotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        Window.size = (initial_window_width, initial_window_height)
        Window.top = (Window.system_size[1] - initial_window_height) / 2
        Window.left = (Window.system_size[0] - initial_window_width) / 2

        self.chat_label = Label(text="МиМ-психолог", font_size=16)
        layout.add_widget(self.chat_label)
        
        self.image_label = get_random_image()
        self.image_label.size_hint_y=None 
        self.image_label.height=Window.size[1]/2 
        layout.add_widget(self.image_label)
        
        with self.image_label.canvas.before:
            Color(rgb=(1, 1, 1))
            self.image_rect = Rectangle(size=self.image_label.size, pos=self.image_label.pos)
        self.image_label.bind(pos=self.update_image_rect, size=self.update_image_rect)
        
        # Определение высоты строки текста.
        font_size = 12
        line_height = int(font_size * Label().line_height)
        
        # Установка размера окна ответов бота равным 250 пикселям с белым фоном.
        self.chat_window = ScrollView(size_hint=(1, None), height=250)
        self.chat_text = TextInput(text='', readonly=True, background_color=(1,1,1,1))
        self.chat_window.add_widget(self.chat_text)
        layout.add_widget(self.chat_window)
        
        self.input_label = Label(text="Введите сообщение:", font_size=12)
        layout.add_widget(self.input_label)
        
        self.input_entry = TextInput(multiline=False)
        layout.add_widget(self.input_entry)
        
        self.send_button = Button(text="Отправить", font_size=14, bold=True)
        self.send_button.bind(on_press=self.send_message)
        layout.add_widget(self.send_button)

        self.clear_button = Button(text="Очистить", font_size=12)
        self.clear_button.bind(on_press=self.clear_chat)
        layout.add_widget(self.clear_button)

        self.exit_button = Button(text="Пока!", font_size=12)
        self.exit_button.bind(on_press=self.exit_program)
        layout.add_widget(self.exit_button)
        
        with layout.canvas.before:
            Color(rgb=(184/255, 198/255, 217/255))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(pos=self.update_rect, size=self.update_rect)

        # Активация моргания курсора при запуске программы.
        self.input_entry.focus = True

        return layout
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def update_image_rect(self, instance, value):
        self.image_rect.pos = instance.pos
        self.image_rect.size = (instance.size[0], instance.size[1] * 1.1) # Добавлен просвет белого цвета высотой 10% от высоты изображения.
    
    # Функция для отправки сообщения чат-боту и получения ответа.
    def send_message(self, instance):
        global wiki_response

        user_input = self.input_entry.text

        # Проверка на наличие определенных ключевых слов или фраз в запросе пользователя.
        if "дела" in user_input.lower():
            bot_response = "У меня все хорошо, спасибо, что спросили! А как у вас дела?"
        elif "счастлив" in user_input.lower():
            bot_response = "Я программа, поэтому не могу испытывать эмоции. Но я всегда готов помочь вам!"
        elif "смерть" in user_input.lower():
            bot_responses = [
                        "Я.",
                        "Ты.",
                        "Он.",
                        "Она."
                    ]
            bot_response = random.choice(bot_responses)
        else:
            if len(user_input.split()) == 1:
                summary = get_wikipedia_summary(user_input)
                if summary:
                    bot_response = f"🧠 {summary}"
                else:
                    bot_responses = [
                        "Пожалуйста, введите вопрос или сообщение.",
                        "К сожалению, я не понял вашего вопроса.",
                        "К сожалению, вы странно сформулировали вопрос.",
                        "К сожалению, ваш вопрос не имеет смысла."
                    ]
                    bot_response = random.choice(bot_responses)
            else:
                bot_response = chatbot.get_response(user_input).text

        self.input_entry.text = ''
        self.chat_text.text += f"Вы: {user_input}\nМиМ: {bot_response}\n\n"
        self.image_label.source = get_random_image().source
    
    # Функция для очистки окна диалога.
    def clear_chat(self, instance):
        self.chat_text.text = ''
    
    # Функция для завершения программы.
    def exit_program(self, instance):
        App.get_running_app().stop()

ChatBotApp().run()
