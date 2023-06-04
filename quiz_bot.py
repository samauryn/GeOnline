import yaml
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

def load_questions(file_path):
    with open(file_path, 'r') as file:
        questions = yaml.safe_load(file)
    return questions

def start_quiz(update, context):
    questions = load_questions('quiz_questions.yaml')
    context.user_data['questions'] = questions
    context.user_data['score'] = 0
    context.user_data['current_question'] = 0
    next_question(update, context)

def next_question(update, context):
    questions = context.user_data['questions']
    current_question = context.user_data['current_question']
    if current_question >= len(questions):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Quiz ended. Your score: {context.user_data['score']}")
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

def handle_answer(update, context):
    query = update.callback_query
    selected_option = query.data
    questions = context.user_data['questions']
    current_question = context.user_data['current_question']
    if questions[current_question]['answer'] == selected_option:
        context.user_data['score'] += 1
    context.user_data['current_question'] += 1
    next_question(update, context)
    query.answer()

def main():
    # Provide your Telegram API token here
    api_token = '6038848754:AAG2Ol7wTjRzf3BjatK9CI15ULlFBjYTTOA'
    
    updater = Updater(api_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_quiz))
    dispatcher.add_handler(CallbackQueryHandler(handle_answer))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
