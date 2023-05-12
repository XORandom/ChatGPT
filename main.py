import telebot
import openai
from googletrans import Translator
import json

# from google_trans_new import google_translator

version = 1

#  Получаем токен бота из файла
with open('BOT_TOKEN.txt', mode='r') as f:
    token = f.read()
#  Получаем токен OpenAI из файла
with open('GPT_TOKEN.txt', mode='r') as f:
    gpt_token = f.read()

bot = telebot.TeleBot(token=token)
openai.api_key = gpt_token
bot.remove_webhook()
# Создаём переводчик
translator = Translator()
# translator = google_translator()
MethodGetUpdates = 'https://api.telegram.org/bot{token}/getUpdates'.format(token=token)


@bot.message_handler(commands=['start', 'stop'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Код', 'Команды', 'TLDR')
    user_markup.row('Короткие ответы', 'ML модели')
    user_markup.row('Чат-бот', 'ИИ Помощник', 'Саркастичный ИИ')
    bot.send_message(message.from_user.id, 'Hi', reply_markup=user_markup)

    msg = bot.send_message(message.from_user.id, 'Выберите режим: ')
    bot.register_next_step_handler(msg, callback_message)


# # @bot.message_handler(func=lambda _: True)
@bot.message_handler(content_types=['text'])
def callback_message(message):
    with open('log.txt', 'a+') as f:
        f.write('Mode:' + message.text + '\n')
    mode = message.text
    msg = bot.send_message(message.from_user.id, 'Введите текст: ')
    bot.register_next_step_handler(msg, text_handler, mode)


@bot.message_handler(content_types=['text'])
def text_handler(message, mode):

    with open('log.txt', 'a+') as f:
        f.write('Q:' + message.text + '\n')

    if mode == 'Короткие ответы':
        # Короткие ответы
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Q: Who is Batman?\nA: Batman is a fictional comic book character.\n\nQ: What is torsalplexity?\nA: ?\n\nQ: What is Devz9?\nA: ?\n\nQ: Who is George Lucas?\nA: George Lucas is American film director and producer famous for creating Star Wars.\n\nQ: What is the capital of California?\nA: Sacramento.\n\nQ: What orbits the Earth?\nA: The Moon.\n\nQ: Who is Fred Rickerson?\nA: ?\n\nQ: What is an atom?\nA: An atom is a tiny particle that makes up everything.\n\nQ: Who is Alvan Muntz?\nA: ?\n\nQ: What is Kozar-09?\nA: ?\n\nQ: How many moons does Mars have?\nA: Two, Phobos and Deimos.\n\nQ:" + message.text + "\nA:",
            temperature=0,
            max_tokens=600,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
    elif mode == 'TLDR':
        # TLDR
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=message.text + "\nTl;dr",
            temperature=0.7,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
        )
    elif mode == 'Саркастичный ИИ':
        # Саркастичный ИИ
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Marv is a chatbot that reluctantly answers questions with sarcastic responses:\n\nYou: How many pounds are in a kilogram?\nMarv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.\nYou: What does HTML stand for?\nMarv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\nYou: When did the first airplane fly?\nMarv: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.\nYou: What is the meaning of life?\nMarv: I’m not sure. I’ll ask my friend Google.\nYou:" + message.text,
            temperature=0.5,
            max_tokens=5000,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )

    elif mode == 'ИИ помощник':
        # ИИ помощник
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: " + message.text + "\nAI:",
            temperature=0.9,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
    elif mode == 'ML модели':
        # языковые модели
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="ML Tutor: I am a ML/AI language model tutor\nYou: What is a language model?\nML Tutor: A language model is a statistical model that describes the probability of a word given the previous words.\nYou:" + message.text + "\nML Tutor:",
            temperature=0.3,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
        )
    elif mode == 'Чат бот':
        # Чат бот
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=message.text,
            temperature=0.5,
            max_tokens=6000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
        )

    else:
        response = openai.Completion.create(
            model='text-davinci-003',  # code-davinci-002 text-davinci-003
            prompt=message.text,
            temperature=0.0,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    answer = response['choices'][0]['text']
    with open('log.txt', 'a+') as f:
        f.write('A:' + answer + '\n')
    try:
        # answer = translator.translate(message.text, dest='eng').text
        translated_reply = translator.translate(str(answer), dest='ru').text
        bot.send_message(message.chat.id, text=answer)
        bot.send_message(message.chat.id, text='/Перевод:')
        bot.send_message(message.chat.id, text=translated_reply)
    except:

        bot.send_message(message.chat.id, text='/Перевести не получилось =(')
        bot.send_message(message.chat.id, text=answer)
    print('--------------------------------')
    print(response)



bot.polling()
