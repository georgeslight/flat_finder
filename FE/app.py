import logging
import os
import time
import re
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import BotCommand
import openai
import requests
from mongo.user_db import User, save_user


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
    try:
        # Create a thread (representing a conversation)
        thread = client.beta.threads.create()
        # Saves thread in user_session
        # user_sessions[user_id] = {
        #     "thread_id": thread.id
        # }
        user_sessions[user_id] = {
            "thread_id": thread.id,
            "profile": {
                "full_name": None,
                "phone_number": None,
                "email": None,
                "address": {
                    "street": None,
                    "house_number": None,
                    "zip_code": None,
                    "city": None,
                    "country": None

                },
                "date_of_birth": None,
                "employment_type": None,
                "average_monthly_net_income": None,
                "smoker": False
            },
            "preferences": {

            }
        }
        return thread.id
    except Exception as e:
        logging.error(f"Failed to create thread: {e}")
        return None


# Message handler that handles incoming '/start' and '/hello'
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome!")
        # Create a new thread for the user
        thread_id = create_thread(message.from_user.id)
    except Exception as e:
        logging.error(f"Failed to send welcome message: {e}")


# Handler for '/profile' command
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    try:
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Profile", callback_data="profile"),
                   InlineKeyboardButton("Preferences", callback_data="preferences"))
        bot.send_message(message.chat.id, "Create / Update your profile:", reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to handle profile command: {e}")


# Callback query handler for inline buttons
@bot.callback_query_handler(func=lambda call: call.data in ['profile'])
def profile_info(call):
    try:
        profile = user_sessions[call.message.chat.id]["profile"]
        address = profile.get('address', {})
        profile_text = (
            f"Here is your profile information:\n\n"
            f"Full Name: {profile.get('full_name', 'Not set')}\n"
            f"Phone Number: {profile.get('phone_number', 'Not set')}\n"
            f"Email: {profile.get('email', 'Not set')}\n"
            f"Address:\n"
            f"     Street: {address.get('street', 'Not set')}\n"
            f"     House number: {address.get('house_number', 'Not set')}\n"
            f"     Zip code: {address.get('zip_code', 'Not set')}\n"
            f"     City: {address.get('city', 'Not set')}\n"
            f"     Country: {address.get('country', 'Not set')}\n"
            f"Date of birth: {profile.get('date_of_birth', 'Not set')}\n"
            f"Employment Type: {profile.get('employment_type', 'Not set')}\n"
            f"Average monthly net income: {profile.get('average_monthly_net_income', 'Not set')}\n"
            f"Smoker: {profile.get('smoker', 'Not set')}\n"
        )
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Full Name", callback_data="change_full_name"),
            InlineKeyboardButton("Phone Number", callback_data="change_phone_number"),
        )
        markup.row(
            InlineKeyboardButton("Email", callback_data="change_email"),
            InlineKeyboardButton("Address", callback_data="change_address"),
        )
        markup.row(
            InlineKeyboardButton("Date of birth", callback_data="change_date_of_birth"),
            InlineKeyboardButton("Employment Type", callback_data="change_employment_type")
        )
        markup.row(
            InlineKeyboardButton("Average monthly net income", callback_data="change_average_monthly_net_income"),
            InlineKeyboardButton("Smoker", callback_data="change_smoker")
        )
        bot.send_message(call.message.chat.id, profile_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to display profile information: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('change_'))
def handle_update_callback(call):
    try:
        field = '_'.join(call.data.split('_')[1:])
        if field == "address":
            msg = bot.send_message(call.message.chat.id, "Please enter your new address (e.g., Street-Name Number, "
                                                         "Zip City Country):")
            bot.register_next_step_handler(msg, lambda message: update_address(message, call))
        elif field == "smoker":
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("True", callback_data="smoker_true"),
                InlineKeyboardButton("False", callback_data="smoker_false")
            )
            bot.send_message(call.message.chat.id, "Please select your smoking status:", reply_markup=markup)
        else:
            msg = bot.send_message(call.message.chat.id, f"Please enter your new {field}:")
            bot.register_next_step_handler(msg, lambda message: update_profile(message, field, call))
    except Exception as e:
        logging.error(f"Failed to handle update callback: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('smoker_'))
def update_smoker_status(call):
    try:
        user_id = call.message.chat.id
        smoker_status = call.data.split('_')[1] == 'true'
        user_sessions[user_id]['profile']['smoker'] = smoker_status
        bot.reply_to(call.message, f"Your smoking status has been updated to: {'True' if smoker_status else 'False'}")
        profile_info(call)
    except Exception as e:
        logging.error(f"Failed to update smoker status: {e}")


def update_address(message, call):
    try:
        user_id = message.from_user.id
        address = message.text

        # Use regex to parse the address
        match = re.match(r'^(.*?[\s\S]+?)\s+(\d+),\s+(\d+)\s+([\s\S]+)\s+([\s\S]+)$', address)
        if match:
            street, house_number, zip_code, city, country = match.groups()
            logging.info(f"Parsed address: {street}, {house_number}, {zip_code}, {city}, {country}")
            user_sessions[user_id]['profile']['address'] = {
                "street": street,
                "house_number": house_number,
                "zip_code": zip_code,
                "city": city,
                "country": country,
            }
            bot.reply_to(message, "Your address has been updated.")
            profile_info(call)
        else:
            bot.reply_to(message, "Invalid address format. Please try again.")
            profile_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update address: {e}")


def update_profile(message, field, call):
    try:
        user_id = message.from_user.id
        new_value = message.text
        user_sessions[user_id]['profile'][field] = new_value
        bot.reply_to(message, f"Your {field} has been updated to: {new_value}")
        profile_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update profile: {e}")


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
