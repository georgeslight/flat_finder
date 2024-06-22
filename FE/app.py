import os
import time
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import BotCommand
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

# Store thread_id and user profile information in simple in-memory storage
user_sessions = {}


# Function to create a new thread for a user
def create_thread(user_id):
    # Create a thread (representing a conversation)
    thread = client.beta.threads.create()
    # Saves thread in user_session
    user_sessions[user_id] = {
        "thread_id": thread.id,
        "profile": {
            "name": None,
            "surname": None,
            "age": None,
            "gender": None,
            "location": None,
        }
    }
    return thread.id


# Message handler that handles incoming '/start' and '/hello'
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Welcome!")
    # Create a new thread for the user
    thread_id = create_thread(message.from_user.id)


# Handler for '/profile' command
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Profile", callback_data="profile"),
               InlineKeyboardButton("Preferences", callback_data="preferences"))
    bot.send_message(message.chat.id, "Create / Update your profile:", reply_markup=markup)


# Callback query handler for inline buttons
@bot.callback_query_handler(func=lambda call: call.data in ['profile'])
def profile_info(call):
    profile = user_sessions[call.message.chat.id]["profile"]
    profile_text = (
        f"Here is your profile information:\n\n"
        f"Name: {profile.get('name', 'Not set')}\n"
        f"Age: {profile.get('age', 'Not set')}\n"
        f"Gender: {profile.get('gender', 'Not set')}\n"
        f"Location: {profile.get('location', 'Not set')}\n"
    )
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Change Name", callback_data="change_name"),
        InlineKeyboardButton("Change Surname", callback_data="change_surname"),
    )
    markup.row(
        InlineKeyboardButton("Change Age", callback_data="change_age"),
        InlineKeyboardButton("Change Gender", callback_data="change_gender"),
    )
    markup.row(
        InlineKeyboardButton("Change Location", callback_data="change_location")
    )
    bot.send_message(call.message.chat.id, profile_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['change_name'])
def set_name(call):
    profile = user_sessions[call.message.chat.id]["profile"]
    bot.send_message(call.message.chat.id, "Enter your first name")


def preferences_info(message):
    pass


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
