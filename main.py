import telebot
import openai
import json

# from google_trans_new import google_translator

version = 3

#  Получаем токен бота из файла
with open('BOT_TOKEN.txt', mode='r') as f:
    token = f.read()
#  Получаем токен OpenAI из файла
with open('GPT_TOKEN.txt', mode='r') as f:
    gpt_token = f.read()
bot = telebot.TeleBot(token=token)
openai.api_key = gpt_token


bot.remove_webhook()
MethodGetUpdates = 'https://api.telegram.org/bot{token}/getUpdates'.format(token=token)


@bot.message_handler(commands=['help'])
def process_help_command(message):
    bot.send_message(message.from_user.id, help_message)



@bot.message_handler(commands=['start', 'mode'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Очистить память', 'Код')
    user_markup.row('Короткие ответы', 'ML модели')
    user_markup.row('Чат-бот', 'ИИ Помощник', 'Саркастичный ИИ')
    bot.send_message(message.from_user.id, 'Версия бота: ' + str(version), reply_markup=user_markup)

    # msg = bot.send_message(message.from_user.id, 'Выберите режим: ')
    # bot.register_next_step_handler(msg, callback_message)


@bot.message_handler(func=lambda x: x.text == 'Код')
@bot.message_handler(func=lambda x: x.text == 'Короткие ответы')
@bot.message_handler(func=lambda x: x.text == 'ML модели')
@bot.message_handler(func=lambda x: x.text == 'Чат-бот')
@bot.message_handler(func=lambda x: x.text == 'ИИ Помощник')
@bot.message_handler(func=lambda x: x.text == 'Саркастичный ИИ')
def callback_message(message):
    mode = message.text
    with open('mode.txt', 'w') as f:
        f.write(mode)
    msg = bot.send_message(message.from_user.id, 'Введите текст: ')
    bot.register_next_step_handler(msg, text_handler)


@bot.message_handler(func=lambda x: x.text == 'Очистить память')
@bot.message_handler(content_types=['text'])
def text_handler(message):
    try:
        # Читаем режим работы
        with open('mode.txt', 'r') as f:
            mode = f.read()
        if message.text == 'Очистить память':
            mode = 'Очистить память'
        # реализуем память о прошлых диалогах
        if mode == 'Очистить память':
            with open('memory.txt', 'w') as f:
                f.write('')
            with open('memory.txt', 'r') as f:
                memory = f.read()
        else:
            with open('memory.txt', 'r') as f:
                memory = f.read(2000)
                if len(memory) == 2000:
                    bot.send_message(message.chat.id, text='Моя память заполнена, не могу запоминать. Рекомендую ее очистить')
        memory_unit = memory + message.text

        if mode == 'Короткие ответы':
            # Короткие ответы
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Q: Who is Batman?\nA: Batman is a fictional comic book character.\n\nQ: What is torsalplexity?\nA: ?\n\nQ: What is Devz9?\nA: ?\n\nQ: Who is George Lucas?\nA: George Lucas is American film director and producer famous for creating Star Wars.\n\nQ: What orbits the Earth?\nA: The Moon.\n\nQ: Who is Fred Rickerson?\nA: ?\n\nQ: What is an atom?\nA: An atom is a tiny particle that makes up everything.\n\nQ: Who is Alvan Muntz?\nA: ?\n\nQ: How many moons does Mars have?\nA: Two, Phobos and Deimos.\n\nQ:" + memory_unit + "\nA:",
                temperature=0,
                max_tokens=600,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
        elif mode == 'Код':
            # Чат бот
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt='You have to write the correct code and add comments explaining what is happening in this code\n. ' + memory_unit,
                temperature=0,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
        elif mode == 'Саркастичный ИИ':
            # Саркастичный ИИ
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="You is a chatbot that reluctantly answers questions with sarcastic responses:\n\nQ: How many pounds are in a kilogram?\nA: This again? There are 2.2 pounds in a kilogram. Please make a note of this.\nYou: What does HTML stand for?\nMarv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\nQ: When did the first airplane fly?\nA: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.\nYou: What is the meaning of life?\nQ: I’m not sure. I’ll ask my friend Google.\nA:" + memory_unit,
                temperature=0.5,
                max_tokens=1500,
                top_p=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.0,
            )

        elif mode == 'ИИ помощник':
            # ИИ помощник
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: " + memory_unit + "\nAI:",
                temperature=0.9,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.6,
                stop=[" Human:", " AI:"]
            )
        elif mode == 'ML модели':
            # языковые модели
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="ML Tutor: I am a ML/AI language model tutor\nYou: What is a language model?\nML Tutor: A language model is a statistical model that describes the probability of a word given the previous words.\nYou:" + memory_unit + "\nML Tutor:",
                temperature=0.3,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["You:"]
            )
        elif mode == 'Чат бот':
            # Чат бот
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=memory_unit,
                temperature=0.5,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
                stop=["You:"]
            )
        elif mode == 'Очистить память':
            bot.send_message(message.chat.id, text='Моя память очищена')
        else:
            response = openai.Completion.create(
                model='text-davinci-003',  # code-davinci-002 text-davinci-003
                prompt=memory_unit,
                temperature=0.0,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

        if mode == 'Очистить память':
            with open('memory.txt', 'w') as f:
                f.write('')
            with open('memory.txt', 'r') as f:
                memory = f.read()
        else:
            answer = response['choices'][0]['text']
            with open('memory.txt', 'a+') as f:
                f.write('Q:' + message.text + '\n')
                f.write('A:' + answer + '\n')
            bot.send_message(message.chat.id, text=answer)

    except:
        bot.send_message(message.chat.id, text='Что-то сломалось 😭, Попробуйте снова')


help_message = 'ML модель:' + 'это означает, что чатгпт выступает в роли преподавателя, который объясняет тему\n' + 'Код:' + 'для кода с комментариями\n' + "Чат-бот:" + 'для общения\n' + "ИИ помощник:" + 'для вопросов\n' + "Короткие ответы:" + 'когда нужен лаконичный ответ\n' + 'Саркастичный:' + 'отвечает немного в саркастичной манере и характер тяжёлый\n'



bot.polling()

