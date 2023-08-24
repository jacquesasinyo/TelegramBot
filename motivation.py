

import logging
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

# Set your OpenAI API key
openai.api_key = "OpenAI API key"

# Define the states for the conversation
ANSWERING_QUESTIONS = range(7)

# Define the questions
questions = [
"Quel est votre Nom et Prenom? ",
"Pouvez-vous me parler un peu de vous et de votre parcours éducatif?",
"Quel programme spécifique postulez-vous à l'université ?",
"Qu'est-ce qui vous a inspiré à poursuivre des études dans ce domaine particulier ?",
"Quelles compétences et qualités possédez-vous qui font de vous un candidat solide pour ce programme ?",

]

answers = {}

# Define the command handler for starting the conversation
def start(update: Update, _: CallbackContext) -> int:
    user_id = update.effective_user.id
    if user_id not in answers:
        answers[user_id] = []

    update.message.reply_text("Bonjour ! Bienvenue sur MotivationBot. Envisagez-vous de postuler dans des universités en Turquie et avez-vous besoin d'aide pour rédiger une lettre de motivation pour votre candidature ? Ne cherchez pas plus loin ! MotivationBot est là pour vous aider. Il vous suffit de donner à MotivationBot votre nom et prénom, et de répondre à quelques questions sur vos notes, vos réalisations, la profession que vous souhaitez exercer, les raisons de ce choix, et pourquoi vous voulez étudier en Turquie. Nous utiliserons vos réponses pour générer une lettre de motivation personnalisée rien que pour vous ! N'oubliez pas que c'est votre chance de montrer votre passion et votre engagement pour le domaine d'études que vous avez choisi. Alors, commençons par rédiger une lettre de motivation convaincante qui impressionnera les universités en Turquie. Mais d'abord, veuillez nous fournir votre nom et prénom afin que nous puissions adresser la lettre de motivation spécifiquement à vous.\n" + questions[0])
    return ANSWERING_QUESTIONS

def ask_questions(update: Update, _: CallbackContext) -> int:
    user_id = update.effective_user.id
    question_number = len(answers[user_id])

    if question_number < len(questions):
        update.message.reply_text(questions[question_number])
        return ANSWERING_QUESTIONS
    else:
        return generate_motivational_letter(update)

def receive_answers(update: Update, _: CallbackContext) -> int:
    user_id = update.effective_user.id
    answers[user_id].append(update.message.text)
    return ask_questions(update, _)

def generate_motivational_letter(update: Update) -> int:
    user_id = update.effective_user.id
   

    # Construct the prompt
    prompt = f"Write a motivation Letter in french based on the following informations. Make sure to include my name at the end of the letter:\n\n"
    for i, question in enumerate(questions[1:]):
        prompt += f"Question: {question}\nAnswer: {answers[user_id][i + 1]}\n\n"

    # Use ChatGPT API to generate the rest of the letter
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2936,  # Set the maximum number of tokens in the response
        temperature=0.7  # Adjust the temperature for randomness (higher values make the output more diverse)
    )

    letter = response.choices[0].text

    update.message.reply_text("Thank you for your answers. Here's your motivational letter:\n\n" + letter)

    return ConversationHandler.END

def main():
    # Set up the Telegram bot
    updater = Updater("Telegram bot token")
    dispatcher = updater.dispatcher

    # Define the conversation handler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ANSWERING_QUESTIONS: [
                MessageHandler(Filters.text & ~Filters.command, receive_answers)
            ]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conversation_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
 