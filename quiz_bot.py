import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

def load_questions(file_path):
    with open(file_path, 'r') as file:
        questions = yaml.safe_load(file)
    return questions

def menu(update, context):
    keyboard = [[InlineKeyboardButton("Start Quiz", callback_data='start_quiz')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Quiz Bot!",
                             reply_markup=reply_markup)
    query = update.callback_query
    
    if query:
        query.message.delete()  # Delete the welcome menu message

    questions = load_questions('quiz_questions.yaml')
    context.user_data['questions'] = questions
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0
    if query:
        query.message.delete()  # Delete the welcome menu message

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




def main():
    # Provide your Telegram API token here
    api_token = '6038848754:AAG2Ol7wTjRzf3BjatK9CI15ULlFBjYTTOA'
    
    updater = Updater(api_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', menu))
    dispatcher.add_handler(CallbackQueryHandler(handle_answer))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
