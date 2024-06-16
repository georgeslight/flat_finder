import os
from dotenv import load_dotenv
import telebot
import openai
import requests

# Load environment variables from .env file
load_dotenv(dotenv_path="../.env")

BOT_TOKEN = os.getenv('BOT_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Creates a bot instance and passed the BOT_TOKEN to it
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize OpenAI client if necessary
client = openai.OpenAI(api_key=openai.api_key)

# Store thread_id in a simple in-memory storage
user_sessions = {}


# Function to create a new thread for a user
def create_thread(user_id):
    # Create a thread (representing a conversation)
    thread = client.beta.threads.create()
    # Saves thread in user_session
    user_sessions[user_id] = {"thread_id": thread.id}
    return thread.id


# Message handler that handles incoming '/start' and '/hello'
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Test Hello")
    # Create a new thread for the user
    thread_id = create_thread(message.from_user.id)


# Handler method for all other text messages
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id

    # Retrieve or create a new thread_id for the user
    thread = user_sessions.get(user_id)
    if not thread:
        send_welcome(message)
        return
    else:
        thread_id = thread.get("thread_id")

    # Prepare parameters for request
    params = {
        "text": message.text,
        "thread": thread_id,
        "user_name": message.from_user.first_name
    }

    # Send request
    url = 'http://localhost:4000/chat'
    response = requests.post(url, json=params)
    # Reply to the user with the response from AI
    bot.reply_to(message, response.text)


# Start polling for messages
if __name__ == "__main__":
    bot.infinity_polling()
