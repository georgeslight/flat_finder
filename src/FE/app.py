import logging
import os
import re
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import requests

# Importing from user_db.py
from src.mongo.user_db import User, get_user, save_user

# Load environment variables from .env file
load_dotenv(dotenv_path="../../.env")

BOT_TOKEN = os.getenv('BOT_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Creates a bot instance and passed the BOT_TOKEN to it
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize OpenAI client if necessary
client = openai.OpenAI(api_key=openai.api_key)

user = None


# Function to create a new thread for a user
def create_user(user_id):
    global user
    try:
        user = get_user(user_id)
        if user is None:
            user = User(id=user_id, thread_id=client.beta.threads.create().id)
            save_user(user)
            return user
        return user
    except Exception as e:
        logging.error(f"Failed to create thread: {e}")
        return None


# Message handler that handles incoming '/start' and '/hello'
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome!")
        # Create a new thread for the user
        create_user(message.from_user.id)
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
    global user
    try:
        # profile = get_user(call.message.chat.id)
        address = user.address
        profile_text = (
            f"Here is your profile information:\n\n"
            f"Full Name: {user.full_name if user.full_name else 'Not set'}\n"
            f"Phone Number: {user.phone_number if user.phone_number else 'Not set'}\n"
            f"Email: {user.email if user.email else 'Not set'}\n"
            f"Address:\n"
            f"     Street: {address.street if address.street else 'Not set'}\n"
            f"     House number: {address.house_number if address.house_number else 'Not set'}\n"
            f"     Zip code: {address.zip_code if address.zip_code else 'Not set'}\n"
            f"     City: {address.city if address.city else 'Not set'}\n"
            f"     Country: {address.country if address.country else 'Not set'}\n"
            f"Date of birth: {user.date_of_birth if user.date_of_birth else 'Not set'}\n"
            f"Employment Type: {user.employment_type if user.employment_type else'Not set'}\n"
            f"Average monthly net income: {user.average_monthly_net_income if user.average_monthly_net_income else 'Not set'}\n"
            f"Smoker: {user.smoker if user.smoker else 'Not set'}\n"
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


@bot.callback_query_handler(func=lambda call: call.data == 'preferences')
def preferences_info(call):
    global user
    try:
        # user = get_user(call.from_user.id)
        if not user:
            bot.send_message(call.message.chat.id, "User not found. Please start with /start command.")
            return
        preferences = user.apartment_preferences
        preferences_text = (
            f"Here are your apartment preferences:\n\n"
            f"Max Rent: {preferences.max_rent if preferences.max_rent else 'Not set'}\n"
            f"Location: {preferences.location if preferences.location else 'Not set'}\n"
            f"Bezirk: {', '.join(preferences.bezirk) if preferences.bezirk else 'Not set'}\n"
            f"Min Size: {preferences.min_size if preferences.min_size else 'Not set'}\n"
            f"Ready to Move In: {preferences.ready_to_move_in if preferences.ready_to_move_in else 'Not set'}\n"
            f"Preferred Roommates Sex: {preferences.preferred_roommates_sex if preferences.preferred_roommates_sex else 'Not set'}\n"
            f"Preferred Roommate Age: {', '.join(map(str, preferences.preferred_roommate_age)) if preferences.preferred_roommate_age else 'Not set'}\n"
            f"Preferred Roommate Num: {preferences.preferred_roommate_num if preferences.preferred_roommate_num else 'Not set'}\n"
            f"Smoking OK: {preferences.smoking_ok if preferences.smoking_ok else 'Not set'}\n"
        )
        additional_info = user.additional_info if user.additional_info else []
        additional_info_text = "\n".join(f"- {info}" for info in additional_info) or "Not set"
        preferences_text += f"\nAdditional Information:\n{additional_info_text}"

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Max Rent", callback_data="change_max_rent"),
            InlineKeyboardButton("Location", callback_data="change_location"),
        )
        markup.row(
            InlineKeyboardButton("Bezirk", callback_data="change_bezirk"),
            InlineKeyboardButton("Min Size", callback_data="change_min_size"),
        )
        markup.row(
            InlineKeyboardButton("Ready to Move In", callback_data="change_ready_to_move_in"),
            InlineKeyboardButton("Preferred Roommates Sex", callback_data="change_preferred_roommates_sex"),
        )
        markup.row(
            InlineKeyboardButton("Preferred Roommate Age", callback_data="change_preferred_roommate_age"),
            InlineKeyboardButton("Preferred Roommate Num", callback_data="change_preferred_roommate_num"),
        )
        markup.row(
            InlineKeyboardButton("Smoking OK", callback_data="change_smoking_ok"),
            InlineKeyboardButton("Additional Info", callback_data="change_additional_info")
        )
        bot.send_message(call.message.chat.id, preferences_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to display preferences information: {e}")


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
        elif field == "bezirk":
            msg = bot.send_message(call.message.chat.id, "Please enter your preferred Bezirks separated by commas:")
            bot.register_next_step_handler(msg, lambda message: update_preferences(message, field, call))
        elif field == "preferred_roommate_age":
            msg = bot.send_message(call.message.chat.id,
                                   "Please enter your preferred roommate ages separated by commas:")
            bot.register_next_step_handler(msg, lambda message: update_preferences(message, field, call))
        elif field == "additional_info":
            msg = bot.send_message(call.message.chat.id,
                                   "Please enter additional information, each item separated by commas:")
            bot.register_next_step_handler(msg, lambda message: update_additional_info(message, call))
        else:
            msg = bot.send_message(call.message.chat.id, f"Please enter your new {field}:")
            bot.register_next_step_handler(msg, lambda message: update_preferences(message, field, call))
    except Exception as e:
        logging.error(f"Failed to handle update callback: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('smoker_'))
def update_smoker_status(call):
    try:
        user_id = call.message.chat.id
        smoker_status = call.data.split('_')[1] == 'true'
        get_user(user_id)['profile']['smoker'] = smoker_status
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
            get_user(user_id)['profile']['address'] = {
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
        get_user(user_id)['profile'][field] = new_value
        bot.reply_to(message, f"Your {field} has been updated to: {new_value}")
        profile_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update profile: {e}")


def update_preferences(message, field, call):
    try:
        user_id = message.from_user.id
        new_value = message.text
        if field == "bezirk" or field == "preferred_roommate_age":
            new_value = [x.strip() for x in new_value.split(',')]
        get_user(user_id)['preferences'][field] = new_value
        bot.reply_to(message, f"Your {field} has been updated to: {new_value}")
        preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update preferences: {e}")


def update_additional_info(message, call):
    try:
        user_id = message.from_user.id
        new_value = [x.strip() for x in message.text.split(',')]
        get_user(user_id)['additional_info'] = new_value
        bot.reply_to(message, "Your additional information has been updated.")
        preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update additional information: {e}")


# Handler method for all other text messages
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id

    # Retrieve or create a new thread_id for the user
    thread = get_user(user_id).thread_id
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