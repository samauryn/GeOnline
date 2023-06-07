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
    keyboard = [[InlineKeyboardButton("Start Quiz", callback_data='start_quiz')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Добро пожаловть в КуизБот! Здесь вы можете проверить свои знание, пройдя наши викторины.\nДля того чтобы начать викторину нажмите кнопку",
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
            [InlineKeyboardButton(option, callback_data=option) for option in options]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=question,
                                 reply_markup=reply_markup)

def end_quiz(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Quiz ended. Your score: {context.user_data['score']}")

def handle_answer(update, context):
    query = update.callback_query
    selected_option = query.data

    if selected_option == 'start_quiz':
        start_quiz(update, context)
    else:
        questions = context.user_data['questions']
        current_question = context.user_data['current_question']

        if questions[current_question]['answer'] == selected_option:
            context.user_data['score'] += 1

        context.user_data['current_question'] += 1

        if current_question + 1 < len(questions):
            next_question(update, context)
        else:
            end_quiz(update, context)

    query.answer()

def login_start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your login:")
    return LOGIN

def login_input(update, context):
    user = update.message.from_user
    login = update.message.text
    context.user_data['login'] = login
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your password:")
    return PASSWORD

def password_input(update, context):
    user = update.message.from_user
    password = update.message.text

    authorized_users = load_authorized_users('authorized_users.json')

    if context.user_data['login'] in authorized_users and authorized_users[context.user_data['login']] == password:
        menu(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized access. Please try again.")

    return ConversationHandler.END

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
