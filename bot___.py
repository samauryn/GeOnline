import yaml
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

# Define conversation states
LOGIN, PASSWORD, EXIT = range(3)

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = yaml.safe_load(file)
    return questions

def load_authorized_users(file_path):
    try:
        with open(file_path, 'r') as file:
            authorized_users = json.load(file)
    except FileNotFoundError:
        authorized_users = {}
    return authorized_users

def save_authorized_users(file_path, authorized_users):
    with open(file_path, 'w') as file:
        json.dump(authorized_users, file)

def menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Quiz бастау", callback_data='start_quiz')],
        [InlineKeyboardButton("Жүйеден шығу", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the sticker message and store the message object
    sticker1 = open('menu.webp', 'rb')
    sticker_message = context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=InputFile(sticker1))
    sticker1.close()
    
    # Send the menu message
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Керемет!\nQuiz-ді бастау үшін түймені басыңыз",
                             reply_markup=reply_markup)

    query = update.callback_query
    if query:
        query.message.delete()  # Delete the welcome menu message
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sticker_message.message_id)  # Delete the sticker message
 
    questions = load_questions('quiz_questions.yaml')
    context.user_data['questions'] = questions
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0


def hello_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Login енгізу", callback_data='login')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sticker2 = open('hello.webp', 'rb')
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=InputFile(sticker2))
    sticker2.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Сәлем!\nQuiz-ботқа қош келдіңіз! Мұнда сіз біздің викториналар арқылы біліміңізді тексере аласыз.Quiz-ді бастау үшін ең алдымен логин енгізіңіз.",
                             reply_markup=reply_markup)

    query = update.callback_query
    if query:
        query.message.delete()  # Delete the welcome menu message
        query.sticker.delete()


def start_quiz(update, context):
    query = update.callback_query

    if query:
        query.message.delete()  # Delete the welcome menu message

    next_question(update, context)

def next_question(update, context):
    questions = context.user_data['questions']
    current_question = context.user_data['current_question']

    if current_question >= len(questions):
        end_quiz(update, context)
    else:
        question = questions[current_question]['question']
        options = questions[current_question]['options']
        question_number = current_question + 1  # Нумерация вопросов начинается с 1
        keyboard = [
            [InlineKeyboardButton(option, callback_data=option)] for option in options
        ]
        # Добавляем кнопку "Остановить викторину"
        keyboard.append([InlineKeyboardButton("Quiz-ді тоқтату", callback_data='stop_quiz')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Сұрақ {question_number}: {question}",
                                           reply_markup=reply_markup)
        # Save the message ID to access and delete it later
        context.user_data['question_message_id'] = message.message_id

        
def stop_quiz(update, context):
    query = update.callback_query
    query.message.delete()  # Удаляем сообщение с вопросом

    questions = context.user_data['questions']
    total_questions = len(questions)

    results = []
    for i in range(total_questions):
        user_answer = context.user_data.get(f'answer_{i}')
        if user_answer is not None:
            question = questions[i]['question']
            answer = questions[i]['answer']
            result = f"Сұрақ {i + 1}: {question}\nСіздің жауабыңыз: {user_answer}\nДұрыс жауап: {answer}\n\n"
            results.append(result)
    
    result_text = ''.join(results)
    score = context.user_data['score']
    answered_questions = len(results)
    score_text = f"Қазіргі нәтиже: {score}/{answered_questions}\n\n"
    message_text = score_text + result_text

    sticker3 = open('yeah.webp', 'rb')
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=InputFile(sticker3))
    sticker3.close()
    keyboard = [
    [InlineKeyboardButton("Quiz-ді қайта бастау", callback_data='retry_quiz')],
    [InlineKeyboardButton("Жүйеден шығу", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=reply_markup)

    return EXIT  # Завершаем обработку диалога

def end_quiz(update, context):
    questions = context.user_data['questions']
    score = context.user_data['score']
    total_questions = len(questions)

    results = []
    for i in range(total_questions):
        question = questions[i]['question']
        answer = questions[i]['answer']
        result = f"Сұрақ {i + 1}: {question}\nСіздің жауабыңыз: {context.user_data.get(f'answer_{i}', '-')}\nДұрыс жауап: {answer}\n\n"
        results.append(result)

    result_text = ''.join(results)
    score_text = f"Куиз аяқталды. Сіздің нәтижеңіз: {score}/{total_questions}\n\n"
    message_text = score_text + result_text

    sticker4 = open('yeah.webp', 'rb')
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=InputFile(sticker4))
    sticker4.close()

    keyboard = [
    [InlineKeyboardButton("Quiz-ді қайта бастау", callback_data='retry_quiz')],
    [InlineKeyboardButton("Жүйеден шығу", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=reply_markup)

    query = update.callback_query
    if query:
        query.message.delete()  # Delete the final quiz message

    if 'current_question' in context.user_data:
        del context.user_data['current_question']

    return EXIT  # Go to the EXIT state to end the conversation

def handle_answer(update, context):
    query = update.callback_query
    selected_option = query.data

    if selected_option == 'start_quiz':
        start_quiz(update, context)
    elif selected_option == 'try_again':
        login_start(update, context)
        return LOGIN
    elif selected_option == 'exit':
        exit_system(update, context)
        return ConversationHandler.END
    elif selected_option == 'stop_quiz':
        stop_quiz(update, context)
        return ConversationHandler.END
    else:
        questions = context.user_data['questions']
        current_question = context.user_data['current_question']

        if questions[current_question]['answer'] == selected_option:
            context.user_data['score'] += 1

        context.user_data[f'answer_{current_question}'] = selected_option  # Store the user's answer

        context.user_data['current_question'] += 1

        if current_question + 1 < len(questions):
            # Remove the previous question message
            prev_message_id = context.user_data['question_message_id']
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)

            next_question(update, context)
        else:
            end_quiz(update, context)

    query.answer()

def login_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Логинді теріңіз:")
    return LOGIN

def login_input(update, context):
    user = update.message.from_user
    login = update.message.text
    context.user_data['login'] = login
    context.bot.send_message(chat_id=update.effective_chat.id, text="Парольді теріңіз:")
    return PASSWORD

def password_input(update, context):
    user = update.message.from_user
    password = update.message.text

    authorized_users = load_authorized_users('authorized_users.json')

    if context.user_data['login'] in authorized_users and authorized_users[context.user_data['login']] == password:
        menu(update, context)
        return ConversationHandler.END  # End the conversation handler after successful login
    else:
        # Unauthorized access, prompt user to try again
        keyboard = [[InlineKeyboardButton("Кері көру", callback_data='try_again')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Логин табылмады. Қайталап көріңіз.", reply_markup=reply_markup)

        return LOGIN  # Go back to the LOGIN state to ask for login input again

def exit_system(update, context):
    query = update.callback_query
    query.message.delete()  # Удаляем сообщение с меню
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сіз жүйеден шықтыңыз. Сау болыңыз!\nКері кіру үшін /login командасын теріңіз")
    sticker5 = open('bye.webp', 'rb')
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=InputFile(sticker5))
    sticker5.close()
    return ConversationHandler.END  # Завершаем обработку диалога

def retry_quiz(update, context):
    menu(update, context)
    return ConversationHandler.END

def main():
    # Provide your Telegram API token here
    api_token = '6181724688:AAFcLIAPrcc32PIv-RoA6FCxNA2Lflpghxg'

    updater = Updater(api_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add conversation handler for login
    login_handler = ConversationHandler(
        entry_points=[CommandHandler('start', hello_menu)],
        states={
            LOGIN: [MessageHandler(Filters.text, login_input)],
            PASSWORD: [MessageHandler(Filters.text, password_input)],
            EXIT: [CallbackQueryHandler(end_quiz)]
        },
        fallbacks=[],
    )
    retry_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login_start)],
        states={
            LOGIN: [MessageHandler(Filters.text, login_input)],
            PASSWORD: [MessageHandler(Filters.text, password_input)],
            EXIT: [CallbackQueryHandler(end_quiz)]
        },
        fallbacks=[],
    )
    lg_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(login_start, pattern='^login$')],
        states={
            LOGIN: [MessageHandler(Filters.text, login_input)],
            PASSWORD: [MessageHandler(Filters.text, password_input)],
            EXIT: [CallbackQueryHandler(end_quiz)]
        },
        fallbacks=[],
    )
    qretry_handler = CallbackQueryHandler(retry_quiz, pattern='^retry_quiz$')
    exit_handler = CallbackQueryHandler(exit_system, pattern='^exit$')
    stop_handler = CallbackQueryHandler(stop_quiz, pattern='^stop_quiz$')
    dispatcher.add_handler(qretry_handler)
    dispatcher.add_handler(retry_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(lg_handler)
    dispatcher.add_handler(exit_handler)
    dispatcher.add_handler(login_handler)
    dispatcher.add_handler(CallbackQueryHandler(handle_answer))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
