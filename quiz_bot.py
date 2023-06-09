import yaml
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

# Define conversation states
LOGIN, PASSWORD = range(2)

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
    keyboard = [[InlineKeyboardButton("Куизді бастау", callback_data='start_quiz')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Куизботқа қош келдіңіз! Мұнда сіз біздің викториналар арқылы біліміңізді тексере аласыз.Викторинаны бастау үшін түймені басыңыз",
                             reply_markup=reply_markup)
    query = update.callback_query

    if query:
        query.message.delete()  # Delete the welcome menu message

    questions = load_questions('quiz_questions.yaml')
    context.user_data['questions'] = questions
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0

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
        keyboard = [
            [InlineKeyboardButton(option, callback_data=option)] for option in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=question,
                                 reply_markup=reply_markup)

def end_quiz(update, context):
    questions = context.user_data['questions']
    score = context.user_data['score']
    total_questions = len(questions)

    results = []
    for i in range(total_questions):
        question = questions[i]['question']
        answer = questions[i]['answer']
        result = f"Сұрақ {i + 1}: {question}\nСіздің жаубыңыз: {context.user_data.get(f'answer_{i}', '-')}\nДұрыс жауап: {answer}\n\n"
        results.append(result)

    result_text = ''.join(results)
    score_text = f"Куиз аяқталды. Сіздің нәтижеңіз: {score}/{total_questions}\n\n"
    message_text = score_text + result_text

    context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)


def handle_answer(update, context):
    query = update.callback_query
    selected_option = query.data

    if selected_option == 'start_quiz':
        start_quiz(update, context)
    elif selected_option == 'try_again':
        login_start(update, context)
        return LOGIN  # Go to the LOGIN state to ask for login input
    else:
        questions = context.user_data['questions']
        current_question = context.user_data['current_question']

        if questions[current_question]['answer'] == selected_option:
            context.user_data['score'] += 1

        context.user_data[f'answer_{current_question}'] = selected_option  # Store the user's answer

        context.user_data['current_question'] += 1

        if current_question + 1 < len(questions):
            next_question(update, context)
        else:
            end_quiz(update, context)

    query.answer()


def login_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Логініңізді теріңіз:")
    return LOGIN

def login_input(update, context):
    user = update.message.from_user
    login = update.message.text
    context.user_data['login'] = login
    context.bot.send_message(chat_id=update.effective_chat.id, text="Парольіңізді теріңіз:")
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


def main():
    # Provide your Telegram API token here
    api_token = '6038848754:AAG2Ol7wTjRzf3BjatK9CI15ULlFBjYTTOA'

    updater = Updater(api_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add conversation handler for login
    login_handler = ConversationHandler(
        entry_points=[CommandHandler('start', login_start)],
        states={
            LOGIN: [MessageHandler(Filters.text, login_input)],
            PASSWORD: [MessageHandler(Filters.text, password_input)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(login_handler)
    dispatcher.add_handler(CallbackQueryHandler(handle_answer))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
